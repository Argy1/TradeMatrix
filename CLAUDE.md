# TradeMatrix AI — project guide for Claude Code

> Created by Argy. Read this file first, then read every file in `docs/` before writing any code.

## What we are building

**TradeMatrix AI** is a crypto market-signal product with a **web app (Next.js)** and a **mobile app (Flutter)** that share **one backend (FastAPI, hosted on Railway)** and **one database (Supabase)**.

For each supported coin and timeframe the apps show a live candlestick chart and a **signal: Up / Down / Neutral with a probability**, plus the reasons behind it. The signal blends three things:

1. Technical indicators (RSI, MACD, EMAs, Bollinger Bands, ATR, volume).
2. A machine-learning model (XGBoost) that outputs the probability the next candle closes higher.
3. News sentiment scored by the **Gemini API**.

It is a **decision-support tool**. It is not an auto-trader, it never places trades, and it never promises profit.

Design: follow `docs/08-DESIGN.md` ("Matrix Glass" 3D look, plain-language signal card). The visual reference canvas is linked at the top of that file; the file wins if they differ.

Brand: the product name is **TradeMatrix AI** and the line **"Created by Argy"** is shown under the name (web header, Flutter splash screen, About page).

## Owner and how to work with him

- Owner: **Argy** — a full-stack developer who builds this to **learn**. Explain the "why" briefly when you make a design decision, and keep code readable with short comments where the idea is not obvious.
- He prefers concise answers and ready-to-use results with minimal back-and-forth. Make reasonable decisions yourself, state them in one line, and only stop to ask when a choice is expensive to undo or needs his accounts/keys (see "Ask Argy first").
- Code, comments, docs and commit messages are in English. Reply in the language Argy writes to you in (English or Indonesian).

## Non-negotiable rules

1. **Honest about prediction.** Never hard-code or claim an accuracy figure. Every signal screen shows the disclaimer (docs/06). The track-record page always shows the naive baseline next to the model's accuracy.
2. **No data leakage.** Features at time `t` use only candles that were closed at `t`. Split data by time, never randomly. Walk-forward validation only.
3. **No trading.** v1 never executes trades and never stores exchange API keys.
4. **Secrets stay secret.** Never commit `.env*` files (except `.env.example`). The Gemini key and the Supabase service-role key exist only on the server (Railway), never in the web or mobile apps.
5. **Clients are thin.** Web and mobile never compute indicators or probabilities. They only draw what the API returns.
6. **Gemini is called only from the backend worker**, with a JSON schema, temperature 0, and validated output.
7. **Every prediction is auditable:** store `model_version_id`, the feature snapshot (values in `predictions.feature_values`, their names once in `model_versions.feature_names`; older rows keep the `features` JSON) and the sentiment value used.
8. **Jobs are idempotent.** Re-running a job must never create duplicate rows (use unique constraints and upserts).
9. **Signals must be easy to understand:** direction word + icon + probability + plain sentence + reasons + reliability vs baseline, always together (docs/08). Never convey direction by color alone.
10. **Stay in v1 scope** (docs/01). Do not add features, markets or paid plans without asking.

## Stack (summary — details in docs/02)

| Layer | Choice |
| --- | --- |
| Web | Next.js (App Router) + TypeScript + Tailwind + shadcn/ui + TanStack Query + TradingView Lightweight Charts, deployed on Vercel |
| Mobile | Flutter (Dart) + Riverpod + go_router + dio + supabase_flutter + firebase_messaging |
| Backend API | Python 3.12 + FastAPI (REST + WebSocket), deployed on Railway |
| Worker | Same Python package, separate Railway service, APScheduler, runs at each candle close |
| Database + Auth | Supabase (Postgres, Auth, Row Level Security, Storage for model files) |
| ML | pandas, numpy, scikit-learn, XGBoost |
| AI sentiment | Gemini API through the official `google-genai` Python SDK |
| Market data | Binance public market-data API (REST klines + WebSocket) behind an adapter |
| News | Free public RSS feeds (CoinDesk, Cointelegraph, Decrypt, The Block, Bitcoin Magazine, The Defiant). CryptoPanic was dropped on 2026-10-07: paid only |
| Push | Firebase Cloud Messaging (Flutter) |
| Optional later | Redis on Railway for pub/sub and caching |

Before using any library, check its current version and docs. Do not rely on memory for model names (Gemini), SDK signatures or free-tier limits; look them up.

## Repository layout (create it as phases need it)

