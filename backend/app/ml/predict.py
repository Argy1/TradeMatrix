"""Live predictions (run_predictions) and their outcomes (resolve_outcomes)."""

import asyncio
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
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
from app.sentiment.aggregate import sentiment_by_asset
from app.timeframes import FAST_TIMEFRAMES, TIMEFRAMES, last_closed_open_time

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


class FrameCache:
    """The newest candles of every coin and size, kept in memory between two runs.

    The every-minute run needs the last 1,000 candles of 16 coins to build its features. A
    closed candle never changes, so after the first run only the candles that are new since
    then are read: one row per coin instead of a thousand. If anything does not line up (a
    gap, a coin that was not held), that size is read in full again: a slower run, never a
    wrong one.
    """

    def __init__(self) -> None:
        self._held: dict[str, dict[int, repo.FeatureFrame]] = {}

    async def get(
        self, session: AsyncSession, asset_ids: list[int], timeframe: str, limit: int
    ) -> dict[int, repo.FeatureFrame]:
        held = self._held.get(timeframe)
        frames = None
        if held is not None and set(asset_ids) <= set(held):
            since = min(held[asset_id].frame.index[-1] for asset_id in asset_ids)
            newer = await repo.feature_frames(session, asset_ids, timeframe, limit, after=since)
            frames = self._extended(held, newer, asset_ids, timeframe, limit)
        if frames is None:
            frames = await repo.feature_frames(session, asset_ids, timeframe, limit)
        self._held[timeframe] = frames
        return frames

    @staticmethod
    def _extended(
        held: dict[int, repo.FeatureFrame],
        newer: dict[int, repo.FeatureFrame],
        asset_ids: list[int],
        timeframe: str,
        limit: int,
    ) -> dict[int, repo.FeatureFrame] | None:
        """The held frames with the new candles added, or None if a candle is missing between."""
        step = TIMEFRAMES[timeframe]
        out = {}
        for asset_id in asset_ids:
            old = held[asset_id]
            new = newer.get(asset_id)
            rows = None if new is None else new.frame[new.frame.index > old.frame.index[-1]]
            if rows is None or rows.empty:
                out[asset_id] = old
                continue
            joined = old.frame.index[-1:].append(rows.index)
            if not ((joined[1:] - joined[:-1]) == step).all():
                return None
            out[asset_id] = repo.FeatureFrame(
                pd.concat([old.frame, rows]).iloc[-limit:], new.last_close
            )
        return out


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
    # A fast model was trained with extra switches (order flow, quiet stretches); files
    # saved before those existed have none, which means "the plain features".
    features = build_features(candles, btc, **(getattr(bundle, "feature_options", None) or {}))
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
    # In shadow mode sentiment did not move the probability, so it must not be shown as one
    # of the reasons for the signal either. It only becomes a reason once it is blended in.
    shown_sentiment = sentiment if blend_k > 0 and sentiment else None
    return {
        "p_ml": p_ml,
        "p_up": p_up,
        "label": label_for(p_up),
        "features": snapshot,
        "reasons": build_reasons(snapshot, bundle.importances(), shown_sentiment),
    }


async def warm_up(
    session: AsyncSession, cache: ModelCache, frames: FrameCache, timeframes: list[str]
) -> dict:
    """Load the model files and the newest candles of these sizes before the first run needs
    them. Downloading a file or reading 1,000 candles per coin takes seconds; a one-minute
    signal should not wait for that."""
    models = await active_models(session, timeframes)
    errors = []
    for path in dict.fromkeys(m.artifact_path for m in models):
        try:
            await cache.get(path)
        except Exception as exc:
            errors.append(f"{path}: {type(exc).__name__}: {exc}")
    assets = await repo.list_assets(session)
    btc_id = next(a.id for a in assets if a.symbol == "BTC")
    for timeframe in dict.fromkeys(m.timeframe for m in models):
        wanted = sorted({m.asset_id for m in models if m.timeframe == timeframe} | {btc_id})
        await frames.get(session, wanted, timeframe, HISTORY)
    return {"models": len(models), "errors": errors}


