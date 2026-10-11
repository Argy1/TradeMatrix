"""Train the live models, store them, and record them in `model_versions`.

Run it through `python -m app.ml.train_models` (see that file for why not this module).

For every model it (1) re-runs the honest evaluation on the evaluation period, (2) trains the
live model on all data up to now with the frozen settings, (3) uploads the file to the private
`models` bucket and (4) activates it. A model that does not beat the baselines is stored with
status 'degraded', so the apps show the "below the baseline" warning (docs/08).
"""

import asyncio
import io
import json
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime

import joblib
import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import db
from app.config import get_settings
from app.data import repo
from app.features.build import feature_columns, labelled
from app.ml.backtest import (
    active_symbols,
    load_jobs,
    run_walk_forward,
    summarize,
    summarize_coins,
)
from app.ml.config import EMBARGO, ModelConfig, chosen, eval_from, is_fast
from app.ml.storage import ModelStorage
from app.ml.train import CalibratedModel, fit_calibrated


@dataclass
class ModelBundle:
    """Everything the worker needs to predict, saved together in one file."""

    model: CalibratedModel
    symbol: str  # "ALL" for the pooled 1d model
    timeframe: str
    config: str
    train_start: datetime
    train_end: datetime
    trained_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    # How build_features was called in training; the worker calls it the same way. Empty for
    # the slow models and for files saved before the fast sizes existed.
    feature_options: dict = field(default_factory=dict)

    def importances(self) -> dict[str, float]:
        return self.model.importances()


def to_bytes(bundle: ModelBundle) -> bytes:
    buffer = io.BytesIO()
    joblib.dump(bundle, buffer)
    return buffer.getvalue()


def from_bytes(data: bytes) -> ModelBundle:
    # Only ever load files we wrote ourselves: unpickling runs code from the file.
    return joblib.load(io.BytesIO(data))


def train_final(
    data: pd.DataFrame, config: ModelConfig
) -> tuple[CalibratedModel, datetime, datetime]:
    """Live model: the newest `val` candles stop the trees and calibrate; older ones train."""
    times = pd.DatetimeIndex(sorted(set(data.index)))
    position = times.get_indexer(data.index)
    val = config.windows["val"]
    val_start = len(times) - val
    middle = val_start + val // 2
    train_end = val_start - EMBARGO
    train_start = 0 if config.expanding else max(0, train_end - config.windows["train"])

    def rows(lo: int, hi: int) -> pd.DataFrame:
        # Only rows with a result: on the fast sizes a flat next candle has none.
        return labelled(data[(position >= lo) & (position < hi)])

    model = fit_calibrated(
        rows(train_start, train_end),
        rows(val_start, middle),
        rows(middle, len(times)),
        feature_columns(data),
        config.params,
    )
    return model, times[train_start], times[train_end - 1]


def _clean(value: object) -> object:
    """JSON has no NaN or numpy types."""
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_clean(v) for v in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def evaluation_metrics(summary: dict, config: ModelConfig, timeframe: str) -> dict:
    """The numbers stored on model_versions.metrics and shown on the track-record page."""
    return _clean(
        {
            "config": config.name,
            "evaluation_from": eval_from(timeframe).isoformat(),
            "folds": len(summary["folds"]),
            "model": summary["model"],
            "baselines": summary["baselines"],
            "accuracy_edge_vs_naive": list(summary["accuracy_edge_vs_naive"]),
            "accuracy_edge_vs_best": list(summary["accuracy_edge_vs_best"]),
            "brier_edge_vs_base_rate": list(summary["brier_edge_vs_base_rate"]),
            "beats_baselines": bool(summary["beats_baselines"]),
            "top_features": summary["importances"].head(8).round(3).to_dict(),
        }
    )


async def register(
    session: AsyncSession,
    asset_ids: list[int],
    timeframe: str,
    artifact_path: str,
    metrics: dict,
    train_start: datetime,
    train_end: datetime,
    feature_names: list[str],
) -> list[int]:
    """Make this model the active one for each asset (one active model per asset+timeframe).

    `feature_names` is the model's own feature list, in its order. Each signal then stores only
    the values (predictions.feature_values) and reads their names from here."""
    status = "ok" if metrics["beats_baselines"] else "degraded"
    ids = []
    for asset_id in asset_ids:
        await session.execute(
            text(
                "update model_versions set is_active = false "
                "where asset_id = :a and timeframe = :tf and is_active"
            ),
            {"a": asset_id, "tf": timeframe},
        )
        ids.append(
            (
                await session.execute(
                    text(
                        """
                        insert into model_versions (asset_id, timeframe, train_start, train_end,
                          metrics, artifact_path, is_active, status, feature_names)
                        values (:a, :tf, :start, :end, cast(:metrics as jsonb), :path, true,
                          :status, cast(:names as text[]))
                        returning id
                        """
                    ),
                    {
                        "a": asset_id,
                        "tf": timeframe,
                        "start": train_start,
                        "end": train_end,
                        "metrics": json.dumps(metrics),
                        "path": artifact_path,
                        "status": status,
                        "names": list(feature_names),
                    },
                )
            ).scalar_one()
        )
    return ids


async def run(timeframes: list[str], symbols: list[str] | None = None) -> None:
    """Train for `symbols` (default: every active coin). The pooled 1d model always uses all."""
    settings = get_settings()
    storage = ModelStorage(
        settings.supabase_url, settings.supabase_service_role_key, settings.supabase_models_bucket
    )
    factory = db.session_factory()
    try:
        async with factory() as session:
            assets = {a.symbol: a.id for a in await repo.list_assets(session)}
        for timeframe in timeframes:
            config = chosen(timeframe)
            everyone = await active_symbols()
            pooled = timeframe == "1d" or config.pooled  # a pooled model always uses every coin
            chosen_symbols = everyone if pooled else (symbols or everyone)
            for name, data in await load_jobs(chosen_symbols, timeframe, config):
                preds, folds = await asyncio.to_thread(
                    run_walk_forward, data, timeframe, config, eval_from(timeframe)
                )
                model, start, end = await asyncio.to_thread(train_final, data, config)
                bundle = ModelBundle(
                    model, name, timeframe, config.name, start, end,
                    feature_options=config.feature_options,
                )  # fmt: skip
                path = f"{name}/{timeframe}/{bundle.trained_at:%Y%m%dT%H%M%SZ}.joblib"
                await storage.upload(path, to_bytes(bundle))
                if name == "ALL" and is_fast(timeframe):
                    # One file for all coins, but every coin is judged on its own predictions,
                    # so "ok" or "degraded" is honest coin by coin.
                    scored = summarize_coins(preds, timeframe, assets)
                    groups = [([assets[coin]], summary, coin) for coin, summary in scored.items()]
                else:
                    asset_ids = list(assets.values()) if name == "ALL" else [assets[name]]
                    groups = [(asset_ids, summarize(preds, folds, timeframe), name)]
                for asset_ids, summary, label in groups:
                    metrics = evaluation_metrics(summary, config, timeframe)
                    async with factory() as session, session.begin():
                        ids = await register(
                            session, asset_ids, timeframe, path, metrics, start, end, model.features
                        )
                    print(
                        f"{label:5} {timeframe:3} config={config.name} "
                        f"status={'ok' if metrics['beats_baselines'] else 'degraded'} "
                        f"trained {start:%Y-%m-%d}..{end:%Y-%m-%d} -> {path} (versions {ids})",
                        flush=True,
                    )
    finally:
        await storage.aclose()
        engine = db.get_engine()
        if engine is not None:
            await engine.dispose()
