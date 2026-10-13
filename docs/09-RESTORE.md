# 09 — Progress record and how to restore

*Created by Argy*

Written on 2026-10-13, right after the fast candle sizes went live. Two purposes:

1. One page that says what is done and what is not.
2. A guide for the day something is deleted: the Railway project, the Supabase database, or both.

Rule for this file: every command here is one that was really run in this project, unless the line says "not tested". Keep it that way when you change it.

---

## 1. Progress on 2026-10-13

| Phase | State | What is still open |
| --- | --- | --- |
| 0 Setup | Done. Gate 0 passed 2026-10-03 | nothing |
| 1 Foundations (candles, API, Railway) | Done. Gate 1 passed 2026-10-03 | the roadmap still lists "GitHub Actions for backend" as open: the workflow files exist (`.github/workflows/backend.yml`, `web.yml`, `mobile.yml`), their runs on GitHub were never checked |
| 2 Prediction engine | Done. Gate 2 passed 2026-10-03 by Argy's decision | nothing |
| 3 Website | Done. Gate 3 passed 2026-10-09 by Argy's decision (6.0 of 7 days) | nothing |
| 4 Sentiment and alerts | Deployed 2026-10-09. **Gate 4 open** | `--clear-json` clean-up; Argy's signed-in check of the alerts pages; sentiment evaluation notebook (needs 4 weeks of data, from about 2026-11-06); optional email alerts |
| 5 Mobile app | Built 2026-10-10. **Gate 5 open** | push notifications (needs a Firebase project); Google sign-in (needs an OAuth client); test on a real phone; signed-in screens on real data |
| 5b Fast candle sizes | **Live since 2026-10-13.** Gates 5b-1 and 5b-2 passed 2026-10-11; 5b-4 passed for the website | Gate 5b-3: 24 hours live, until 2026-10-14 16:03 UTC, not checked yet; the app on a phone; **Supabase still on the Free plan** (database full about 2026-10-22) |
| 6 Hardening and launch | Not started | everything in docs/05, Phase 6 |

What runs today:

- **Website:** https://tradematrix-rho.vercel.app (Vercel project `tradematrix`, deploys on every push to `main`).
- **API:** https://api-production-a829.up.railway.app (Railway project `tradematrix`, service `api`).
- **Worker:** Railway service `worker`, exactly one replica. Hourly run for 1h/4h/1d at :00:05, fast run for 1m to 30m every minute at second :01, news every 15 minutes, Gemini sentiment (shadow mode, `k = 0`), price alerts every minute, daily counts every hour, clean-up of fast rows older than 90 days.
- **App:** APK 0.2.0 (`com.argy.tradematrix`), built on Argy's PC, not in a store.
- **Models:** 128 active: 48 for 1h/4h/1d and 80 for the fast sizes.
- **Database on 2026-10-13:** 184 MB. 5,682 signals since 2026-10-03, 5,554 results, 608 daily-count rows, 16 coins, 1 user, no alerts or watchlists yet.

Other open items that belong to no phase:

- Rotate the secrets that were pasted into chat earlier (Gemini key, database password, Supabase secret key). The Railway variables must change at the same moment.
- Retrain the fast models about every two weeks (section 7).
- The pooled 1d model gives every coin the same probability (flagged `degraded`).
- **There is no backup of the live track record** (section 8).

---

## 2. Where everything lives

| Thing | Where | Second copy | If it is lost |
| --- | --- | --- | --- |
| Code, migrations, docs, backtest reports | GitHub `Argy1/TradeMatrix` (private), branch `main` | Argy's PC | Clone again. Nothing is lost while one copy exists |
| Database: tables, coins, candles, signals, results, daily counts, news, model register | Supabase project `TradeMatrix` (ref `hoanadzkysksfvgimukn`, Singapore) | **none** | Schema, coins and candles can be rebuilt. Signals and results cannot (section 3) |
| User accounts, watchlists, alerts | Same Supabase project (Auth and tables) | **none** | Gone. People sign up again |
| Model files (65 files) | Supabase Storage, private bucket `models` | none | Train again (section 7). The new models are not identical to the old ones |
| API and worker | Railway project `tradematrix`, services `api` and `worker` | built from `backend/` in git | Recreate and deploy (section 4). Railway keeps no data |
| Website | Vercel project `tradematrix`, root `apps/web` | built from git | Recreate, set 5 values, deploy |
| Secret values | `.env` in the repo root on Argy's PC (git-ignored), and the Railway variables | each is a copy of the other | Create new ones in each provider's dashboard (section 6) |
| Public build values | `apps/web/.env.local`, `apps/mobile/dart_defines.json` (git-ignored), Vercel settings | each other | Read again from the Supabase dashboard |
| Training history of the fast sizes | `backend/data/history/` on Argy's PC, 80 files, about 540 MB (git-ignored) | none | Download again: about 30 minutes |
| APK files | `apps/mobile/build/app/outputs/flutter-apk/` on Argy's PC | the copy on Argy's phone | Build again: about 2 minutes |
| Error reports | Sentry | none | Not needed to run |

