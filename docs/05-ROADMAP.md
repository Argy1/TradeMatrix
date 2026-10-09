# 05 — Roadmap: six phases, tasks and gates

*Created by Argy*

Work phase by phase. Tick the boxes as you finish. **Do not start a phase before the previous gate passes.** Weeks are rough estimates for one developer working part-time (about 10–15 focused hours a week); the order matters more than the dates.

Legend: `[ ]` todo, `[x]` done. After each task update "Status" in `CLAUDE.md`.

---

## Phase 0 — Setup (a few evenings)

Goal: tools, accounts and an empty but organized repo.

- [x] `git init`, first commit with `CLAUDE.md`, `README.md`, `docs/`, `.gitignore`, `.env.example`, the SQL migration.
- [x] Ask Argy to create (or confirm) accounts and give you values safely: Supabase project, Railway project, Vercel account, Google AI Studio API key (Gemini). Firebase can wait until Phase 5. Never paste real keys into files that are committed.
  - Supabase project `TradeMatrix` (ref `hoanadzkysksfvgimukn`, ap-southeast-1, free plan); Railway and Vercel accounts confirmed; Gemini key is in the git-ignored root `.env`. The Railway project is created at deploy time in Phase 1, which also needs the database password in `.env`.
- [x] Verify tools: Python 3.12 + `uv`, Node LTS, Flutter SDK (`flutter doctor`), Supabase CLI, Railway CLI.
  - uv 0.12.22 with uv-managed Python 3.12.15, Node 24.13.1, Flutter 3.41.1 (Android toolchain OK), Supabase CLI 2.119.0 through `npx`, Railway CLI 4.40.0.
- [x] Test that the exchange API is reachable from Argy's location (`GET /api/v3/klines` for BTCUSDT 1h). If blocked, choose another exchange and tell Argy.
  - `api.binance.com` is blocked by the ISP. Binance's market-data-only hosts work, so the exchange stays Binance: `BINANCE_REST_URL=https://data-api.binance.vision`, `BINANCE_WS_URL=wss://data-stream.binance.vision`.
- [x] Look up the current Gemini model list in Google's docs, propose a Flash-tier model for sentiment, get Argy's OK, set `GEMINI_MODEL`.
  - `gemini-3.8-flash`, approved by Argy on 2026-10-03.
- [x] Apply the migration to the Supabase project (`supabase db push`) and verify the 12 tables and 5 seeded assets exist.
  - Applied through the Supabase connector (the local CLI is logged in to another account); history row aligned to `20261003000000`. Verified: 12 tables, RLS on all, 11 policies, 5 assets.

**Gate 0:** the database exists with the schema, the exchange is reachable, and a Gemini test call returns valid JSON. Check with `uv run scripts/gate0_check.py`.

Gate 0 passed on 2026-10-03: schema verified (12 tables, 5 assets), 2 closed BTCUSDT 1h candles fetched, and `gemini-3.8-flash` returned schema-valid JSON for 3 sample headlines.

---

## Phase 1 — Foundations (weeks 1–2)

Goal: candles flow into the database and a chart endpoint works.

- [x] Scaffold `backend/` (uv project, FastAPI app, config via pydantic-settings, async SQLAlchemy engine with `statement_cache_size=0`, ruff, pytest).
- [x] `ExchangeClient` interface + Binance implementation (klines REST, pagination, rate-limit handling, closed-candle filter).
- [x] `ingest_candles` job + CLI `python -m app.data.backfill` for the history sizes in docs/03; idempotent upserts; data-quality checks.
  - The job logic is `app/data/ingest.py`; the scheduler that runs it at every candle close is the Phase 2 worker.
- [x] Core indicators + tests (RSI, EMA, MACD, Bollinger, ATR, ADX, OBV).
- [x] API: `/health`, `/v1/assets`, `/v1/candles` (with indicator series), `/v1/status`, OpenAPI docs, CORS, rate limit.
- [x] Supabase JWT verification dependency (used later by protected routes) + a test with a fake token.
- [x] Deploy `api` to Railway with env vars; confirm `/health` works on the public URL.
  - https://api-production-a829.up.railway.app, Railway project `tradematrix`, service `api`, region asia-southeast1 (Singapore).
- [ ] GitHub Actions for backend lint + tests.
  - `.github/workflows/backend.yml` is pushed to the private repo; its first result has not been checked yet.

**Gate 1:** 2 years of 1h candles for the 5 coins are stored; `GET /v1/candles` returns candles with valid indicators on the Railway URL; tests pass.

