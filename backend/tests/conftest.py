"""Shared test setup."""

import os

# Tests must never touch the real database or Supabase project. Environment variables win
# over the .env file, so emptying them here (before the app is imported) is enough.
os.environ["DATABASE_URL"] = ""
os.environ["SUPABASE_URL"] = ""
os.environ["SUPABASE_JWKS_URL"] = ""
os.environ["SUPABASE_JWT_SECRET"] = ""
os.environ["GEMINI_API_KEY"] = ""  # tests use a fake scorer; they must never call Gemini
os.environ["CORS_ORIGINS"] = "http://localhost:3000"
os.environ["STREAM_ENABLED"] = "false"
