"""Live predictions (run_predictions) and their outcomes (resolve_outcomes)."""

import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

import numpy as np
import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.data import repo
from app.data.exchanges.base import Candle
from app.features.build import CONTEXT_COLUMNS, build_features
from app.ml.config import NEUTRAL_HIGH, NEUTRAL_LOW
from app.ml.reasons import build_reasons
from app.ml.registry import ModelBundle, from_bytes
from app.ml.storage import ModelStorage
from app.timeframes import TIMEFRAMES, last_closed_open_time

# Candles loaded for live features. Training computed indicators over the full history; with
# 1000 candles the EMAs have converged to the same values (difference < 0.001%).
HISTORY = 1000


@dataclass(frozen=True)
class ActiveModel:
    id: int
    asset_id: int
    symbol: str
    timeframe: str
    artifact_path: str
    status: str
    # Feature names saved once on the model version; None for models stored before that existed.
    feature_names: list[str] | None = None


async def active_models(session: AsyncSession, timeframes: list[str]) -> list[ActiveModel]:
    rows = await session.execute(
        text(
            """
            select m.id, m.asset_id, a.symbol, m.timeframe, m.artifact_path, m.status,
                   m.feature_names
            from model_versions m join assets a on a.id = m.asset_id
            where m.is_active and a.active and m.timeframe = any(:timeframes)
            order by m.timeframe, a.id
            """
        ),
        {"timeframes": timeframes},
    )
    return [ActiveModel(*row) for row in rows]


class ModelCache:
    """Model files are downloaded once per process, then reused every hour."""

    def __init__(self, storage: ModelStorage) -> None:
        self._storage = storage
        self._bundles: dict[str, ModelBundle] = {}

    async def get(self, path: str) -> ModelBundle:
        if path not in self._bundles:
            self._bundles[path] = from_bytes(await self._storage.download(path))
        return self._bundles[path]


def candle_frame(candles: list[Candle]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "open": [float(c.open) for c in candles],
            "high": [float(c.high) for c in candles],
            "low": [float(c.low) for c in candles],
            "close": [float(c.close) for c in candles],
            "volume": [float(c.volume) for c in candles],
        },
        index=pd.DatetimeIndex([c.open_time for c in candles]),
    )


def label_for(p_up: float) -> str:
    return "up" if p_up > NEUTRAL_HIGH else "down" if p_up < NEUTRAL_LOW else "neutral"


def snapshot_columns(
    snapshot: dict[str, float | None], stored_names: list[str] | None
) -> tuple[str | None, list[float | None] | None]:
    """How the audit snapshot is stored: (`features` JSON, `feature_values` array), one is None.

    The compact form keeps only the values; their names are stored once on the model version.
    A list of numbers under the wrong names would be a wrong audit trail that raises no error,
    so the compact form is used only when the stored names match this snapshot name by name,
    in the same order. Anything else falls back to the JSON, which carries its own names.
    """
    if stored_names is not None and list(snapshot) == list(stored_names):
        return None, list(snapshot.values())
    return json.dumps(snapshot), None


def make_prediction(
    bundle: ModelBundle,
    candles: pd.DataFrame,
    btc: pd.DataFrame | None,
    asset_id: int,
    *,
    sentiment: float = 0.0,
    blend_k: float = 0.0,
) -> dict | None:
    """Prediction for the candle after the last row of `candles`, or None if history is short."""
    features = build_features(candles, btc)
    if bundle.symbol == "ALL":
        features["asset_id"] = float(asset_id)
    # Same columns as in training. In the pooled 1d model, BTC's own rows had no BTC-context
    # columns, so they stay empty (NaN) here too, exactly as the model learned them.
    row = features.iloc[[-1]].reindex(columns=bundle.model.features)
    by_design = set(CONTEXT_COLUMNS) if btc is None else set()
    if row.drop(columns=[c for c in row.columns if c in by_design]).isna().any(axis=None):
        return None  # not enough history yet
    p_ml = float(bundle.model.predict(row)[0])
    # Sentiment is stored but only blended in when k > 0 (shadow mode first, docs/03).
    p_up = float(np.clip(p_ml + blend_k * sentiment, 0.01, 0.99))
    snapshot = {  # JSON has no NaN: empty-by-design values are stored as null
        name: None if pd.isna(value) else float(value) for name, value in row.iloc[0].items()
    }
    return {
        "p_ml": p_ml,
        "p_up": p_up,
        "label": label_for(p_up),
        "features": snapshot,
        "reasons": build_reasons(snapshot, bundle.importances(), sentiment or None),
    }


