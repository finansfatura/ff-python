"""Typed exceptions for the Finansfatura API.

Every failed HTTP call raises a :class:`FinansfaturaError` (or a subclass) that
carries the HTTP ``status`` and the parsed ``body`` so callers can branch on the
kind of failure with ``except`` instead of inspecting status codes by hand.
"""


class FinansfaturaError(Exception):
    def __init__(self, status, body, message=None):
        self.status = status
        self.body = body
        super().__init__(message or f"[{status}] {body}")


class AuthError(FinansfaturaError):
    """401 — API key missing, invalid, revoked or expired."""


class InsufficientCredits(FinansfaturaError):
    """402 — not enough credits (kontör) to issue the document."""


class ScopeError(FinansfaturaError):
    """403 — the API key lacks the required scope (e.g. invoice:write)."""


class OnboardingRequired(FinansfaturaError):
    """412 — e-invoice onboarding not completed. Body carries error_code/message."""


class ProviderError(FinansfaturaError):
    """5xx — gateway/provider or transient upstream failure. Safe to retry with
    the same Idempotency-Key."""


_BY_STATUS = {
    401: AuthError,
    402: InsufficientCredits,
    403: ScopeError,
    412: OnboardingRequired,
}


def error_from_response(status, body):
    cls = _BY_STATUS.get(status)
    if cls is None:
        cls = ProviderError if status >= 500 else FinansfaturaError
    return cls(status, body)
