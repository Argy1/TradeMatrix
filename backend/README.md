# TradeMatrix AI backend

*Created by Argy*

One Python package that runs as two services: the **API** (FastAPI) and, from Phase 2, the **worker**.

## Run it

```bash
uv sync                                        # install the pinned dependencies (uv.lock)
uv run uvicorn app.api.main:app --reload       # API on http://localhost:8000, docs at /docs
uv run pytest                                  # tests (fake exchange, no network)
uv run pytest -m live                          # one real call to the exchange
uv run ruff check . && uv run ruff format .    # lint and format
```

Settings come from environment variables, or from the git-ignored `.env` in the repo root
(see `.env.example`). Tests never read the real database: `tests/conftest.py` empties those variables.

## What is where

| Path | Purpose |
| --- | --- |
| `app/config.py` | Settings (pydantic-settings) |
| `app/db.py` | Async SQLAlchemy engine for the Supabase pooler (`statement_cache_size=0`) |
| `app/timeframes.py` | The supported candle sizes: 1h, 4h, 1d |
| `app/data/exchanges/` | `ExchangeClient` interface and the Binance market-data client |
| `app/data/quality.py` | Candle checks: duplicates, gaps, impossible values |
| `app/features/indicators.py` | SMA, EMA, RSI, MACD, Bollinger Bands, ATR, ADX, OBV |
| `app/api/main.py` | FastAPI app: CORS, rate limit, error shape, `/health` |
| `app/api/auth.py` | Supabase JWT verification for protected routes |
| `tests/` | One test file per module |

## Deploy (Railway)

The `api` service builds `backend/Dockerfile` (settings in `backend/railway.toml`) and runs in Singapore,
close to the Supabase database. Variables are set on the service, never committed.

```bash
railway up --service api --ci     # from backend/: upload, build and deploy
railway logs --service api        # read the logs
```

Public URL: https://api-production-a829.up.railway.app (`/health`, `/docs`, `/v1/...`).
