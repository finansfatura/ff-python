"""Helpers that build the two-layer issue payload with the exact field casing
the API expects.

Gotcha the API imposes: the outer layer is snake_case (``document_type``,
``canonical``) but everything inside ``canonical`` is PascalCase (``Recipient``,
``Lines``, ``Totals``, ``VKNorTCKN`` …). A snake_case key inside ``canonical`` is
silently ignored. These builders encode that so callers never get it wrong.

Totals are computed from the lines with :class:`~decimal.Decimal` to avoid float
kuruş drift; ``LineTotal`` is the KDV-excl net used verbatim by the server.
"""

from decimal import Decimal


def _party(p):
    return {
        "VKNorTCKN": p["vkn_tckn"],
        "Title": p.get("title", ""),
        "Address": p.get("address", ""),
        "TaxOffice": p.get("tax_office", ""),
        "Email": p.get("email", ""),
        "Phone": p.get("phone", ""),
    }


def _lines_and_totals(lines):
    canon = []
    subtotal = Decimal("0")
    vat_total = Decimal("0")
    for l in lines:
        qty = Decimal(str(l["qty"]))
        unit = Decimal(str(l["unit_price"]))
        rate = Decimal(str(l["vat_rate"]))  # 0.20 == %20
        line_net = (qty * unit).quantize(Decimal("0.01"))
        subtotal += line_net
        vat_total += (line_net * rate).quantize(Decimal("0.01"))
        canon.append({
            "Title": l["title"],
            "ProductCode": l.get("product_code", ""),
            "Quantity": float(qty),
            "UnitPrice": float(unit),
            "UnitCode": l.get("unit_code", "C62"),
            "VatRate": float(rate),
            "LineTotal": float(line_net),
        })
    totals = {
        "SubtotalExclVAT": float(subtotal),
        "VatTotal": float(vat_total),
        "DiscountTotal": 0,
        "GrandTotal": float(subtotal + vat_total),
    }
    return canon, totals


def build_payload(document_type, recipient, lines, *, issuer=None,
                  recipient_alias=None, invoice_type_code="SATIS", note=None):
    """Generic builder. ``recipient``/``issuer`` are dicts with ``vkn_tckn`` +
    optional ``title``/``address``/``tax_office``/``email``/``phone``. ``lines``
    are dicts with ``title``/``qty``/``unit_price``/``vat_rate`` (+ optional
    ``product_code``/``unit_code``).

    Do NOT pass ``issuer`` in production — the server fills seller identity from
    the company profile. It exists only for testing before the profile VKN is set.
    """
    canon_lines, totals = _lines_and_totals(lines)
    canonical = {
        "DocumentType": document_type,
        "InvoiceTypeCode": invoice_type_code,
        "Currency": "TRY",
        "Recipient": _party(recipient),
        "Lines": canon_lines,
        "Totals": totals,
    }
    if issuer is not None:
        canonical["Issuer"] = _party(issuer)
    if recipient_alias:
        canonical["RecipientAlias"] = recipient_alias
    if note:
        canonical["Note"] = note
    return {"document_type": document_type, "canonical": canonical}


def build_earsiv_payload(recipient, lines, **kwargs):
    """e-Arşiv (final consumer / non-registered recipient — TCKN is fine)."""
    return build_payload("EARSIV", recipient, lines, **kwargs)


def build_efatura_payload(recipient, lines, recipient_alias, **kwargs):
    """e-Fatura (GİB-registered recipient). ``recipient_alias`` is required — the
    mailbox handle GİB routes by (resolve it via a recipient lookup first)."""
    return build_payload("EFATURA", recipient, lines,
                         recipient_alias=recipient_alias, **kwargs)