async def run_predictions(
    session: AsyncSession,
    cache: ModelCache,
    timeframes: list[str],
    now: datetime,
    *,
    blend_k: float = 0.0,
) -> dict:
    """One prediction per active model for the candle that opens now. Idempotent: the unique
    key (asset, timeframe, target candle) means a second run inserts nothing."""
    created = skipped = 0
    errors: list[str] = []
    btc_id = next(a.id for a in await repo.list_assets(session) if a.symbol == "BTC")
    for model in await active_models(session, timeframes):
        expected = last_closed_open_time(now, model.timeframe)
        candles = await repo.fetch_candles(session, model.asset_id, model.timeframe, HISTORY)
        if not candles or candles[-1].open_time != expected:
            skipped += 1  # the newest candle is missing: never predict from stale data
            continue
        try:
            btc = None
            if model.asset_id != btc_id:
                btc = candle_frame(
                    await repo.fetch_candles(session, btc_id, model.timeframe, HISTORY)
                )
            bundle = await cache.get(model.artifact_path)
            result = make_prediction(
                bundle, candle_frame(candles), btc, model.asset_id, sentiment=0.0, blend_k=blend_k
            )
        except Exception as exc:  # one broken model must not block the others
            errors.append(f"{model.symbol} {model.timeframe}: {type(exc).__name__}: {exc}")
            continue
        if result is None:
            skipped += 1
            continue
        features_json, feature_values = snapshot_columns(result["features"], model.feature_names)
        inserted = await session.execute(
            text(
                """
                insert into predictions (asset_id, timeframe, base_open_time, target_open_time,
                  base_close, p_ml, p_up, label, sentiment_agg, sentiment_k, model_version_id,
                  features, feature_values, reasons)
                values (:asset_id, :tf, :base, :target, :base_close, :p_ml, :p_up, :label,
                  0, :k, :model_id, cast(:features as jsonb), cast(:feature_values as real[]),
                  cast(:reasons as jsonb))
                on conflict (asset_id, timeframe, target_open_time) do nothing
                returning id
                """
            ),
            {
                "asset_id": model.asset_id,
                "tf": model.timeframe,
                "base": expected,
                "target": expected + TIMEFRAMES[model.timeframe],
                "base_close": Decimal(candles[-1].close),
                "p_ml": result["p_ml"],
                "p_up": result["p_up"],
                "label": result["label"],
                "k": blend_k,
                "model_id": model.id,
                "features": features_json,
                "feature_values": feature_values,
                "reasons": json.dumps(result["reasons"]),
            },
        )
        created += inserted.first() is not None
    return {"created": created, "skipped": skipped, "errors": errors}


async def resolve_outcomes(session: AsyncSession) -> dict:
    """Fill in what actually happened for every prediction whose target candle has closed.

    Flat counts as down, matching the training label; Neutral calls get correct = null.
    """
    rows = await session.execute(
        text(
            """
            insert into prediction_outcomes
              (prediction_id, target_close, actual_direction, correct, return_pct)
            select p.id, c.close, d.direction,
                   case when p.label = 'neutral' then null else p.label = d.direction end,
                   (c.close / p.base_close - 1) * 100
            from predictions p
            join candles c on c.asset_id = p.asset_id and c.timeframe = p.timeframe
                          and c.open_time = p.target_open_time
            cross join lateral (
              select case when c.close > p.base_close then 'up' else 'down' end as direction
            ) d
            where not exists (select 1 from prediction_outcomes o where o.prediction_id = p.id)
            on conflict (prediction_id) do nothing
            returning prediction_id
            """
        )
    )
    return {"resolved": len(rows.all())}
