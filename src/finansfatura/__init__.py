"""Finansfatura e-invoice API client."""

from .client import DEFAULT_BASE_URL, FinansfaturaClient
from .errors import (
    AuthError,
    FinansfaturaError,
    InsufficientCredits,
    OnboardingRequired,
    ProviderError,
    ScopeError,
)
from .payload import build_earsiv_payload, build_efatura_payload, build_payload

__version__ = "0.1.0"

__all__ = [
    "FinansfaturaClient",
    "DEFAULT_BASE_URL",
    "build_payload",
    "build_earsiv_payload",
    "build_efatura_payload",
    "FinansfaturaError",
    "AuthError",
    "InsufficientCredits",
    "ScopeError",
    "OnboardingRequired",
    "ProviderError",
    "__version__",
]
