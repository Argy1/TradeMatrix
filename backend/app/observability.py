"""Error tracking with Sentry. Off until SENTRY_DSN is set (locally and in tests it stays off)."""

import sentry_sdk

from app.config import get_settings


def init_sentry(component: str) -> bool:
    """Start Sentry for the "api" or "worker" service. Returns True when it is on."""
    settings = get_settings()
    if not settings.sentry_dsn:
        return False
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.app_env,
        traces_sample_rate=0.1,  # 10% of requests: enough to see slow endpoints on the free plan
        send_default_pii=False,  # never send IPs, headers with tokens, or emails
    )
    sentry_sdk.set_tag("component", component)
    return True
