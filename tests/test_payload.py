import unittest

from finansfatura import build_earsiv_payload, build_efatura_payload


class TestPayload(unittest.TestCase):
    def test_earsiv_casing_and_totals(self):
        p = build_earsiv_payload(
            recipient={"vkn_tckn": "11111111111", "title": "Ahmet"},
            lines=[
                {"title": "A", "qty": 2, "unit_price": 100.0, "vat_rate": 0.20},
                {"title": "B", "qty": 1, "unit_price": 50.0, "vat_rate": 0.20},
            ],
        )
        # outer layer snake_case, canonical PascalCase
        assert p["document_type"] == "EARSIV"
        c = p["canonical"]
        assert c["DocumentType"] == "EARSIV"
        assert c["Recipient"]["VKNorTCKN"] == "11111111111"
        # 2*100 + 1*50 = 250 net, 20% KDV = 50, grand 300
        assert c["Totals"]["SubtotalExclVAT"] == 250.0
        assert c["Totals"]["VatTotal"] == 50.0
        assert c["Totals"]["GrandTotal"] == 300.0
        assert c["Lines"][0]["LineTotal"] == 200.0
        # Issuer must NOT be present unless explicitly injected
        assert "Issuer" not in c

    def test_issuer_injection_and_efatura_alias(self):
        p = build_efatura_payload(
            recipient={"vkn_tckn": "1234567801", "title": "Kurum"},
            lines=[{"title": "X", "qty": 1, "unit_price": 10.0, "vat_rate": 0.20}],
            recipient_alias="urn:mail:defaultpk@example.com",
            issuer={"vkn_tckn": "1234567801", "title": "Satici"},
        )
        c = p["canonical"]
        assert c["DocumentType"] == "EFATURA"
        assert c["RecipientAlias"] == "urn:mail:defaultpk@example.com"
        assert c["Issuer"]["VKNorTCKN"] == "1234567801"


if __name__ == "__main__":
    unittest.main()
