"""HTTP client for the Finansfatura e-invoice API.

    from finansfatura import FinansfaturaClient, build_earsiv_payload

    ff = FinansfaturaClient(api_key="ff_live_...")
    payload = build_earsiv_payload(
        recipient={"vkn_tckn": "11111111111", "title": "Ahmet Yılmaz"},
        lines=[{"title": "Kulaklık", "qty": 1, "unit_price": 100.0, "vat_rate": 0.20}],
    )
    result = ff.issue_invoice(payload, idempotency_key="order-1042")
"""

from .errors import error_from_response

DEFAULT_BASE_URL = "https://api.finansfatura.com/v1/invoicing"


class FinansfaturaClient:
    """Thin wrapper over the invoicing endpoints. All calls send ``X-Api-Key``.

    Pass a custom ``session`` (any object exposing ``get``/``post`` like a
    ``requests.Session``) to reuse connections or to inject a fake in tests.
    """

    def __init__(self, api_key, base_url=DEFAULT_BASE_URL, timeout=15, session=None):
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        self.base = base_url.rstrip("/")
        self.timeout = timeout
        if session is None:
            import requests  # only needed for real HTTP; payload helpers stay dep-free
            session = requests.Session()
        self.session = session

    # -- internals ---------------------------------------------------------
    def _headers(self, extra=None):
        h = {"X-Api-Key": self.api_key, "Content-Type": "application/json"}
        if extra:
            h.update(extra)
        return h

    def _handle(self, resp):
        if resp.status_code >= 400:
            try:
                body = resp.json()
            except ValueError:
                body = resp.text
            raise error_from_response(resp.status_code, body)
        return resp

    # -- endpoints ---------------------------------------------------------
    def issue_invoice(self, payload, idempotency_key):
        """POST /invoices/ — issue a document. ``idempotency_key`` (any unique
        string, e.g. the order id) is required; retrying with the same key never
        double-issues."""
        if not idempotency_key:
            raise ValueError("idempotency_key is required")
        resp = self.session.post(
            f"{self.base}/invoices/",
            json=payload,
            headers=self._headers({"Idempotency-Key": str(idempotency_key)}),
            timeout=self.timeout,
        )
        return self._handle(resp).json()

    def get_invoice(self, invoice_id):
        """GET /invoices/:id — one invoice (poll here while status is QUEUED)."""
        resp = self.session.get(
            f"{self.base}/invoices/{invoice_id}",
            headers=self._headers(),
            timeout=self.timeout,
        )
        return self._handle(resp).json()

    def list_invoices(self, page=1):
        """GET /invoices/ — paginated list."""
        resp = self.session.get(
            f"{self.base}/invoices/",
            params={"page": page},
            headers=self._headers(),
            timeout=self.timeout,
        )
        return self._handle(resp).json()

    def download(self, invoice_id, fmt="pdf"):
        """GET /invoices/:id/download — raw document bytes (pdf|html|xml)."""
        resp = self.session.get(
            f"{self.base}/invoices/{invoice_id}/download",
            params={"format": fmt},
            headers=self._headers(),
            timeout=self.timeout,
        )
        return self._handle(resp).content

    def cancel(self, invoice_id):
        """POST /invoices/:id/cancel — cancel before GİB acceptance."""
        resp = self.session.post(
            f"{self.base}/invoices/{invoice_id}/cancel",
            headers=self._headers(),
            timeout=self.timeout,
        )
        self._handle(resp)
        return True
