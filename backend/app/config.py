"""Settings loaded from environment variables (and the git-ignored .env for local work)."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    # Real environment variables win over the .env files, so Railway variables and
    # test overrides always take priority. Unknown variables are ignored because the
    # root .env also holds values for the web and mobile apps.
    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"

    # Supabase pooled connection string in SQLAlchemy form: postgresql+asyncpg://...
    database_url: str = ""
    supabase_url: str = ""
    supabase_jwks_url: str = ""
    supabase_jwt_secret: str = ""

    exchange: str = "binance"
    binance_rest_url: str = "https://data-api.binance.vision"
    binance_ws_url: str = "wss://data-stream.binance.vision"

    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def database_configured(self) -> bool:
        """False while the URL is empty or still holds the .env.example placeholders."""
        url = self.database_url
        return bool(url) and "PASSWORD" not in url and "PROJECT_REF" not in url


@lru_cache
def get_settings() -> Settings:
    return Settings()