Gate 1 passed on 2026-10-03: 17,520 1h candles per coin (2.00 years, no gaps) plus 3 years of 4h and 5 years of 1d; `/v1/candles` on the Railway URL returns candles with every indicator filled; 60 unit tests, 4 database tests and 1 live exchange test pass.

---

## Phase 2 — Prediction engine v1 (weeks 3–5)  ← the most important gate

Goal: a model that is **measured honestly**.

- [x] Feature builder (docs/03) with the no-leakage test.
- [x] Baselines (`naive`, `always_up`) and the metrics module (accuracy, precision/recall, Brier, log loss, simulated return with fees, drawdown, Sharpe).
- [x] Walk-forward splitter + tests.
- [x] XGBoost training + calibration; model artifacts to Supabase Storage; `model_versions` rows.
  - `uv run python -m app.ml.train_models`: re-runs the evaluation, trains on all data, uploads to the private `models` bucket (migration `20261003120000_models_bucket.sql`), activates a `model_versions` row with the metrics. Status `degraded` when the model does not beat the baselines.
- [x] Backtest report generator (`backend/reports/…md`) for each asset/timeframe.
  - First run, 2026-10-03, 11 reports: no model beats the baselines with a margin that survives the bootstrap check. On 1h the Brier score equals the base rate, so there is no probability edge. On 4h and pooled 1d the Brier score is significantly worse than the base rate (overconfident). Simulated long-only returns after fees lose money on every coin except XRP 4h, which still trails buy and hold.
  - Improvement round, 2026-10-03 (Argy chose option 1). Changes: 1h/4h/1d history extended back to 2020-09; larger early-stopping and calibration windows; 4 candidate settings compared ONLY on test folds inside 2021–2024 (`reports/tuning_2026-10-02.md`); winners frozen in `app/ml/config.py`; then scored once on 2024-10 onwards.
  - Result: **1h beats both baselines for BTC, ETH, BNB and XRP** (accuracy on calls 55–57% vs naive about 48%, coverage 14–18%; Brier 0.2489–0.2495 vs 0.2500; both bootstrap intervals above zero, ETH only just). SOL 1h, all 4h and the pooled 1d model do not. Trading every hourly Up call after fees still loses money: the edge is real but smaller than trading costs.
  - Caveat: the 2024-10 onwards period was also scored once in the first run, before the improvement round, so it is not perfectly unseen. Fresh live predictions are the real test.
- [x] `run_predictions` job (idempotent), `resolve_outcomes` job, `worker` service with APScheduler, advisory locks, heartbeat table updates.
  - Every hour at :00:05 UTC: `ingest_candles` → `run_predictions` (15 models, deterministic reasons, feature snapshot, idempotent) → `resolve_outcomes`; heartbeat every 5 minutes; transaction-level advisory locks.
- [x] Deploy `worker` to Railway (one replica). Predictions appear in the database at every candle close.
  - Railway service `worker` (Singapore, one replica). First 15 predictions stored on 2026-10-03; a second run created none (idempotent).
- [x] Notebook in `backend/notebooks/` that reproduces the report so Argy can read and learn from it.

**Gate 2 (decision point):** show Argy the report. Continue to Phase 3 only if the out-of-sample accuracy and Brier score beat the baselines with a margin that survives the bootstrap check **or** Argy explicitly decides to proceed with the honest result anyway (the track-record page will show it). If the model does not beat the baseline, spend extra time on features/data/validation first and re-run. Never tune on the test folds.

Gate 2 decision, 2026-10-03 (Argy): after one improvement round, 1h beats the baselines for BTC, ETH, BNB and XRP; SOL 1h, all 4h and 1d do not. Proceed to Phase 3 and keep all three timeframes; signals from `degraded` models show the docs/08 warning "This model is performing below the baseline right now. Treat the signal with extra caution."

---

## Phase 3 — Web MVP (weeks 6–8)

Goal: a usable dashboard on Vercel.

- [x] Scaffold `apps/web` (Next.js, TS strict, Tailwind, shadcn/ui, TanStack Query), theme with the brand: **TradeMatrix AI** + "Created by Argy" under it.
  - Next.js 16.3, Tailwind 4, TanStack Query 5, Lightweight Charts 5. shadcn/ui is not used yet: the docs/08 components are custom (glass, keycap, orb), so there was nothing to take from it so far.
