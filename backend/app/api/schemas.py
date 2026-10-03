"""Response models. FastAPI turns these into the OpenAPI contract the web and mobile apps use."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


def price(value: Decimal) -> str:
    """Prices travel as strings so no client rounds them through a float (docs/04)."""
    return format(value.normalize(), "f")


class AssetOut(BaseModel):
    symbol: str
    name: str
    exchange_symbol: str


class CandleOut(BaseModel):
    t: datetime  # open time, UTC
    o: str
    h: str
    l: str  # noqa: E741 - short names match the WebSocket candle message in docs/04
    c: str
    v: str
    ema9: float | None
    ema21: float | None
    ema50: float | None
    bb_upper: float | None
    bb_mid: float | None
    bb_lower: float | None
    rsi14: float | None
    macd: float | None
    macd_signal: float | None
    macd_hist: float | None


class CandlesResponse(BaseModel):
    symbol: str
    timeframe: str
    candles: list[CandleOut]
    stale: bool


class JobStatus(BaseModel):
    job_name: str
    last_run_at: datetime | None
    last_success_at: datetime | None
    last_error: str | None


class CandleFreshness(BaseModel):
    timeframe: str
    latest_open_time: datetime | None
    stale: bool


class ModelStatus(BaseModel):
    symbol: str
    timeframe: str
    model_version_id: int
    trained_at: datetime
    # "degraded": did not beat the baselines in the evaluation, so the apps show a warning.
    status: str


class StatusResponse(BaseModel):
    jobs: list[JobStatus]
    candles: list[CandleFreshness]
    models: list[ModelStatus]
    stale: bool
