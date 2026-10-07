# 04 — Database and API contract

*Created by Argy*

The SQL is in `supabase/migrations/20261003000000_init.sql` (ready to apply with `supabase db push`). Do not edit an applied migration; add a new file for changes.

## Tables

| Table | Purpose | Written by |
| --- | --- | --- |
| `assets` | Supported coins (`symbol` = `BTC`, `exchange_symbol` = `BTCUSDT`) | seed / admin |
| `candles` | OHLCV for closed candles, PK `(asset_id, timeframe, open_time)` | worker |
| `news_items` | Headlines, deduped by URL and title hash, tagged with asset symbols | worker |
| `sentiments` | Gemini result per headline (score, confidence, event type, reason, model, prompt version) | worker |
| `model_versions` | Trained models, metrics JSON, Storage path, `is_active` (one per asset + timeframe), `status` | worker |
| `predictions` | One row per asset + timeframe + target candle: `p_ml`, final `p_up`, label, sentiment, feature snapshot (`feature_values`, named by `model_versions.feature_names`; the view `prediction_features` shows it as JSON), reasons, model version | worker |
| `prediction_outcomes` | Filled when the target candle closes: actual direction, `correct`, return | worker |
| `watchlists`, `alerts`, `device_tokens` | Per-user settings | api (as the user) |
| `notifications` | In-app notifications | worker |
| `worker_heartbeat` | Last run / last success / last error per job | worker |

Prediction semantics (important):

- `base_open_time` = open time of the last **closed** candle used; `base_close` = its close.
- `target_open_time` = `base_open_time + timeframe`. The prediction says whether the close of that candle will be above `base_close`.
- Outcome: `actual_direction = 'up'` if `target_close > base_close`, else `'down'` (a flat close counts as down, matching the training label). `correct` is `null` when the label was `neutral`.
- `sentiment_k = 0` means the row was produced in shadow mode (sentiment stored but not blended).

## Security model