- [x] Implement the design system from `docs/08-DESIGN.md` first (tokens, glass card, 3D buttons, orb with probability ring, signal card, tiles) and match the design canvas at 1440, 1024, 768 and 390 px (Playwright screenshots).
  - Compared with the canvas on 2026-10-03 and aligned: hero copy and 3D scene (badge shows the live BTC 1h signal, not sample data), one-table signals list, How-it-works tiles, track-record panel, active nav, guide strip copy, chart header with period high/low, NEXT ghost column, section subtitles. Kept docs/08 where the canvas differed: the docs/06 disclaimer text, a probability on Neutral chips, footer brand lockup. Playwright checks 1440/1024/768/390 px.
- [x] Generate the typed API client from OpenAPI.
  - `npm run api:types` (openapi-typescript) + openapi-fetch.
- [x] Supabase Auth (email + Google), protected routes, session handling.
  - Email + password with email confirmation (PKCE, `/auth/callback`), session refresh in `src/proxy.ts`. Google sign-in postponed by Argy (needs his own Google Cloud OAuth client).
- [x] Markets list page; coin detail page with `lightweight-charts` (candles, volume, EMA/Bollinger/RSI/MACD toggles from API data), timeframe switcher.
- [x] Signal card with reasons, valid-until countdown, recent accuracy vs baseline, disclaimer.
  - Plus the degraded warning (Gate 2 decision) and the stale banner. Live accuracy only (docs/06).
- [x] WebSocket client: live candle updates + new prediction events, reconnect logic.
  - Backend `/ws/stream`: one upstream Binance market-data connection, fan-out, 5 s prediction polling, ping/idle limits.
