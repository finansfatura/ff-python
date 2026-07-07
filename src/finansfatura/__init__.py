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
from .models import Line, Party
from .payload import build_earsiv_payload, build_efatura_payload, build_payload

__version__ = "0.1.1"

__all__ = [
    "FinansfaturaClient",
    "DEFAULT_BASE_URL",
    "Party",
    "Line",
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