- Public read: market data, predictions, outcomes, news. Writes only by the backend.
- User tables: Row Level Security with `auth.uid() = user_id`. In addition, the API **always** filters by the `user_id` from the verified JWT (the backend's DB role bypasses RLS, so the API must enforce it itself).
- `model_versions` and `worker_heartbeat` are backend-only.

## REST API (`/v1`)

Conventions:

- JSON, snake_case, UTC ISO-8601 timestamps with `Z`. Prices as strings (`"67123.45"`) where precision matters.
- `symbol` is the asset symbol (`BTC`, `ETH`, `SOL`, `BNB`, `XRP`). `tf` is `1h`, `4h` or `1d`.
- Errors: HTTP status + `{"error": {"code": "not_found", "message": "Asset not found"}}`.
- Public endpoints: rate limit about 60 requests/min/IP (use `slowapi` or similar). Protected endpoints need `Authorization: Bearer <Supabase access token>`.
- Pagination: `limit` (default 50, max 500) and `before` (ISO timestamp or id).
- Every response that depends on fresh data may include `"stale": true` when the worker has missed its last expected run.

### Public

| Method and path | Purpose |
| --- | --- |
| `GET /health` | Liveness + DB check (for Railway) |
| `GET /v1/status` | Last success per job, active model versions, degraded flags |
| `GET /v1/assets` | Supported coins |
| `GET /v1/markets` | For each asset: last price, 24h change %, latest signal per timeframe |
| `GET /v1/candles?symbol=BTC&tf=1h&limit=500&before=` | Closed candles + indicator series computed on the server (`ema9`, `ema21`, `ema50`, `bb_upper`, `bb_mid`, `bb_lower`, `rsi14`, `macd`, `macd_signal`, `macd_hist`). Fetch extra warm-up candles internally so the first returned candle has valid indicators |
| `GET /v1/predictions/latest?symbol=BTC&tf=1h` | Current signal (example below) |
| `GET /v1/predictions/history?symbol=BTC&tf=1h&limit=50&before=` | Past signals with outcomes |
| `GET /v1/performance?symbol=BTC&tf=1h&days=30` | Track record (example below). `symbol` optional (all coins), `tf` optional |
| `GET /v1/news?symbol=BTC&limit=30` | Headlines with sentiment (score, confidence, event type, reason) |

### Protected (login)

| Method and path | Purpose |
| --- | --- |
| `GET /v1/watchlist` / `PUT /v1/watchlist/{symbol}` / `DELETE /v1/watchlist/{symbol}` | Manage watchlist |
| `GET /v1/alerts`, `POST /v1/alerts`, `PATCH /v1/alerts/{id}`, `DELETE /v1/alerts/{id}` | Manage alerts |
| `POST /v1/devices` (body: `fcm_token`, `platform`), `DELETE /v1/devices/{fcm_token}` | Register / remove a push token |
| `GET /v1/notifications?limit=50`, `POST /v1/notifications/{id}/read` | In-app notifications |

### Example: `GET /v1/predictions/latest?symbol=BTC&tf=1h`

```json
{
  "symbol": "BTC",
  "timeframe": "1h",
  "label": "up",
  "p_up": 0.582,
  "base_open_time": "2026-10-03T13:00:00Z",
  "target_open_time": "2026-10-03T14:00:00Z",
  "target_close_time": "2026-10-03T15:00:00Z",
  "base_close": "67123.45",
  "reasons": [
    {"code": "rsi", "text": "RSI 38: leaving oversold"},
    {"code": "ema_trend", "text": "Close above EMA 21 by 0.6%"},
    {"code": "sentiment", "text": "News sentiment +0.31"}
  ],
  "sentiment_agg": 0.31,
  "model": {"id": 12, "trained_at": "2026-09-28T02:10:00Z", "status": "ok"},
  "recent_accuracy": {"model": 0.541, "naive_baseline": 0.512, "n": 200},
  "disclaimer": "Signals are probabilistic estimates ...",
  "stale": false
}
```

### Example: `GET /v1/performance?symbol=BTC&tf=1h&days=30`

```json
{
  "symbol": "BTC", "timeframe": "1h", "days": 30,
  "n_predictions": 720, "n_resolved": 718, "coverage": 0.62,
  "accuracy": 0.541,
  "baseline": {"naive": 0.512, "always_up": 0.503},
  "brier": 0.2491, "brier_baseline": 0.2500,
  "by_label": {"up": {"n": 230, "accuracy": 0.55}, "down": {"n": 215, "accuracy": 0.53}}
}
```

Definitions: `accuracy` = share of **non-neutral** resolved predictions that were correct; `coverage` = non-neutral share of all resolved; `naive` accuracy = predicting the same direction as the base candle's own move over the same target candles; `brier` = mean squared error of `p_up` against the actual 0/1 outcome; `brier_baseline` = Brier of always predicting the base rate. Report the numbers as they are. If `n_resolved` is small, include `"low_sample": true`.

## WebSocket `/ws/stream`

Connect: `/ws/stream?symbols=BTC,ETH&tf=1h` (public). Optional `token=` query parameter for authenticated events later.

Server → client messages (JSON):

```json
{"type": "candle", "symbol": "BTC", "tf": "1h",
 "candle": {"t": "2026-10-03T14:00:00Z", "o": "67123.45", "h": "67200.00", "l": "67090.10", "c": "67188.00", "v": "412.3", "closed": false}}
{"type": "prediction", "symbol": "BTC", "tf": "1h", "prediction": { /* same shape as /v1/predictions/latest */ }}
{"type": "ping"}
```

Client → server: `{"type": "subscribe", "symbols": ["SOL"], "tf": "4h"}` / `{"type": "unsubscribe", ...}` / `{"type": "pong"}`.

Rules: close idle connections after 60 s without pong; limit symbols per connection (max 10); on reconnect the client re-fetches `/v1/candles` and `/v1/predictions/latest` then resumes the stream.

## Alert rule semantics

| `type` | `threshold` | Fires when |
| --- | --- | --- |
| `signal_change` | none | The new label for `(asset, timeframe)` differs from the previous prediction's label |
| `prob_above` | 0–1 | New `p_up` ≥ threshold |
| `prob_below` | 0–1 | New `p_up` ≤ threshold |
| `price_above` | price | Last price crosses above (checked every minute) |
| `price_below` | price | Last price crosses below |

At most one notification per rule per `cooldown_minutes`. Evaluate against the stored predictions so alerts match what the app shows.