```
TradeMatrix/
  CLAUDE.md                 this file
  README.md                 how to start
  docs/                     the full plan (read all of it)
  supabase/migrations/      SQL migrations (source of truth for the schema)
  backend/                  FastAPI + worker + ML in ONE Python package
    app/api/                routers, schemas, auth dependency, websocket
    app/worker/             scheduler and jobs
    app/data/               exchange + news adapters, ingestion
    app/features/           indicators and feature building
    app/ml/                 training, calibration, backtest, prediction, registry
    app/sentiment/          Gemini client, prompt, schemas, aggregation
    tests/  notebooks/
  apps/web/                 Next.js app
  apps/mobile/              Flutter app
```

## Commands (fill in the exact ones when you scaffold each part)

- Backend: `cd backend && uv run pytest` / `uv run ruff check .` / `uv run uvicorn app.api.main:app --reload` / `uv run python -m app.worker.main`. `uv run pytest -m db` runs the SQL tests against the real database inside transactions that are rolled back. `uv run pytest -m live` runs the one test that calls the real exchange.
- Web: `cd apps/web && npm run dev` / `npm run lint` / `npm test` / `npm run typecheck` / `npm run api:types` (regenerate API types after backend changes)
- Mobile: `cd apps/mobile && flutter run` / `flutter analyze` / `flutter test`
- Database: `npx supabase db push` (apply `supabase/migrations`). The Supabase CLI runs through `npx`, there is no global install. While the CLI is logged in to a different Supabase account, apply migrations through the Supabase connector or with `npx supabase db push --db-url <session pooler URL>`.
- Gate 0 check: `uv run scripts/gate0_check.py` (from the repo root; reads the root `.env`)
- Models (from backend/): `uv run python -m app.ml.tune` (choose settings on 2021-2024) / `uv run python -m app.ml.backtest` (evaluate) / `uv run python -m app.ml.train_models` (train, store, activate). Then redeploy `worker` so it loads the new files.
- Audit snapshots (from backend/): `uv run python -m app.ml.snapshots` stores the feature names of older models and converts older signals to the compact form, with a check; `--clear-json` removes the converted JSON afterwards. Read a snapshot with `select * from prediction_features where prediction_id = ...`.
- Python: `uv` manages Python 3.12 (the system Python is 3.14 and is not used).

If a command here does not exist yet, create it as part of the task and update this section.

## Conventions

- **Python:** type hints everywhere, pydantic v2 models for all API input/output, `ruff` for lint and format, `pytest` for tests, SQLAlchemy 2.x async with `asyncpg`. CPU-heavy work (pandas, XGBoost) runs in `asyncio.to_thread`. Supabase pooled connections need `statement_cache_size=0` for asyncpg.
- **SQL:** all schema changes are new files in `supabase/migrations/` (never edit an applied migration). RLS is enabled on every table.
- **API:** versioned under `/v1`, OpenAPI generated by FastAPI is the contract. Web and mobile clients are generated from or typed against it.
- **Web:** TypeScript strict, server components by default, no secrets in `NEXT_PUBLIC_*` except the Supabase URL and anon key.
- **Mobile:** feature-first folders, Riverpod providers, immutable models.
- **Time:** store UTC everywhere. Convert to the user's timezone (default Asia/Jakarta, WIB) only in the UI.
- **Money/prices:** `numeric` in Postgres, strings or decimals over the API where precision matters; never floats for stored prices.
- **Git:** run `git init` in the first task. Small commits with conventional messages (`feat:`, `fix:`, `docs:`, `test:`, `chore:`). Do not push or create remotes without Argy's OK.

## Definition of done (for every task)

- It works end to end for the thing the task describes (run it, do not just write it).
- Tests exist for the logic that can break (indicators, labels/no-leakage, API contracts, job idempotency).
- Lint and type checks pass.
- No secrets in code. `.env.example` updated if you added a variable.
- The checkbox in `docs/05-ROADMAP.md` is ticked and the "Status" section below is updated.
- You told Argy in 2–4 lines what you built and how to run or check it.

## Ask Argy first (do not guess)

- Creating or paying for accounts, any real API key or secret value, deployments to production.
- Whether Binance is reachable from his location (if not, switch the adapter to Bybit, OKX or Kraken).
- The final Gemini model name to use (look up the current list first, propose one).
- Anything that changes v1 scope, the brand, or the legal disclaimer.

## Status

Update this block as work progresses.

