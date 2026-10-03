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
from app.features.build import feature_columns
from app.ml.backtest import active_symbols, load_jobs, run_walk_forward, summarize
from app.ml.config import EMBARGO, EVAL_FROM, ModelConfig, chosen
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
        return data[(position >= lo) & (position < hi)]

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


def evaluation_metrics(summary: dict, config: ModelConfig) -> dict:
    """The numbers stored on model_versions.metrics and shown on the track-record page."""
    return _clean(
        {
            "config": config.name,
            "evaluation_from": EVAL_FROM.isoformat(),
            "folds": len(summary["folds"]),
            "model": summary["model"],
            "baselines": summary["baselines"],
            "accuracy_edge_vs_naive": list(summary["accuracy_edge_vs_naive"]),
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
) -> list[int]:
    """Make this model the active one for each asset (one active model per asset+timeframe)."""
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
                          metrics, artifact_path, is_active, status)
                        values (:a, :tf, :start, :end, cast(:metrics as jsonb), :path, true,
                          :status)
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
            chosen_symbols = everyone if timeframe == "1d" else (symbols or everyone)
            for name, data in await load_jobs(chosen_symbols, timeframe):
                preds, folds = await asyncio.to_thread(
                    run_walk_forward, data, timeframe, config, EVAL_FROM
                )
                metrics = evaluation_metrics(summarize(preds, folds, timeframe), config)
                model, start, end = await asyncio.to_thread(train_final, data, config)
                bundle = ModelBundle(model, name, timeframe, config.name, start, end)
                path = f"{name}/{timeframe}/{bundle.trained_at:%Y%m%dT%H%M%SZ}.joblib"
                await storage.upload(path, to_bytes(bundle))
                asset_ids = list(assets.values()) if name == "ALL" else [assets[name]]
                async with factory() as session, session.begin():
                    ids = await register(session, asset_ids, timeframe, path, metrics, start, end)
                print(
                    f"{name:4} {timeframe:3} config={config.name} "
                    f"status={'ok' if metrics['beats_baselines'] else 'degraded'} "
                    f"trained {start:%Y-%m-%d}..{end:%Y-%m-%d} -> {path} (model_versions {ids})"
                )
    finally:
        await storage.aclose()
        engine = db.get_engine()
        if engine is not None:
            await engine.dispose()
