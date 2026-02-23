class ArcesseError(Exception):
    """Base exception for all arcesse errors."""


class BackendError(ArcesseError):
    """The backend returned an error response."""


class BackendUnavailableError(ArcesseError):
    """Cannot reach the backend service."""


class ChallengeFailedError(ArcesseError):
    """The Cloudflare challenge could not be solved."""