# Every signal of one run is stored by one statement: the rows travel as one JSON document and
# Postgres unpacks them (jsonb_to_recordset). "do nothing" on the unique key keeps a second
# run from creating duplicates, and "returning" tells how many rows were really new.
_INSERT_SIGNALS = text(
    """
    insert into predictions (asset_id, timeframe, base_open_time, target_open_time,
      base_close, p_ml, p_up, label, sentiment_agg, sentiment_k, model_version_id,
      features, feature_values, reasons)
    select r.asset_id, r.timeframe, r.base_open_time, r.target_open_time, r.base_close,
           r.p_ml, r.p_up, r.label, r.sentiment_agg, r.sentiment_k, r.model_version_id,
           r.features, r.feature_values, r.reasons
    from jsonb_to_recordset(cast(:rows as jsonb)) as r(
      asset_id smallint, timeframe text, base_open_time timestamptz,
      target_open_time timestamptz, base_close numeric, p_ml real, p_up real, label text,
      sentiment_agg real, sentiment_k real, model_version_id integer, features jsonb,
      feature_values real[], reasons jsonb)
    on conflict (asset_id, timeframe, target_open_time) do nothing
    returning id
    """
)
PREDICT_PARALLEL = 4  # feature building and model calls running side by side


async def run_predictions(
    session: AsyncSession,
    cache: ModelCache,
    timeframes: list[str],
    now: datetime,
    *,
    blend_k: float = 0.0,
    frames: FrameCache | None = None,
) -> dict:
    """One prediction per active model for the candle that opens now. Idempotent: the unique
    key (asset, timeframe, target candle) means a second run inserts nothing.

    `frames` (the every-minute run passes one) keeps the candles between runs, so only the
    new ones are read."""
    skipped = 0
    errors: list[str] = []
    assets = await repo.list_assets(session)
    btc_id = next(a.id for a in assets if a.symbol == "BTC")
    symbols = [a.symbol for a in assets]
    models = await active_models(session, timeframes)
    # Load each model file once, before the coins are worked on side by side (a pooled model
    # is one file for 16 coins). A file that cannot be loaded fails only its own coins.
    broken: dict[str, Exception] = {}
    for path in dict.fromkeys(m.artifact_path for m in models):
        try:
            await cache.get(path)
        except Exception as exc:
            broken[path] = exc

    # The candles of every coin of one size arrive in one query (Bitcoin included: it is the
    # market context of the others), instead of two queries per coin.
    loaded: dict[str, dict[int, repo.FeatureFrame]] = {}
    for timeframe in dict.fromkeys(m.timeframe for m in models):
        wanted = sorted({m.asset_id for m in models if m.timeframe == timeframe} | {btc_id})
        if frames is not None:
            loaded[timeframe] = await frames.get(session, wanted, timeframe, HISTORY)
        else:
            loaded[timeframe] = await repo.feature_frames(session, wanted, timeframe, HISTORY)

    # News sentiment per coin, as of the moment the predicted candle opens (one lookup per
    # target time: candles of different sizes that open together share it).
    sentiments: dict[datetime, dict[str, float]] = {}
    gate = asyncio.Semaphore(PREDICT_PARALLEL)

    async def predict(model: ActiveModel) -> dict | None:
        """The row to store for one model, or None when there is nothing to predict from."""
        if model.artifact_path in broken:
            raise broken[model.artifact_path]
        expected = last_closed_open_time(now, model.timeframe)
        own = loaded[model.timeframe].get(model.asset_id)
        if own is None or own.frame.index[-1] != expected:
            return None  # the newest candle is missing: never predict from stale data
        target = expected + TIMEFRAMES[model.timeframe]
        sentiment = sentiments[target].get(model.symbol, 0.0)
        btc = None
        if model.asset_id != btc_id:
            btc_frame = loaded[model.timeframe].get(btc_id)
            btc = None if btc_frame is None else btc_frame.frame
        bundle = await cache.get(model.artifact_path)
        async with gate:
            # pandas and XGBoost are CPU work: in threads, so the event loop stays free and
            # several coins are worked on at the same time.
            result = await asyncio.to_thread(
                make_prediction,
                bundle,
                own.frame,
                btc,
                model.asset_id,
                sentiment=sentiment,
                blend_k=blend_k,
            )
        if result is None:
            return None
        features_json, feature_values = snapshot_columns(result["features"], model.feature_names)
        return {
            "asset_id": model.asset_id,
            "timeframe": model.timeframe,
            "base_open_time": expected.isoformat(),
            "target_open_time": target.isoformat(),
            "base_close": format(Decimal(own.last_close), "f"),  # exact, never a float
            "p_ml": result["p_ml"],
            "p_up": result["p_up"],
            "label": result["label"],
            "sentiment_agg": sentiment,
            "sentiment_k": blend_k,
            "model_version_id": model.id,
            "features": None if features_json is None else json.loads(features_json),
            "feature_values": feature_values,
            "reasons": result["reasons"],
        }

    for target in {
        last_closed_open_time(now, m.timeframe) + TIMEFRAMES[m.timeframe] for m in models
    }:
        sentiments[target] = await sentiment_by_asset(session, symbols, target)
    answers = await asyncio.gather(*(predict(m) for m in models), return_exceptions=True)

    rows = []
    for model, answer in zip(models, answers, strict=True):
        if isinstance(answer, BaseException):  # one broken model must not block the others
            errors.append(f"{model.symbol} {model.timeframe}: {type(answer).__name__}: {answer}")
        elif answer is None:
            skipped += 1
        else:
            rows.append(answer)
    created = 0
    if rows:
        inserted = await session.execute(_INSERT_SIGNALS, {"rows": json.dumps(rows)})
        created = len(inserted.all())
    return {"created": created, "skipped": skipped, "errors": errors}


