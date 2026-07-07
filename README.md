# finansfatura

Python client for the [Finansfatura](https://finansfatura.com) e-invoice API
(e-Fatura / e-Arşiv). Issue, list, download and cancel invoices with an API key —
no WooCommerce required, this is the general external REST API.

## Install

```bash
pip install finansfatura
```

## Quickstart

```python
import os
from finansfatura import FinansfaturaClient, build_earsiv_payload

ff = FinansfaturaClient(api_key=os.environ["FINANSFATURA_API_KEY"])  # ff_live_...

payload = build_earsiv_payload(
    recipient={"vkn_tckn": "11111111111", "title": "Ahmet Yılmaz",
               "email": "ahmet@example.com"},
    lines=[
        {"title": "Kablosuz Kulaklık", "product_code": "SKU-1042",
         "qty": 1, "unit_price": 100.0, "vat_rate": 0.20},
    ],
)

result = ff.issue_invoice(payload, idempotency_key="order-1042")
print(result["invoice_id"], result["status"])   # -> ... QUEUED
```

`build_earsiv_payload` computes totals from the lines (Decimal, no float drift)
and applies the API's exact field casing for you: the outer layer is snake_case
(`document_type`, `canonical`) but everything inside `canonical` is PascalCase
(`Recipient`, `Lines`, `Totals`, `VKNorTCKN`). A snake_case key inside `canonical`
is silently ignored by the server, so let the builder handle it.

## Idempotency

`idempotency_key` is **required** and can be any unique string (use your order
id). Retrying with the same key never double-issues — safe on timeout/retry.

## Reading & lifecycle

```python
ff.get_invoice(invoice_id)                 # poll while status is QUEUED
ff.list_invoices(page=1)
pdf_bytes = ff.download(invoice_id, "pdf")  # or "html" / "xml"
ff.cancel(invoice_id)                       # before GİB acceptance
```

## Errors

Failed calls raise a typed exception carrying `.status` and `.body`:

| Exception | HTTP | Meaning |
|-----------|------|---------|
| `AuthError` | 401 | key missing/invalid/revoked/expired |
| `InsufficientCredits` | 402 | not enough credits (kontör) |
| `ScopeError` | 403 | key lacks the required scope |
| `OnboardingRequired` | 412 | e-invoice onboarding not completed |
| `ProviderError` | 5xx | transient upstream — retry same idempotency key |
| `FinansfaturaError` | other | base class |

```python
from finansfatura import FinansfaturaError, OnboardingRequired

try:
    ff.issue_invoice(payload, idempotency_key=f"order-{order.id}")
except OnboardingRequired as e:
    ...  # e.body -> {"error_code": ..., "message": ...}
except FinansfaturaError as e:
    log.error("issue failed [%s]: %s", e.status, e.body)
```

## e-Fatura (registered recipients)

e-Arşiv targets final consumers (TCKN is fine). For a GİB-registered recipient
use e-Fatura, which needs the recipient's mailbox alias:

```python
from finansfatura import build_efatura_payload

payload = build_efatura_payload(
    recipient={"vkn_tckn": "1234567890", "title": "Kurum A.Ş."},
    lines=[...],
    recipient_alias="urn:mail:defaultpk@example.com",
)
```

## Notes

- Seller identity (`Issuer`) is filled server-side from your company profile —
  don't send it. Make sure the profile VKN is set, or issuing returns 503.
- Keep the API key in an env var; never commit it.

## Development

```bash
pip install -e ".[dev]"
python -m pytest        # or: python -m unittest discover tests
```

## License

MIT
