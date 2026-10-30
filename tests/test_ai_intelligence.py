import unittest

from ai.retrieval import retrieve
from ai.evidence_analyst import analyse
from ai.contradiction_analyst import analyse_contradictions
from ai.anomaly_explainer import explain_anomaly
from ai.uncertainty_explainer import explain_uncertainty
from ai.recommendation_explainer import explain_decision
from ai.policy_brief import generate_brief
from ai.natural_language_query import answer_question
from ai.source_grounding import verify_sources
from ai.numeric_guard import verify_numbers
from ai.hallucination_guard import validate_claims
from ai.abstention import should_abstain
from ai.privacy import detect_pii, reject_pii
from ai.audit_integration import record_ai_action


class TestAIIntelligence(unittest.TestCase):
    def setUp(self):
        self.data = [
            {
                "district": "Raichur",
                "indicator": "DGPI",
                "value": 4.03,
                "source": "synthetic_source",
                "period": "2022-23"
            }
        ]

    def test_retrieval(self):
        self.assertEqual(len(retrieve(self.data, "Raichur")), 1)

    def test_evidence_analysis(self):
        self.assertEqual(analyse(self.data)["status"], "EVIDENCE_AVAILABLE")

    def test_empty_evidence_abstains(self):
        self.assertEqual(analyse([])["status"], "INSUFFICIENT_EVIDENCE")

    def test_contradiction_detection(self):
        data = self.data + [{
            **self.data[0], "value": 5.0, "source": "second_source"
        }]
        self.assertEqual(len(analyse_contradictions(data)), 1)

    def test_no_false_contradiction(self):
        self.assertEqual(analyse_contradictions(self.data), [])

    def test_anomaly_explanation(self):
        result = explain_anomaly({
            "indicator": "DGPI",
            "observed_value": 4.03,
            "expected_value": 2.0,
            "method": "synthetic_test"
        })
        self.assertEqual(result["status"], "REQUIRES_REVIEW")

    def test_uncertainty_detection(self):
        result = explain_uncertainty([{
            **self.data[0], "stale": True
        }])
        self.assertEqual(result["status"], "UNCERTAINTY_PRESENT")

    def test_recommendation_requires_human(self):
        result = explain_decision("REVIEW", ["Evidence incomplete"])
        self.assertTrue(result["human_review_required"])

    def test_policy_brief(self):
        result = generate_brief("Raichur", self.data)
        self.assertEqual(result["district"], "Raichur")

    def test_natural_language_query(self):
        result = answer_question("Why is this district flagged?", self.data)
        self.assertEqual(result["mode"], "OFFLINE_RETRIEVAL")

    def test_source_grounding(self):
        result = verify_sources(
            [{"source": "synthetic_source"}], self.data
        )
        self.assertTrue(result[0]["grounded"])

    def test_numeric_guard(self):
        result = verify_numbers([{
            "indicator": "DGPI",
            "value": 4.03,
            "source": "synthetic_source"
        }], self.data)
        self.assertTrue(result[0]["valid"])

    def test_hallucination_rejection(self):
        result = validate_claims([{
            "indicator": "DGPI",
            "value": 999,
            "source": "invented_source"
        }], self.data)
        self.assertEqual(len(result["rejected"]), 1)

    def test_abstention(self):
        self.assertTrue(should_abstain([]))

    def test_pii_detection(self):
        self.assertIn("email", detect_pii("test@example.com"))

    def test_pii_rejection(self):
        with self.assertRaises(ValueError):
            reject_pii("Contact test@example.com")

    def test_audit_event(self):
        result = record_ai_action(
            "evidence", ["synthetic_source"], "passed"
        )
        self.assertTrue(result["human_review_required"])


if __name__ == "__main__":
    unittest.main()