async def resolve_outcomes(
    session: AsyncSession,
    timeframes: list[str] | None = None,
    *,
    now: datetime | None = None,
    look_back: timedelta = timedelta(days=7),
) -> dict:
    """Fill in what actually happened for every prediction whose target candle has closed.

    A flat candle (same close as the one before) follows the training label of its size:
    on the slow sizes it counts as down; on the fast sizes it is 'flat', which has no result
    (correct = null), like a Neutral call. See build_labels.

    The query walks coin by coin and size by size through the newest predictions only
    (`look_back`), so it stays quick however large the table grows.
    """
    now = now or datetime.now(UTC)
    rows = await session.execute(
        text(
            """
            insert into prediction_outcomes
              (prediction_id, target_close, actual_direction, correct, return_pct)
            select p.id, c.close, d.direction,
                   case when p.label = 'neutral' or d.direction = 'flat' then null
                        else p.label = d.direction end,
                   (c.close / p.base_close - 1) * 100
            from assets a
            cross join unnest(cast(:timeframes as text[])) as tf(timeframe)
            join predictions p on p.asset_id = a.id and p.timeframe = tf.timeframe
                              and p.target_open_time >= :since
            join candles c on c.asset_id = p.asset_id and c.timeframe = p.timeframe
                          and c.open_time = p.target_open_time
            cross join lateral (
              select case when c.close > p.base_close then 'up'
                          when c.close = p.base_close
                               and p.timeframe = any(cast(:fast as text[])) then 'flat'
                          else 'down' end as direction
            ) d
            where not exists (select 1 from prediction_outcomes o where o.prediction_id = p.id)
            on conflict (prediction_id) do nothing
            returning prediction_id
            """
        ),
        {
            "timeframes": timeframes or list(TIMEFRAMES),
            "fast": list(FAST_TIMEFRAMES),
            "since": now - look_back,
        },
    )
    return {"resolved": len(rows.all())}
