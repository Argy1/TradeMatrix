"""Public signal endpoints: latest signal, history, markets overview and track record."""

from datetime import UTC, date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.errors import ApiError
from app.api.schemas import (
    HistoryItem,
    HistoryResponse,
    MarketRow,
    ModelInfo,
    OutcomeOut,
    PerformanceOut,
    PerformanceSummary,
    PredictionOut,
    ReasonOut,
    RecentAccuracy,
    SignalChip,
    price,
)
from app.api.v1 import Db
from app.data import repo
from app.ml import stats
from app.ml.performance import Resolved, Totals, from_totals, performance
from app.timeframes import (
    TIMEFRAMES,
    Timeframe,
    interval_case_sql,
    last_closed_open_time,
    stale_grace,
)

router = APIRouter(prefix="/v1", tags=["signals"])

# The candle before the base candle, for the naive baseline ("repeat the last move").
_PREVIOUS = f"p.base_open_time - {interval_case_sql('p.timeframe')}"


def prediction_is_stale(target_open_time: datetime, timeframe: str, now: datetime) -> bool:
    """True if the worker should already have predicted a later candle."""
    grace = stale_grace(timeframe)
    expected = last_closed_open_time(now - grace, timeframe) + TIMEFRAMES[timeframe]
    return target_open_time < expected


async def _asset_or_404(session: AsyncSession, symbol: str) -> repo.Asset:
    asset = await repo.get_asset(session, symbol.upper())
    if asset is None:
        raise ApiError(404, "not_found", "Asset not found")
    return asset


async def resolved_rows(
    session: AsyncSession, asset_id: int, timeframe: str, limit: int
) -> list[Resolved]:
    """The newest signals of one coin and size that have a result (for the signal card)."""
    rows = await session.execute(
        text(
            f"""
            select p.p_up, p.label, o.actual_direction, (p.base_close > prev.close) as prev_up
            from predictions p
            join prediction_outcomes o on o.prediction_id = p.id
            left join candles prev on prev.asset_id = p.asset_id
              and prev.timeframe = p.timeframe and prev.open_time = {_PREVIOUS}
            where p.asset_id = :a and p.timeframe = :tf
              and o.actual_direction <> 'flat'  -- a flat candle has no result
            order by p.target_open_time desc
            limit :limit
            """
        ),
        {"a": asset_id, "tf": timeframe, "limit": limit},
    )
    return [Resolved(float(r[0]), r[1], r[2], r[3]) for r in rows]


def first_day(days: int) -> date:
    """The track record counts whole UTC days: today and the `days` days before it."""
    return (datetime.now(UTC) - timedelta(days=days)).date()


def performance_row(
    symbol: str | None, timeframe: str | None, days: int, counts: tuple[int, int, Totals]
) -> PerformanceOut:
    n_signals, n_flat, totals = counts
    return PerformanceOut(
        symbol=symbol,
        timeframe=timeframe,
        days=days,
        n_predictions=n_signals,
        n_flat=n_flat,
        **from_totals(totals),
    )


@router.get("/predictions/latest", response_model=PredictionOut)
async def latest_prediction(session: Db, symbol: str, tf: Timeframe) -> PredictionOut:
    """The current signal for one coin and timeframe, with its reasons and live track record."""
    asset = await _asset_or_404(session, symbol)
    row = (
        await session.execute(
            text(
                """
                select p.label, p.p_up, p.base_open_time, p.target_open_time, p.base_close,
                       p.reasons, p.sentiment_agg, p.sentiment_k, m.id, m.trained_at, m.status
                from predictions p join model_versions m on m.id = p.model_version_id
                where p.asset_id = :a and p.timeframe = :tf
                order by p.target_open_time desc limit 1
                """
            ),
            {"a": asset.id, "tf": tf},
        )
    ).first()
    if row is None:
        raise ApiError(404, "not_found", "No prediction yet for this coin and timeframe")
    label, p_up, base_open, target_open, base_close, reasons, sentiment, k = row[:8]
    mid, trained, status = row[8:]
    recent = performance(await resolved_rows(session, asset.id, tf, 200))
    return PredictionOut(
        symbol=asset.symbol,
        timeframe=tf,
        label=label,
        p_up=round(float(p_up), 4),
        base_open_time=base_open,
        target_open_time=target_open,
        target_close_time=target_open + TIMEFRAMES[tf],
        base_close=price(base_close),
        reasons=[ReasonOut(**reason) for reason in reasons],
        sentiment_agg=round(float(sentiment), 3),
        sentiment_used=float(k) > 0,
        model=ModelInfo(id=mid, trained_at=trained, status=status),
        recent_accuracy=RecentAccuracy(
            model=recent["accuracy"],
            naive_baseline=recent["baseline"]["naive"],
            n=recent["n_resolved"],
            low_sample=recent["low_sample"],
        ),
        stale=prediction_is_stale(target_open, tf, datetime.now(UTC)),
    )