---

## 3. What can be rebuilt and what cannot

**Can be rebuilt from git and from the exchange:**

- The whole schema, with row-level security and the 16 coins: the six files in `supabase/migrations/`.
- All candles. Binance serves the full history again.
- All models, by training again. Settings are frozen in `backend/app/ml/config.py`, so no tuning is needed.
- Railway services, the Vercel project, the APK.

**Cannot be rebuilt:**

- **The live signals and their results** (`predictions`, `prediction_outcomes`) and the daily counts made from them (`signal_stats_daily`). This is the live track record since 2026-10-03, the proof of how the models really did. A signal that was not stored at its minute can never be made honestly afterwards.
- User accounts, watchlists, alert rules, notifications.
- Stored headlines and their Gemini scores. New headlines arrive again; old ones do not.
- Which model version made which old signal (`model_versions` history).

After a full database loss the product works again within about an hour of work, but its track record starts at zero and the page must say so. Do not fill the gap with backtest numbers (rule 1).

---

## 4. Railway is deleted, the database is fine

Nothing is lost except the signals of the minutes and hours the worker was away. Those stay missing; candles are caught up by themselves.

1. Create a Railway project `tradematrix`, region **Singapore** (asia-southeast1). The exchange rejects US addresses and the database is in Singapore.
2. Create two services in it, both built from `backend/Dockerfile`, one replica each:

   | Service | Start command | Health check | Restart |
   | --- | --- | --- | --- |
   | `api` | the Dockerfile's own command (uvicorn) | `/health`, 60 s | on failure, max 5 |
   | `worker` | `python -m app.worker.main` | none | always |

   The worker must never have more than one replica.