- Current phase: **Phase 4 — Sentiment and alerts** (see docs/05-ROADMAP.md). Gates 0, 1 and 2 passed on 2026-10-03 (Gate 2 by Argy's decision). Gate 3 passed on 2026-10-09 by Argy's decision at 6.0 of 7 days (145 of 145 hourly runs complete, no errors).
- Phase 4 was deployed on 2026-10-09 (`main` = `0058cb3`, built on branch `phase-4`): compact feature snapshot, news from six free RSS feeds, Gemini sentiment in shadow mode (`k = 0`), `GET /v1/news` and the news list, alerts (API, worker checks, `/alerts` page). Verified live: the 17:00 WIB run wrote 16 of 16 signals in the compact form with their news tone.
- What the `worker` runs now: `candle_close` at :00:05 (ingest candles, predict, resolve outcomes, evaluate alerts), `ingest_news` at :02/:17/:32/:47, `score_sentiment` at :04/:19/:34/:49, `check_price_alerts` every minute at second 30, heartbeat every 5 minutes. It needs `GEMINI_API_KEY` and `GEMINI_MODEL` on Railway; without them it runs but does not score headlines.
- Left in Phase 4 (details in docs/05): the `--clear-json` clean-up a few days after 2026-10-09; Argy's signed-in check of the alerts pages; the sentiment evaluation notebook once 4 weeks of data exist (from about 2026-11-06); optional email alerts.
- Models: 48 active (16 coins x 1h/4h/1d) in the private `models` bucket and `model_versions`. `ok`: 1h for BTC, ETH, BNB, XRP, ADA, LINK, AVAX, LTC, DOT, BCH, XLM. Everything else is `degraded` (all 4h, the pooled 1d, and 1h for SOL, DOGE, UNI, NEAR, TRX). Notebook: `backend/notebooks/01_backtest_walkthrough.ipynb`. Model versions 1 to 15 are dead files from the first training run (the `__main__` pickle problem); they are inactive and nothing uses them.
- Web is live at https://tradematrix-rho.vercel.app (Vercel project `tradematrix`, auto-deploys on push to `main`): markets home, coin page (chart, live updates, signal card, news tone), track record, watchlist, alerts, About. Email login; Google sign-in later. Run locally with `cd apps/web && npm run dev` (reads `apps/web/.env.local`).
- Deploying the backend: from `backend/`, `railway up --service api --detach` and `railway up --service worker --detach` (they upload the local files; a push to GitHub does not deploy Railway). Deploy the worker between two hourly runs, and apply migrations before the code that needs them.
- Web types before an API change is deployed: from `backend/`, write `app.openapi()` to a JSON file and run `npx openapi-typescript <file> -o src/lib/api/schema.d.ts` in `apps/web` (`npm run api:types` reads the deployed API).
- Sentry is live (web + api + worker). Supabase Auth Site URL set by Argy.
- 16 coins since 2026-10-03 (scope change by Argy). Adding a coin later: migration in `supabase/migrations/`, `uv run python -m app.data.backfill --symbols X --since 2020-09-01`, `uv run python -m app.ml.backtest --symbols X --timeframes 1h,4h`, `uv run python -m app.ml.train_models --symbols X --timeframes 1h,4h` and `--timeframes 1d` (pooled), then redeploy `api` so the live stream includes it. Adding a coin after a gate has passed does not restart that gate; the new coin only starts with an empty live track record.
- Storage: the database was about 150 MB of the 500 MB free tier on 2026-10-09. Measured growth before the compact snapshot was about 32 MB a month at 16 coins; expected now about 18 to 20 MB a month (a signal row went from about 1,430 to about 530 bytes; candles are about 118 bytes each; headlines are deleted after 90 days). Argy decided to stay at 16 coins for now; the real lever for less growth is fewer coins or timeframes.
- Open for Argy: sign in and try the alerts pages (docs/05); rotate the secrets that were shared in chat (the worker uses the Gemini key that was in `.env` on 2026-10-09; the database password and the Supabase secret key must be changed together with the Railway variables, so tell Claude first); check the Gemini request limits at https://aistudio.google.com/rate-limit.
- Open question for Argy: the pooled 1d model's calibration falls back to the base rate, so it gives every coin the same probability (57% Up after the 16-coin retrain), flagged `degraded`.
- Supabase project: `TradeMatrix` (ref `hoanadzkysksfvgimukn`, ap-southeast-1). Railway: project `tradematrix`, services `api` (https://api-production-a829.up.railway.app) and `worker`. GitHub: https://github.com/Argy1/TradeMatrix (private).
- Decisions: `GEMINI_MODEL=gemini-3.8-flash` (approved 2026-10-03). Exchange stays Binance through the market-data-only hosts in `BINANCE_REST_URL` / `BINANCE_WS_URL`.
- Known issues:
  - `api.binance.com` is blocked on Argy's network, and it also rejects US IPs. Always use the hosts from the env variables, and pick a Singapore region on Railway in Phase 1.
  - The Supabase CLI on this machine is logged in to another Supabase account, so `supabase link` cannot see this project (see Commands).
  - `flutter doctor`: the Visual Studio C++ workload is incomplete. It only affects Windows desktop builds, which are not a target.
