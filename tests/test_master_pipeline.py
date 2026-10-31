import unittest

from ai.master_pipeline import (
    run_pipeline,
    answer_query,
    analyse_anomalies
)


class TestMasterPipeline(unittest.TestCase):

    def setUp(self):
        self.evidence = [
            {
                "indicator": "DGPI",
                "value": 2.50,
                "period": "2022-23",
                "source": "SOURCE_A"
            },
            {
                "indicator": "DGPI",
                "value": 4.03,
                "period": "2023-24",
                "source": "SOURCE_A"
            },
            {
                "indicator": "DGPI",
                "value": 3.80,
                "period": "2023-24",
                "source": "SOURCE_B"
            }
        ]

    def test_pipeline_returns_report(self):
        result = run_pipeline("Raichur", self.evidence)
        self.assertEqual(result["district"], "Raichur")

    def test_detects_conflicting_sources(self):
        result = run_pipeline("Raichur", self.evidence)
        self.assertEqual(len(result["evidence"]["conflicts"]), 1)

    def test_detects_missing_indicators(self):
        result = run_pipeline(
            "Raichur",
            self.evidence,
            ["DGPI", "PLACEMENT"]
        )
        self.assertIn(
            "PLACEMENT",
            result["evidence"]["missing_indicators"]
        )

    def test_detects_anomaly(self):
        result = run_pipeline("Raichur", self.evidence)
        self.assertGreaterEqual(
            len(result["anomalies"]["anomalies"]), 1
        )

    def test_human_authority_is_preserved(self):
        result = run_pipeline("Raichur", self.evidence)
        self.assertEqual(
            result["governance"]["decision_authority"],
            "HUMAN_OFFICER"
        )

    def test_empty_evidence_abstains(self):
        result = run_pipeline("Raichur", [])
        self.assertEqual(result["status"], "INSUFFICIENT_EVIDENCE")

    def test_query_retrieves_matching_claim(self):
        result = run_pipeline("Raichur", self.evidence)
        answer = answer_query("DGPI 2023-24", result)
        self.assertEqual(answer["status"], "EVIDENCE_RETRIEVED")

    def test_query_rejects_empty_question(self):
        result = run_pipeline("Raichur", self.evidence)
        with self.assertRaises(ValueError):
            answer_query("", result)

    def test_negative_threshold_rejected(self):
        with self.assertRaises(ValueError):
            analyse_anomalies(self.evidence, -1)

    def test_invalid_district_rejected(self):
        with self.assertRaises(ValueError):
            run_pipeline("", self.evidence)


if __name__ == "__main__":
    unittest.main()
