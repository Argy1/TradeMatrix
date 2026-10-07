"""FastAPI application. Run with: uv run uvicorn app.api.main:app --reload"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app import db
from app.api.account import router as account_router
from app.api.errors import install_error_handlers
from app.api.news import router as news_router
from app.api.signals import router as signals_router
from app.api.stream import hub
from app.api.stream import router as stream_router
from app.api.v1 import router as v1_router
from app.config import get_settings
from app.observability import init_sentry

# About 60 requests per minute per IP on public endpoints (docs/04).
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Start the live-stream hub with the server and stop it on shutdown."""
    settings = get_settings()
    if settings.stream_enabled:
        await hub.start(settings.binance_ws_url)
    yield
    await hub.stop()


def create_app() -> FastAPI:
    settings = get_settings()
    init_sentry("api")
    app = FastAPI(
        title="TradeMatrix AI API",
        version="0.1.0",
        description="Market data and probabilistic signals. Not financial advice.",
        lifespan=lifespan,
    )
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        # Vercel preview deployments get random URLs; this pattern allows only our own project.
        allow_origin_regex=settings.cors_origin_regex or None,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    install_error_handlers(app)
    app.include_router(v1_router)
    app.include_router(signals_router)
    app.include_router(news_router)
    app.include_router(stream_router)
    app.include_router(account_router)

    @app.get("/health", tags=["ops"])
    @limiter.exempt
    async def health(request: Request) -> JSONResponse:
        """Liveness plus a database check. Railway calls this to decide if the service is up."""
        database = await db.ping()
        healthy = database == "ok"
        return JSONResponse(
            status_code=200 if healthy else 503,
            content={"status": "ok" if healthy else "degraded", "database": database},
        )

    return app


app = create_app()
