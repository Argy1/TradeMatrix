# 02 — Architecture, stack and deployment

*Created by Argy*

## Overview

```
 Next.js web (Vercel)        Flutter app (Android/iOS)
          \                      /
           \   REST + WebSocket  /
            v                   v
        FastAPI service  (Railway: "api")
          |         ^
          | read/   | poll new predictions
          v write   |
   Supabase Postgres + Auth + Storage
          ^
          | write
   Worker (Railway: "worker", APScheduler)
     |-- pulls candles      <- Binance public API (via adapter)
     |-- pulls headlines    <- public RSS feeds
     |-- scores headlines   -> Gemini API
     |-- trains / predicts  -> XGBoost model files (Supabase Storage)
     |-- sends alerts       -> Firebase Cloud Messaging
```

Key idea: the **API only serves data**; the **worker is the only place predictions are made**. A slow model run can never slow down a chart update.

## Components

### API service (`backend/app/api`)

- FastAPI, async. REST under `/v1`, WebSocket at `/ws/stream`.
- Verifies the Supabase JWT (JWKS preferred) for protected routes (watchlist, alerts, devices, notifications). Market data, predictions and performance are public read endpoints, rate limited per IP.
- Keeps **one upstream Binance WebSocket connection per active symbol/timeframe** and fans live candle updates out to connected clients in-process. (If the API is ever scaled to several instances, move fan-out to Redis pub/sub.)
- New predictions reach WebSocket clients by **polling the `predictions` table every 5 seconds** for rows newer than the last seen id (simple, no Redis needed for the MVP).
- Health check: `GET /health` (checks DB connectivity) used by Railway.

### Worker service (`backend/app/worker`)

One process, one instance only. Scheduled jobs (UTC):

| Job | Schedule | What it does |
| --- | --- | --- |
| `ingest_candles` | at each candle close + 5 s (1h: every hour; 4h: 00,04,08,12,16,20; 1d: 00:00) | Fetch newly closed candles for all active assets, upsert into `candles` |
| `run_predictions` | right after `ingest_candles` for that timeframe | Build features, predict, read the coin's news sentiment (blended only when `k > 0`), store a row in `predictions` |
| `resolve_outcomes` | after each candle close | Fill `prediction_outcomes` for predictions whose target candle just closed |
| `evaluate_alerts` | after each candle close, last step | Check signal alerts against the new predictions, write `notifications` |
| `ingest_news` | every 15 min (:02, :17, :32, :47) | Fetch headlines from the RSS feeds, dedupe by URL and by title, tag assets by keyword, delete headlines older than 90 days |
| `score_sentiment` | every 15 min (:04, :19, :34, :49) | Send unscored headlines from the last 24 h to Gemini in batches, validate and store the results; stops at the daily budget |
| `check_price_alerts` | every 1 min (second :30) | If any price alert exists: fetch last prices and fire the alerts whose level was crossed since the previous check |
| `retrain_models` | weekly, Sunday 02:00 UTC | Walk-forward train per asset/timeframe; activate new model only if it is not worse |
| `heartbeat` | every 5 min | Log a heartbeat and update `worker_heartbeat` for monitoring |

All jobs are **idempotent** (unique constraints + upserts) and take a Postgres advisory lock so two instances can never run the same job at once.

### Data adapters (`backend/app/data`)

- `exchanges/base.py` defines `ExchangeClient` with `get_klines(symbol, timeframe, start, end, limit)`, `get_last_price(symbol)`, `stream_klines(symbols, timeframe)`.
- `exchanges/binance.py` is the first implementation (public endpoints only, no key). Add `bybit.py` / `okx.py` / `kraken.py` only if Binance is not reachable. Selected by the `EXCHANGE` variable.
- `news/` has `rss.py` (reader), `tagging.py` (coin keywords) and `ingest.py`. Sources are free public RSS feeds: CoinDesk, Cointelegraph, Decrypt, The Block, Bitcoin Magazine and The Defiant. CryptoPanic was dropped on 2026-10-07 because it is paid only. A new source is one more entry in `RSS_FEEDS`, or a new class with a `fetch()` method.

### Web app (`apps/web`)

Next.js App Router, TypeScript strict, Tailwind, shadcn/ui, TanStack Query, `lightweight-charts`, `@supabase/ssr` for auth. Pages: `/`, `/markets/[symbol]`, `/track-record`, `/watchlist`, `/alerts`, `/login`, `/about`. A typed API client is generated from the FastAPI OpenAPI schema (`openapi-typescript`).

### Mobile app (`apps/mobile`)

Flutter, Riverpod, go_router, dio, `supabase_flutter`, `firebase_messaging`. Screens mirror the web pages (Markets, Coin detail, Track record, Watchlist, Alerts, Settings/About). Chart: start with the `candlesticks` package (check maintenance and license first); fall back to another chart package if it lacks indicators. API models are generated with `openapi-generator` (`dart-dio`) or hand-written with `json_serializable`.

## Candle-close data flow (the heart of the system)