3. Set the variables. Names per service (values come from the root `.env`):

   - `api`: `APP_ENV`, `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_JWKS_URL`, `EXCHANGE`, `BINANCE_REST_URL`, `BINANCE_WS_URL`, `CORS_ORIGINS`, `CORS_ORIGIN_REGEX`, `SENTRY_DSN`
   - `worker`: `APP_ENV`, `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `EXCHANGE`, `BINANCE_REST_URL`, `BINANCE_WS_URL`, `SENTRY_DSN`

   `CORS_ORIGINS` on `api` must contain the website's address, or the browser blocks every request. A secret can be set without showing it on screen: pipe the value into `railway variables --service worker --set-from-stdin NAME` (Railway CLI 4.40; newer versions call it `railway variable set NAME --stdin`).
4. Deploy from `backend/`, the API first:

   ```bash
   railway up --service api --detach
   ```

   ```bash
   railway up --service worker --detach
   ```

5. The API gets a **new address**. Put it in four places and release each:
   - Vercel: `NEXT_PUBLIC_API_BASE_URL` (https) and `NEXT_PUBLIC_WS_URL` (wss), then redeploy the website.
   - `apps/mobile/lib/config.dart` (the two default values) and `apps/mobile/dart_defines.example.json`, then build a new APK.
   - `apps/web/package.json`, script `api:types`.
   - `CLAUDE.md` and `backend/README.md`.
6. Check with section 9.

At start the worker loads every candle it missed, the model files and the newest candles. Give it about a minute.

---

## 5. The database (Supabase project) is deleted, Railway is fine

Read section 3 first: the live track record is gone.

1. **New project.** Create a Supabase project in Singapore (`ap-southeast-1`). Creating or paying for it is Argy's step. Write its URL, database password and keys into the root `.env`.
2. **Schema.** Apply the six migrations in file-name order. They were applied through the Supabase connector one by one (`apply_migration`, then the `version` in `supabase_migrations.schema_migrations` set to the file's timestamp). `npx supabase db push --db-url <session pooler URL>` should do the same in one step; that path is **not tested**. Afterwards there must be 13 tables with row-level security, 16 rows in `assets` and a private Storage bucket `models`.
3. **Auth.** In the dashboard, Authentication, URL Configuration: set the Site URL to the website's address. Email sign-in is the only method in use.
4. **Candles for the slow sizes**, from `backend/` (the models train on history since September 2020):

   ```bash
   uv run python -m app.data.backfill --timeframes 1h,4h,1d --since 2020-09-01
   ```

5. **Candles for the fast sizes** (about 1,500 to 2,900 per coin and size, 2 minutes):

   ```bash
   uv run python -m app.data.backfill --timeframes 1m,3m,5m,15m,30m
   ```

6. **Models** (section 7): train the slow ones, then the fast ones. Training also writes the files to the `models` bucket and registers them.
7. **Point everything at the new project:**
   - Railway, both services: `DATABASE_URL`, `SUPABASE_URL`; `api` also `SUPABASE_JWKS_URL`; `worker` also `SUPABASE_SERVICE_ROLE_KEY`. Then deploy both (section 4, step 4), the worker between two hourly runs.
   - Vercel: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, then redeploy.
   - `apps/web/.env.local` and `apps/mobile/dart_defines.json`, then build a new APK.
   - `CLAUDE.md`: the project ref.
8. Check with section 9. The track record page is empty until signals have results; the hourly `summarize_signals` job fills `signal_stats_daily` by itself.

Time: about an hour of work, most of it waiting for the first backfill and the training.

---

## 6. Everything is gone except GitHub

1. Clone the repository. Install the tools from `README.md` (git, Node, `uv`, Flutter, Railway CLI).
2. Copy `.env.example` to `.env` and fill it. Where each value comes from:

   | Value | Where to get it |
   | --- | --- |
   | `DATABASE_URL` | Supabase, Connect, transaction pooler (port 6543), written as `postgresql+asyncpg://...` |
   | `SUPABASE_URL`, `SUPABASE_JWKS_URL` | Supabase project URL; the second is that URL plus `/auth/v1/.well-known/jwks.json` |
   | `SUPABASE_SERVICE_ROLE_KEY` | Supabase, API keys, the secret key. Server only, never in the website or the app |
   | `NEXT_PUBLIC_SUPABASE_ANON_KEY`, mobile `SUPABASE_ANON_KEY` | Supabase, API keys, the publishable key |
   | `GEMINI_API_KEY` | Google AI Studio. `GEMINI_MODEL=gemini-3.8-flash` (approved 2026-10-03; check Google's model list before changing) |
   | `BINANCE_REST_URL`, `BINANCE_WS_URL` | the two market-data hosts already written in `.env.example` |
   | `SENTRY_DSN`, `NEXT_PUBLIC_SENTRY_DSN` | Sentry. Optional: empty means off |

3. Do section 5 (database), then section 4 (Railway).
4. Vercel: project with root `apps/web`, the five `NEXT_PUBLIC_*` values, connected to the GitHub repository so that a push to `main` deploys.
5. `uv run scripts/gate0_check.py` from the repo root checks the database, the exchange and the Gemini key in one go.

---

## 7. Training the models again

All from `backend/`. Slow models read candles from the database; fast models read the history files.

Slow sizes (not timed; expect several minutes):

```bash
uv run python -m app.ml.train_models --timeframes 1h,4h,1d
```

Fast sizes. First the history files, about 30 minutes for a first download, seconds for an update:

```bash
uv run python -m app.data.history
```

Then train, about 15 minutes:

```bash
uv run python -m app.ml.train_models --timeframes 1m,3m,5m,15m,30m
```

Then deploy the worker so it loads the new files (between two hourly runs):

```bash
railway up --service worker --detach
```

Each model is evaluated again while it is trained and gets `ok` or `degraded` from that evaluation. The numbers will differ a little from the ones in `backend/reports/`, because the data ends later. Nothing is tuned: the settings stay as chosen in `config.py`.

---

## 8. Backups: what exists and what is missing

- **Nothing in this project is backed up automatically today.** The Supabase Free plan keeps no backups.
- Supabase Pro keeps daily backups for a limited number of days (check the number in the dashboard). They help after a mistake inside the project. They do not help if the project itself is deleted.
- **Missing: an export of the tables that cannot be rebuilt** (`predictions`, `prediction_outcomes`, `signal_stats_daily`, `model_versions`, and the user tables) to a file outside Supabase, together with a tested way to load it back. Until that exists, section 3 is the honest answer to "what happens if the database is deleted".
- The smallest useful protection is `signal_stats_daily` alone: a few hundred small rows that hold the whole track record as counts.

---

## 9. Check after a restore

1. `https://<api>/health` answers `ok`.
2. `https://<api>/v1/status`: every job has a recent "last success", no "last error", and all eight sizes are fresh.
3. A signal for the current minute exists. In the Supabase SQL editor:

   ```sql
   select timeframe, count(*), max(target_open_time),
          round(avg(extract(epoch from (created_at - target_open_time)))::numeric, 1) as seconds_after_close
   from predictions where target_open_time > now() - interval '10 minutes' group by 1;
   ```

   Expect 16 signals per closed 1m candle, stored about 2 seconds after the close.
4. The website shows a chart and a signal for BTC on 1m and on 1h, and the 1m card changes by itself after each minute.
5. From `backend/`: `uv run pytest` (241 tests) and `uv run pytest -m db` (24 tests against the real tables, everything rolled back).
