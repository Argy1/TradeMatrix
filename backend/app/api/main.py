"""FastAPI application. Run with: uv run uvicorn app.api.main:app --reload"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app import db
from app.api.errors import install_error_handlers
from app.config import get_settings

# About 60 requests per minute per IP on public endpoints (docs/04).
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="TradeMatrix AI API",
        version="0.1.0",
        description="Market data and probabilistic signals. Not financial advice.",
    )
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    install_error_handlers(app)

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
