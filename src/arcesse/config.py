from __future__ import annotations

import os

DEFAULT_BACKEND_URL = "http://localhost:8191"
DEFAULT_TIMEOUT = 60000  # milliseconds

ENV_BACKEND_URL = "ARCESSE_BACKEND_URL"
ENV_TIMEOUT = "ARCESSE_TIMEOUT"


def resolve_backend_url(flag_value: str | None) -> str:
    """Resolve backend URL: CLI flag > env var > default."""
    if flag_value:
        return flag_value
    return os.environ.get(ENV_BACKEND_URL, DEFAULT_BACKEND_URL)


def resolve_timeout(flag_value: int | None) -> int:
    """Resolve timeout: CLI flag > env var > default."""
    if flag_value is not None:
        return flag_value
    env = os.environ.get(ENV_TIMEOUT)
    if env:
        return int(env)
    return DEFAULT_TIMEOUT
