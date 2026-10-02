# API image for Railway, built from the backend/ folder.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1

# Dependencies first: this layer is reused when only the code changes, so deploys are faster.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev

COPY app ./app
ENV PATH="/app/.venv/bin:$PATH"

# Railway sets $PORT. --proxy-headers lets the rate limiter see the real client IP
# behind Railway's proxy instead of the proxy's own address.
CMD ["sh", "-c", "uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips '*'"]
