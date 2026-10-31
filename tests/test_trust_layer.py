import unittest

from ai.master_pipeline import run_pipeline
from ai.trust_layer import (
    verify_claims,
    validate_numeric_claims,
    detect_unsupported_claims,
    validate_district_report,
    redact_pii,
    assess_sufficiency,
    validate_ai_output
)


class TestTrustLayer(unittest.TestCase):

    def setUp(self):

        self.evidence = [
            {
                "indicator": "DGPI",
                "value": 4.03,
                "period": "2023-24",
                "source": "SOURCE_A"
            }
        ]

        self.claims = [
            {
                "indicator": "DGPI",
                "value": 4.03,
                "period": "2023-24",
                "source": "SOURCE_A"
            }
        ]

    def test_valid_claim_grounded(self):
        result = verify_claims(self.claims, self.evidence)
        self.assertTrue(result["passed"])

    def test_invented_value_rejected(self):
        claim = [dict(self.claims[0], value=99)]
        result = verify_claims(claim, self.evidence)
        self.assertFalse(result["passed"])

    def test_numeric_integrity(self):
        result = validate_numeric_claims(
            self.claims,
            self.evidence
        )
        self.assertTrue(result["passed"])

    def test_hallucination_guard(self):
        claim = [dict(self.claims[0], value=999)]
        result = detect_unsupported_claims(
            claim,
            self.evidence
        )
        self.assertTrue(
            result["hallucination_risk_detected"]
        )

    def test_report_schema(self):
        report = run_pipeline("Raichur", self.evidence)
        result = validate_district_report(report)
        self.assertTrue(result["valid"])

    def test_pii_redaction(self):
        result = redact_pii(
            "Contact test@example.com"
        )
        self.assertTrue(result["pii_detected"])
        self.assertNotIn(
            "test@example.com",
            result["redacted_text"]
        )

    def test_clean_text(self):
        result = redact_pii("Raichur district report")
        self.assertFalse(result["pii_detected"])

    def test_abstention_on_missing_evidence(self):
        result = assess_sufficiency(
            [],
            expected_indicators=["DGPI"]
        )
        self.assertTrue(result["abstain"])

    def test_conflicts_trigger_abstention(self):
        result = assess_sufficiency(
            self.evidence,
            conflicts=[{"indicator": "DGPI"}]
        )
        self.assertTrue(result["abstain"])

    def test_unified_validation(self):
        report = run_pipeline("Raichur", self.evidence)
        result = validate_ai_output(report, self.evidence)
        self.assertTrue(result["validation_passed"])


if __name__ == "__main__":
    unittest.main()