1. Worker wakes at e.g. 14:00:05 UTC for the 1h timeframe.
2. Fetch the just-closed candle(s), upsert into `candles` (drop any candle that is not closed).
3. For each asset: load the last N closed candles, build features, load the active model, compute `p_up` (calibrated).
4. Read the aggregated sentiment for the asset (shadow mode: store it, do not blend while `SENTIMENT_BLEND_K=0`).
5. Compute the label with the neutral band, build the "why" reasons, insert into `predictions`.
6. Resolve outcomes of the previous prediction (its target candle just closed).
7. Evaluate alerts, create `notifications`, send FCM pushes.
8. API polling picks up the new rows and broadcasts a `prediction` event to WebSocket clients.

## Stack details and decisions

| Decision | Choice | Reason |
| --- | --- | --- |
| One language for data + API | Python | The ML and the API share code and tests |
| One backend package, two services | `backend/` run as `api` and `worker` | Shared code, simple Railway setup |
| DB access | SQLAlchemy 2.x async + `asyncpg` | Standard, typed |
| Migrations | Supabase CLI SQL files | Same tool that manages RLS and auth |
| Scheduler | APScheduler (AsyncIOScheduler) | Enough for one worker, no queue needed |
| Model storage | Supabase Storage private bucket `models` | No extra infra; version recorded in `model_versions` |
| ML | XGBoost classifier + isotonic/Platt calibration | Strong on tabular data, explainable via feature importances |
| Indicators | Own pandas/numpy implementations of RSI (Wilder), EMA, MACD, Bollinger, ATR, ADX, OBV | No dependency risk; verify against a maintained library in tests |
| LLM | Gemini API via `google-genai` | Argy's choice; structured JSON output |
| Realtime for predictions | DB polling every 5 s | Avoids Redis and Postgres LISTEN (not supported on pooled connections) |
| Redis | Optional, phase 6 | Only needed to scale WebSocket fan-out |

Always check current versions of: Next.js, React, Flutter, FastAPI, SQLAlchemy, XGBoost, `google-genai`, `supabase_flutter`, `lightweight-charts` when scaffolding, and pin them.

## Environment variables

See `.env.example` at the repo root for the full list and where each belongs.

| Variable | Used by | Notes |
| --- | --- | --- |
| `DATABASE_URL` | api, worker | Supabase pooled string (port 6543), asyncpg format |
| `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` | api, worker | Server only; service role bypasses RLS |
| `SUPABASE_JWKS_URL` / `SUPABASE_JWT_SECRET` | api | Verify user tokens |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | worker | Server only |
| `SENTIMENT_BLEND_K` | worker | Blend weight (0 at first) |
| `SENTIMENT_MAX_PER_RUN`, `SENTIMENT_BATCH_SIZE`, `SENTIMENT_MAX_PER_DAY` | worker | Cost guard: headlines per run, per request and per UTC day |
| `EXCHANGE` | api, worker | `binance` by default |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | worker | JSON content as a Railway variable |
| `CORS_ORIGINS` | api | Web origins allowed |
| `NEXT_PUBLIC_*` | web | Only Supabase URL, anon key, API base URL, WS URL |
| `--dart-define` values | mobile | Supabase URL, anon key, API base URL, WS URL |

## Deployment

- **Supabase:** create one cloud project; apply `supabase/migrations` with the Supabase CLI; enable Google provider in Auth when needed; create the private `models` Storage bucket.
- **Railway:** one project `tradematrix` with services from this repo, root directory `backend`:
  - `api` — start command `uvicorn app.api.main:app --host 0.0.0.0 --port $PORT`, health check `/health`.
  - `worker` — start command `python -m app.worker.main`, **exactly one replica**.
  - Variables set in the Railway dashboard (never committed). Add a Redis service only when needed.
  - Add a `Dockerfile` or rely on the Railway builder; whichever you choose, document it in `backend/README.md`.
- **Vercel:** project root `apps/web`, env vars from `.env.example` (`NEXT_PUBLIC_*` only).
- **Firebase:** one project for FCM; Android/iOS app registration happens in Phase 5.
- **CI (GitHub Actions):** on every push run backend `ruff` + `pytest`, web `lint` + `test` + `build`, mobile `flutter analyze` + `flutter test`.

## Observability and errors

- Structured JSON logs with `asset`, `timeframe`, `job`, `duration_ms`.
- Sentry (free tier) in api, worker and web.
- A `/v1/status` endpoint returns the last successful run time per job and the active model versions; the About/Status page shows "data fresh as of …".
- If a job fails, log it, keep the previous prediction visible and mark the data as stale in the API response (`stale: true`) instead of showing wrong numbers.

## Local development

1. `supabase start` (local Postgres + Auth) **or** use the cloud dev project.
2. Backend: `cd backend && uv sync && uv run uvicorn app.api.main:app --reload` and in a second terminal `uv run python -m app.worker.main`.
3. Web: `cd apps/web && npm install && npm run dev`.
4. Mobile: `cd apps/mobile && flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000 ...` (Android emulator reaches the host at `10.0.2.2`).
