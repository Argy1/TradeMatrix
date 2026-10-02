# 05 — Roadmap: six phases, tasks and gates

*Created by Argy*

Work phase by phase. Tick the boxes as you finish. **Do not start a phase before the previous gate passes.** Weeks are rough estimates for one developer working part-time (about 10–15 focused hours a week); the order matters more than the dates.

Legend: `[ ]` todo, `[x]` done. After each task update "Status" in `CLAUDE.md`.

---

## Phase 0 — Setup (a few evenings)

Goal: tools, accounts and an empty but organized repo.

- [ ] `git init`, first commit with `CLAUDE.md`, `README.md`, `docs/`, `.gitignore`, `.env.example`, the SQL migration.
- [ ] Ask Argy to create (or confirm) accounts and give you values safely: Supabase project, Railway project, Vercel account, Google AI Studio API key (Gemini). Firebase can wait until Phase 5. Never paste real keys into files that are committed.
- [ ] Verify tools: Python 3.12 + `uv`, Node LTS, Flutter SDK (`flutter doctor`), Supabase CLI, Railway CLI.
- [ ] Test that the exchange API is reachable from Argy's location (`GET /api/v3/klines` for BTCUSDT 1h). If blocked, choose another exchange and tell Argy.
- [ ] Look up the current Gemini model list in Google's docs, propose a Flash-tier model for sentiment, get Argy's OK, set `GEMINI_MODEL`.
- [ ] Apply the migration to the Supabase project (`supabase db push`) and verify the 12 tables and 5 seeded assets exist.

**Gate 0:** the database exists with the schema, the exchange is reachable, and a Gemini test call returns valid JSON.

---

## Phase 1 — Foundations (weeks 1–2)

Goal: candles flow into the database and a chart endpoint works.

- [ ] Scaffold `backend/` (uv project, FastAPI app, config via pydantic-settings, async SQLAlchemy engine with `statement_cache_size=0`, ruff, pytest).
- [ ] `ExchangeClient` interface + Binance implementation (klines REST, pagination, rate-limit handling, closed-candle filter).
- [ ] `ingest_candles` job + CLI `python -m app.data.backfill` for the history sizes in docs/03; idempotent upserts; data-quality checks.
- [ ] Core indicators + tests (RSI, EMA, MACD, Bollinger, ATR, ADX, OBV).
- [ ] API: `/health`, `/v1/assets`, `/v1/candles` (with indicator series), `/v1/status`, OpenAPI docs, CORS, rate limit.
- [ ] Supabase JWT verification dependency (used later by protected routes) + a test with a fake token.
- [ ] Deploy `api` to Railway with env vars; confirm `/health` works on the public URL.
- [ ] GitHub Actions for backend lint + tests.

**Gate 1:** 2 years of 1h candles for the 5 coins are stored; `GET /v1/candles` returns candles with valid indicators on the Railway URL; tests pass.

---

## Phase 2 — Prediction engine v1 (weeks 3–5)  ← the most important gate

Goal: a model that is **measured honestly**.

- [ ] Feature builder (docs/03) with the no-leakage test.
- [ ] Baselines (`naive`, `always_up`) and the metrics module (accuracy, precision/recall, Brier, log loss, simulated return with fees, drawdown, Sharpe).
- [ ] Walk-forward splitter + tests.
- [ ] XGBoost training + calibration; model artifacts to Supabase Storage; `model_versions` rows.
- [ ] Backtest report generator (`backend/reports/…md`) for each asset/timeframe.
- [ ] `run_predictions` job (idempotent), `resolve_outcomes` job, `worker` service with APScheduler, advisory locks, heartbeat table updates.
- [ ] Deploy `worker` to Railway (one replica). Predictions appear in the database at every candle close.
- [ ] Notebook in `backend/notebooks/` that reproduces the report so Argy can read and learn from it.

**Gate 2 (decision point):** show Argy the report. Continue to Phase 3 only if the out-of-sample accuracy and Brier score beat the baselines with a margin that survives the bootstrap check **or** Argy explicitly decides to proceed with the honest result anyway (the track-record page will show it). If the model does not beat the baseline, spend extra time on features/data/validation first and re-run. Never tune on the test folds.

---

## Phase 3 — Web MVP (weeks 6–8)

Goal: a usable dashboard on Vercel.

- [ ] Scaffold `apps/web` (Next.js, TS strict, Tailwind, shadcn/ui, TanStack Query), theme with the brand: **TradeMatrix AI** + "Created by Argy" under it.
- [ ] Implement the design system from `docs/08-DESIGN.md` first (tokens, glass card, 3D buttons, orb with probability ring, signal card, tiles) and match the design canvas at 1440, 1024, 768 and 390 px (Playwright screenshots).
- [ ] Generate the typed API client from OpenAPI.
- [ ] Supabase Auth (email + Google), protected routes, session handling.
- [ ] Markets list page; coin detail page with `lightweight-charts` (candles, volume, EMA/Bollinger/RSI/MACD toggles from API data), timeframe switcher.
- [ ] Signal card with reasons, valid-until countdown, recent accuracy vs baseline, disclaimer.
- [ ] WebSocket client: live candle updates + new prediction events, reconnect logic.
- [ ] Track-record page; About page (how it works, disclaimer, brand line).
- [ ] Watchlist (login). Loading / empty / error states, mobile-responsive layout.
- [ ] Deploy to Vercel; CORS configured; Sentry added.
- [ ] Basic tests (vitest for utils/hooks) and a Playwright smoke test of the coin page.

**Gate 3:** the live site shows real signals and a live chart; signals are logged for 7 days with no missed runs; `/v1/status` shows fresh jobs.

---

## Phase 4 — Sentiment and alerts (weeks 9–10)

Goal: Gemini sentiment in **shadow mode**, plus alerts.

- [ ] `ingest_news` (RSS + CryptoPanic) with dedupe and asset keyword tagging.
- [ ] Gemini client (`google-genai`): JSON schema, temperature 0, validation, retry, budget guard, prompt versioning + tests with mocked and malformed responses.
- [ ] `score_sentiment` job; recency-weighted aggregation per asset; store `sentiment_agg` on predictions (`SENTIMENT_BLEND_K=0`).
- [ ] News list with sentiment badges on the coin page.
- [ ] Alerts: CRUD API, evaluation after each prediction + `check_price_alerts` every minute, cooldowns, `notifications` rows, in-app notification list on web.
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