@router.get("/predictions/history", response_model=HistoryResponse)
async def prediction_history(
    session: Db,
    symbol: str,
    tf: Timeframe,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    before: datetime | None = None,
) -> HistoryResponse:
    """Past signals, newest first, with what actually happened."""
    asset = await _asset_or_404(session, symbol)
    if before is not None and before.tzinfo is None:
        before = before.replace(tzinfo=UTC)
    rows = await session.execute(
        text(
            """
            select p.label, p.p_up, p.base_open_time, p.target_open_time, p.base_close, m.status,
                   o.target_close, o.actual_direction, o.correct, o.return_pct
            from predictions p
            join model_versions m on m.id = p.model_version_id
            left join prediction_outcomes o on o.prediction_id = p.id
            where p.asset_id = :a and p.timeframe = :tf
              and (cast(:before as timestamptz) is null or p.target_open_time < :before)
            order by p.target_open_time desc limit :limit
            """
        ),
        {"a": asset.id, "tf": tf, "before": before, "limit": limit},
    )
    items = [
        HistoryItem(
            label=r[0],
            p_up=round(float(r[1]), 4),
            base_open_time=r[2],
            target_open_time=r[3],
            base_close=price(r[4]),
            model_status=r[5],
            outcome=None
            if r[6] is None
            else OutcomeOut(
                target_close=price(r[6]),
                actual_direction=r[7],
                correct=r[8],
                return_pct=round(float(r[9]), 4),
            ),
        )
        for r in rows
    ]
    return HistoryResponse(symbol=asset.symbol, timeframe=tf, items=items)


@router.get("/markets", response_model=list[MarketRow])
async def markets(session: Db) -> list[MarketRow]:
    """Every coin with its last price, 24h change and the latest signal per timeframe."""
    now = datetime.now(UTC)
    prices = await session.execute(
        text(
            """
            select a.id, a.symbol, a.name, last.close, prior.close
            from assets a
            left join lateral (
              select close, open_time from candles
              where asset_id = a.id and timeframe = '1h' order by open_time desc limit 1
            ) last on true
            left join lateral (
              select close from candles where asset_id = a.id and timeframe = '1h'
                and open_time = last.open_time - interval '24 hours'
            ) prior on true
            where a.active order by a.id
            """
        )
    )
    # The newest signal of every coin and size. One small index lookup per pair: a query that
    # sorts the whole table would get slower with every signal the fast sizes add.
    signals = await session.execute(
        text(
            """
            select a.id, tf.timeframe, p.label, p.p_up, p.target_open_time, m.status
            from assets a
            cross join unnest(cast(:timeframes as text[])) as tf(timeframe)
            join lateral (
              select label, p_up, target_open_time, model_version_id from predictions
              where asset_id = a.id and timeframe = tf.timeframe
              order by target_open_time desc limit 1
            ) p on true
            join model_versions m on m.id = p.model_version_id
            where a.active
            """
        ),
        {"timeframes": list(TIMEFRAMES)},
    )
    chips: dict[tuple[int, str], SignalChip] = {
        (asset_id, tf): SignalChip(
            label=label,
            p_up=round(float(p_up), 4),
            target_open_time=target,
            model_status=status,
            stale=prediction_is_stale(target, tf, now),
        )
        for asset_id, tf, label, p_up, target, status in signals
    }
    return [
        MarketRow(
            symbol=symbol,
            name=name,
            last_price=price(last) if last is not None else None,
            change_24h_pct=round(float((last / prior - 1) * 100), 2) if last and prior else None,
            signals={tf: chips.get((asset_id, tf)) for tf in TIMEFRAMES},
        )
        for asset_id, symbol, name, last, prior in prices
    ]


@router.get("/performance", response_model=PerformanceOut)
async def track_record(
    session: Db,
    symbol: str | None = None,
    tf: Timeframe | None = None,
    days: Annotated[int, Query(ge=1, le=365)] = 30,
) -> PerformanceOut:
    """Live track record: model accuracy next to the baselines, always (docs/06).

    Read from the daily counts (signal_stats_daily), which the worker refreshes every hour.
    """
    asset_id = (await _asset_or_404(session, symbol)).id if symbol else None
    counts = await stats.totals(session, asset_id, tf, first_day(days))
    return performance_row(symbol.upper() if symbol else None, tf, days, counts)


@router.get("/performance/summary", response_model=PerformanceSummary)
async def track_record_summary(
    session: Db,
    days: Annotated[int, Query(ge=1, le=365)] = 30,
    tf: Timeframe | None = None,
) -> PerformanceSummary:
    """Live track record for every active coin and candle size, plus the overall numbers.

    With `tf`, only that size (rows and overall). The fast sizes make far more signals than
    the slow ones, so an overall number across all sizes is mostly a one-minute number.
    """
    by_pair = await stats.totals_by_pair(session, tf, first_day(days))
    nothing = (0, 0, Totals())
    overall = nothing
    for n_signals, n_flat, totals in by_pair.values():
        overall = (overall[0] + n_signals, overall[1] + n_flat, overall[2] + totals)
    assets = await repo.list_assets(session)
    return PerformanceSummary(
        days=days,
        timeframe=tf,
        overall=performance_row(None, tf, days, overall),
        rows=[
            performance_row(a.symbol, size, days, by_pair.get((a.id, size), nothing))
            for a in assets
            for size in ([tf] if tf else TIMEFRAMES)
        ],
    )
