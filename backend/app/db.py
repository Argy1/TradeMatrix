"""Async database engine for Supabase Postgres."""

from collections.abc import AsyncIterator
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.config import get_settings

_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine | None:
    """Return the shared engine, or None while DATABASE_URL is not filled in."""
    global _engine
    settings = get_settings()
    if not settings.database_configured:
        return None
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            # Supabase's pooler (port 6543) already pools connections, so we do not pool again.
            poolclass=NullPool,
            connect_args={
                # The pooler hands each transaction to a different server connection, so
                # prepared statements cannot be cached or reused by name.
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
                "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
                "timeout": 10,
            },
        )
    return _engine


def session_factory() -> async_sessionmaker[AsyncSession] | None:
    """A factory for sessions, or None while the database is not configured."""
    engine = get_engine()
    if engine is None:
        return None
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """One session for a unit of work (a request or a job run)."""
    factory = session_factory()
    if factory is None:
        raise RuntimeError("DATABASE_URL is not configured")
    async with factory() as session:
        yield session


async def ping() -> str:
    """'ok', 'down' or 'not_configured' for the health check."""
    engine = get_engine()
    if engine is None:
        return "not_configured"
    try:
        async with engine.connect() as connection:
            await connection.execute(text("select 1"))
    except (SQLAlchemyError, OSError, TimeoutError):
        return "down"
    return "ok"
