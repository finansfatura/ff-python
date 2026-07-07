import unittest

from finansfatura import FinansfaturaClient, InsufficientCredits


class FakeResp:
    def __init__(self, status, payload=None, content=b""):
        self.status_code = status
        self._payload = payload
        self.content = content

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload

    @property
    def text(self):
        return "error"


class FakeSession:
    def __init__(self, resp):
        self.resp = resp
        self.calls = []

    def post(self, url, **kw):
        self.calls.append(("POST", url, kw))
        return self.resp

    def get(self, url, **kw):
        self.calls.append(("GET", url, kw))
        return self.resp


class TestClient(unittest.TestCase):
    def test_issue_sets_idempotency_header_and_returns_json(self):
        resp = FakeResp(200, {"invoice_id": "abc", "status": "QUEUED"})
        sess = FakeSession(resp)
        ff = FinansfaturaClient(api_key="ff_live_x", session=sess)

        out = ff.issue_invoice({"document_type": "EARSIV"}, idempotency_key="order-1")

        assert out["status"] == "QUEUED"
        method, url, kw = sess.calls[0]
        assert method == "POST" and url.endswith("/invoices/")
        assert kw["headers"]["X-Api-Key"] == "ff_live_x"
        assert kw["headers"]["Idempotency-Key"] == "order-1"

    def test_error_status_maps_to_typed_exception(self):
        resp = FakeResp(402, {"message": "insufficient credits"})
        ff = FinansfaturaClient(api_key="ff_live_x", session=FakeSession(resp))
        with self.assertRaises(InsufficientCredits) as ctx:
            ff.issue_invoice({}, idempotency_key="order-2")
        assert ctx.exception.status == 402

    def test_missing_idempotency_key_rejected_client_side(self):
        ff = FinansfaturaClient(api_key="ff_live_x", session=FakeSession(FakeResp(200, {})))
        with self.assertRaises(ValueError):
            ff.issue_invoice({}, idempotency_key="")

    def test_api_key_required(self):
        with self.assertRaises(ValueError):
            FinansfaturaClient(api_key="")


if __name__ == "__main__":
    unittest.main()
