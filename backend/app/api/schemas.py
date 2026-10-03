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


# ---------- Signals (docs/04) ----------

# Exact text from docs/06. Changing it needs Argy's approval.
DISCLAIMER = (
    "Signals are probabilistic estimates for information and education only, not financial "
    "advice. Crypto is volatile and you can lose all the money you invest. Past performance does "
    "not guarantee future results. TradeMatrix AI does not execute trades."
)


class ReasonOut(BaseModel):
    code: str
    text: str
    effect: str  # up / down / none -> "Pushes up" / "Pushes down" / "No clear push" (docs/08)


class ModelInfo(BaseModel):
    id: int
    trained_at: datetime
    status: str  # "degraded" -> show the below-baseline warning


class RecentAccuracy(BaseModel):
    """Live track record of this coin and timeframe (last 200 resolved predictions)."""

    model: float | None
    naive_baseline: float | None
    n: int
    low_sample: bool


class PredictionOut(BaseModel):
    symbol: str
    timeframe: str
    label: str
    p_up: float
    base_open_time: datetime
    target_open_time: datetime
    target_close_time: datetime
    base_close: str
    reasons: list[ReasonOut]
    sentiment_agg: float
    model: ModelInfo
    recent_accuracy: RecentAccuracy
    disclaimer: str = DISCLAIMER
    stale: bool


class OutcomeOut(BaseModel):
    target_close: str
    actual_direction: str
    correct: bool | None  # null for Neutral (no call)
    return_pct: float


class HistoryItem(BaseModel):
    label: str
    p_up: float
    base_open_time: datetime
    target_open_time: datetime
    base_close: str
    model_status: str
    outcome: OutcomeOut | None  # null until the target candle has closed


class HistoryResponse(BaseModel):
    symbol: str
    timeframe: str
    items: list[HistoryItem]


class SignalChip(BaseModel):
    label: str
    p_up: float
    target_open_time: datetime
    model_status: str
    stale: bool


class MarketRow(BaseModel):
    symbol: str
    name: str
    last_price: str | None  # close of the latest closed 1h candle
    change_24h_pct: float | None
    signals: dict[str, SignalChip | None]  # "1h" / "4h" / "1d"


class LabelStats(BaseModel):
    n: int
    accuracy: float | None


class PerformanceBaseline(BaseModel):
    naive: float | None
    always_up: float | None


class PerformanceOut(BaseModel):
    symbol: str | None
    timeframe: str | None
    days: int
    n_predictions: int
    n_resolved: int
    coverage: float | None
    accuracy: float | None
    baseline: PerformanceBaseline
    brier: float | None
    brier_baseline: float | None
    by_label: dict[str, LabelStats]
    low_sample: bool