- [x] Track-record page; About page (how it works, disclaimer, brand line).
- [x] Watchlist (login). Loading / empty / error states, mobile-responsive layout.
  - `/v1/watchlist` (JWT, scoped to the token's user) + `/watchlist` page and a watch toggle on the coin page.
- [x] Deploy to Vercel; CORS configured; Sentry added.
  - Vercel: https://tradematrix-rho.vercel.app (project `tradematrix`, root `apps/web`, auto-deploys on push to `main`, functions in sin1). CORS on the API allows it plus this project's preview URLs. Sentry live on 2026-10-03: projects `tradematrix-web` (Vercel `NEXT_PUBLIC_SENTRY_DSN`) and `tradematrix-backend` (Railway `SENTRY_DSN` on api + worker); errors + 10% tracing, no personal data. Local development keeps Sentry off.
- [x] Basic tests (vitest for utils/hooks) and a Playwright smoke test of the coin page.
  - `npm test` (vitest) and `npm run test:e2e` (Playwright; `PW_CHANNEL=chrome` locally, `BASE_URL=...` against a deployed site).

**Gate 3:** the live site shows real signals and a live chart; signals are logged for 7 days with no missed runs; `/v1/status` shows fresh jobs.

Scope change 2026-10-03 (Argy): 11 more coins (16 total). Argy chose to add them now and restart the Gate 3 clock: the 7-day window starts at the first hourly run with all 16 coins predicted, so the earliest pass is about 2026-10-10.

Gate 3 decision, 2026-10-09 (Argy): passed by decision at 6.0 of the 7 days, one day early. Checked against the database at 16:16 WIB: 145 of 145 hourly runs complete since the clock started (4h: 36 of 36, 1d: 6 of 6), each with all 16 coins, slowest run 17.6 seconds after the hour, no job errors, candles fresh, live site and API answering. The full 7 days would have been complete on 2026-10-10 at 16:00 WIB.

New-coin results (frozen settings, scored on 2024-10 onwards, reports in `backend/reports/`): 1h beats both baselines for ADA, LINK, AVAX, LTC, DOT, BCH and XLM; DOGE, UNI, NEAR and TRX do not. No 4h model beats them. The pooled 1d model, retrained on all 16 coins, improved (53.7% vs naive 50.1%) but its Brier score is still not better than the base rate, so it stays `degraded`. Totals: 48 active models, 11 `ok` (all 1h), 37 `degraded`.

---

## Phase 4 — Sentiment and alerts (weeks 9–10)

Goal: Gemini sentiment in **shadow mode**, plus alerts.

- [ ] First task after Gate 3 (approved by Argy 2026-10-03): compact feature snapshot, to slow database growth from about 25 MB to about 11 MB a month. Each signal stores 33 feature values as JSON with names (about 1,070 bytes); store them as `predictions.feature_values real[]` in the model's feature order (about 160 bytes) and the names once in `model_versions.feature_names text[]`.
  - Additive migration first (new columns, `features` becomes nullable), deployed between two hourly runs so no run is missed.
  - Fill `feature_names` for the existing models from their model files.
  - A view that joins names and values back into JSON, so an audit stays one query.
  - Test: a snapshot reads back to the same values in the same order (the main risk is a name/value order mix-up).
  - Convert the old rows and compare them with the JSON; drop the `features` column in a later migration only after they match.
  - Update the wording of rule 7 in `CLAUDE.md` ("features JSON" becomes "feature snapshot") and docs/03 if it names the column.
  - Status 2026-10-07: written and unit-tested on branch `phase-4` (migration `20261007120000_compact_feature_snapshot.sql`, `app/ml/predict.py`, `app/ml/registry.py`, `app/ml/snapshots.py`, rule 7 and docs/04 wording). Not applied and not deployed. The worker only writes the compact form when the names stored on the model version match the model's own list exactly; otherwise it keeps writing JSON, so the order of the steps below cannot produce a wrong snapshot.
  - Deploy steps for the whole `phase-4` branch, after Gate 3 passes, all between two hourly runs (not in the first minutes of an hour). The order matters: database first, then the backend, then the website, so nothing ever calls something that does not exist yet.
    1. Apply the migration (Supabase connector, then set its `schema_migrations` version to `20261007120000`).
    2. On the `phase-4` checkout: `uv run pytest -m db`. The snapshot tests and the prediction-job SQL test stop skipping and must pass.
    3. Set `GEMINI_API_KEY` (after Argy rotated it) and `GEMINI_MODEL` on the Railway `worker` service.
    4. Deploy `api`, then `worker`, from the `phase-4` checkout (`railway up` uploads the local files, so it does not need the merge). The next hourly run must log `created=16` (still JSON snapshots at this point), and `/v1/status` must list `ingest_news` and `score_sentiment`.
    5. Merge `phase-4` into `main`: Vercel then deploys the website with the news list. Run `npm run api:types` and check that `schema.d.ts` does not change (it was generated from the local API description).
    6. `uv run python -m app.ml.snapshots`: stores the feature names of the 68 existing model versions, converts the old signals and checks them. From the next run on, new signals are compact.
    7. A few days later: `uv run python -m app.ml.snapshots --clear-json`, then a new migration that drops `predictions.features` once no row needs it.
- [ ] `ingest_news` from RSS feeds with dedupe and asset keyword tagging. (CryptoPanic was in the original plan; Argy dropped it on 2026-10-07 because it is paid only.)
  - Status 2026-10-07, branch `phase-4`: written and tested (`app/data/news/`). Six free feeds: CoinDesk, Cointelegraph, Decrypt, The Block, Bitcoin Magazine, The Defiant, each checked that day (answers, parses, has headlines from the last 24 hours). Safe XML parsing with `defusedxml`, tracking parameters removed from links, dedupe by URL and by normalized title, keyword tagging for the 16 coins, headlines older than 90 days pruned. The worker job runs every 15 minutes at :02/:17/:32/:47. Not deployed.
  - Feeds tried and not used: Blockworks and DL News (their feeds were months stale), CryptoSlate (refuses automated readers), and several high-volume sites whose price-prediction and sponsored posts would add noise to the sentiment.
- [ ] Gemini client (`google-genai`): JSON schema, temperature 0, validation, retry, budget guard, prompt versioning + tests with mocked and malformed responses.
  - Status 2026-10-07, branch `phase-4`: written and tested (`app/sentiment/`: `prompts.py` v1, `schemas.py`, `gemini.py`). One real request to `gemini-3.8-flash` through this code scored 7 of 7 headlines; a hostile test headline got score 0. Not deployed.
- [ ] `score_sentiment` job; recency-weighted aggregation per asset; store `sentiment_agg` on predictions (`SENTIMENT_BLEND_K=0`).
  - Status 2026-10-07, branch `phase-4`: written and tested (`app/sentiment/score.py`, `aggregate.py`; `run_predictions` stores the coin's sentiment as of the moment the predicted candle opens, and in shadow mode never lists it as a reason). Job at :04/:19/:34/:49, at most 400 headlines per UTC day. Not deployed.
  - Before deploying: `GEMINI_API_KEY` (rotated by Argy) and `GEMINI_MODEL` must be set on the Railway `worker` service; without them the worker runs but logs `sentiment_disabled`. Argy to check his project's real request limits at https://aistudio.google.com/rate-limit (Google does not publish them per model).
  - Known limit to look at in the evaluation: one event reported by several publishers under different titles counts once per publisher (the title dedupe only catches identical titles).
- [ ] News list with sentiment badges on the coin page.
  - Status 2026-10-07, branch `phase-4`: `GET /v1/news` (`app/api/news.py`) and the "News tone" section on the coin page (`apps/web/src/components/news-list.tsx`) are written and tested. Checked in the browser at desktop and phone width with real headlines, using a local API whose database transaction was never committed (first run: 221 headlines fetched, 160 stored, 40 scored with 2 Gemini requests). `PredictionOut.sentiment_used` tells the page whether news is part of the signal; while `k = 0` the page says news is context only. Not deployed.
- [ ] Alerts: CRUD API, evaluation after each prediction + `check_price_alerts` every minute, cooldowns, `notifications` rows, in-app notification list on web.
  - Status 2026-10-07, branch `phase-4`, backend: written and tested (`app/alerts/rules.py` and `evaluate.py`, `app/api/alerts.py`, jobs `evaluate_alerts` and `check_price_alerts`). Tested with fakes and against the real database in rolled-back transactions: rules are private per user and capped at 20, a signal fires a rule once, cooldowns hold, a price rule fires on a crossing only. Push notifications (FCM, `/v1/devices`) belong to Phase 5. Not deployed.
  - Status 2026-10-07, branch `phase-4`, web: `/alerts` page (notification list, rule list with pause/resume/delete, "New alert" form), an "Alerts" link with an unread count in the header, and the button under the signal card now creates a "signal changes" rule in one tap (`apps/web/src/components/alerts-view.tsx`, `lib/alerts.ts`, `lib/api/alerts.ts`). Checked in the browser for signed-out visitors only. **Still to check by Argy after deploy, signed in:** create one rule of each kind, pause and delete one, and mark a notification as read (Claude cannot sign in through Supabase).
- [ ] Gate 4 manual check of alerts (after deploy): create a `signal_change` rule and a price rule near the current price, and confirm one notification arrives for each.
- [ ] After at least 4 weeks of shadow data: evaluation notebook (does `p_ml + k * sentiment_agg` improve Brier/accuracy?). Record the decision and the final `k` here.
- [ ] Optional: email alerts (Resend) after in-app alerts work.

**Gate 4:** sentiment is stored for every prediction, alerts fire correctly in tests and manually, and the sentiment evaluation is written down (use `k > 0` only if it helped; otherwise keep 0).

Sentiment decision log: _(fill in)_

---

## Phase 5 — Flutter app (weeks 11–14)

Goal: the mobile app against the same API.

- [ ] Scaffold `apps/mobile` (Flutter, Riverpod, go_router, dio, supabase_flutter), flavors/dart-define for URLs, splash screen showing **TradeMatrix AI — Created by Argy**.
- [ ] Build the Flutter theme and components from `docs/08-DESIGN.md` (glass, 3D buttons, orb with ring, signal card, tab bar) to match the mobile screens in the design canvas.
- [ ] API client (generated from OpenAPI or hand-written DTOs) and auth (email + Google).
- [ ] Screens: Markets, Coin detail (chart with candles/volume + indicator overlays, timeframe switch, signal card, news), Track record, Watchlist, Alerts, Notifications, About/Settings.
- [ ] WebSocket live updates with reconnect and lifecycle handling (pause in background).
- [ ] Firebase project, FCM setup (Android first), device-token registration (`/v1/devices`), worker sends pushes for alerts.
- [ ] Widget tests for the signal card and one golden or smoke test; `flutter analyze` clean.
- [ ] Build a release APK / internal testing track; iOS later if Argy has the Apple developer account.

**Gate 5:** private beta build runs on a real Android phone: login, live chart, signal, alert push received.

---

## Phase 6 — Hardening and launch (weeks 15–16)

- [ ] Tests across backend, web, mobile; CI green on every push.
- [ ] Sentry in api, worker, web, mobile; log review; alerts when a job misses two runs in a row.
- [ ] Rate limits, input validation, security review (docs/06 checklist), secrets rotation check.
- [ ] Disclaimers and terms/privacy pages; legal check before any public launch (docs/06).
- [ ] Performance pass: chart with 500 candles smooth on a mid phone; API p95 reasonable; indexes verified with `EXPLAIN`.
- [ ] Optional: Redis for WebSocket fan-out if more than one API instance is needed.
- [ ] Invite beta users; collect feedback; write a short retrospective in `docs/`.

**Gate 6:** 14 days of stable operation, track-record numbers match a manual SQL check, disclaimers in place on every signal screen.

---

## After v1 (ideas, not scope)

More coins, more timeframes, derivatives data (funding rate, open interest), on-chain data, paper trading, IDR display, subscriptions. Revisit only after Gate 6 and with Argy's approval.
