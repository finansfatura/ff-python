"""Optional typed inputs for building payloads.

These are plain stdlib dataclasses (no third-party dep). Using them gives you
IDE autocomplete and an early error when a required field is missing, instead of
a silent KeyError deep in the builder or a server-side rejection.

They are optional: every builder also accepts plain dicts with the same keys, so
the quick path stays dict-based.

    from finansfatura import Party, Line, build_earsiv_payload

    payload = build_earsiv_payload(
        recipient=Party(vkn_tckn="11111111111", title="Ahmet Yılmaz"),
        lines=[Line(title="Kulaklık", qty=1, unit_price=100.0, vat_rate=0.20)],
    )
"""

from dataclasses import dataclass


@dataclass
class Party:
    """A buyer (recipient) or seller (issuer). ``vkn_tckn`` is required: 10-digit
    VKN for a company, 11-digit TCKN for an individual."""

    vkn_tckn: str
    title: str = ""
    address: str = ""
    tax_office: str = ""
    email: str = ""
    phone: str = ""


@dataclass
class Line:
    """One invoice line. ``unit_price`` is KDV-excl; ``vat_rate`` is a decimal
    ratio (0.20 == %20)."""

    title: str
    qty: float
    unit_price: float
    vat_rate: float
    product_code: str = ""
    unit_code: str = "C62"
