"""Shared test setup."""

import os

import pytest

# Tests must never touch the real database or Supabase project. Environment variables win
# over the .env file, so emptying them here (before the app is imported) is enough.
os.environ["DATABASE_URL"] = ""
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_JWKS_URL"] = ""
os.environ["SUPABASE_JWT_SECRET"] = ""
os.environ["GEMINI_API_KEY"] = ""  # tests use a fake scorer; they must never call Gemini
os.environ["CORS_ORIGINS"] = "http://localhost:3000"
os.environ["STREAM_ENABLED"] = "false"


@pytest.fixture
async def session():
    """For tests marked `db` (run on purpose with `uv run pytest -m db`): a session on the REAL
    database inside one outer transaction that is always rolled back.

    A `session.commit()` made by the code under test only ends a savepoint inside that outer
    transaction, so it is rolled back with everything else and nothing is ever left behind.
    """
    # Imported here, after the variables above are set, like every other app import.
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.pool import NullPool

    from app.config import BACKEND_DIR, REPO_ROOT, Settings

    # DATABASE_URL is blanked above for normal tests, so read the .env files directly here.
    os.environ.pop("DATABASE_URL", None)
    settings = Settings(_env_file=(REPO_ROOT / ".env", BACKEND_DIR / ".env"))
    os.environ["DATABASE_URL"] = ""
    if not settings.database_configured:
        pytest.skip("DATABASE_URL is not configured")
    engine = create_async_engine(
        settings.database_url,
        poolclass=NullPool,
        connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0},
    )
    async with engine.connect() as connection:
        transaction = await connection.begin()
        yield AsyncSession(bind=connection, expire_on_commit=False)
        await transaction.rollback()
    await engine.dispose()
