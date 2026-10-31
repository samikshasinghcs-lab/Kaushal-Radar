import unittest

from ai.final_service import (
    generate_district_report,
    create_decision_summary,
    query_district
)


class TestFinalIntegration(unittest.TestCase):

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
            }
        ]

    def test_report_generation(self):

        report = generate_district_report(
            "Raichur",
            self.evidence
        )

        self.assertEqual(report["district"], "Raichur")

    def test_trust_validation(self):

        report = generate_district_report(
            "Raichur",
            self.evidence
        )

        self.assertTrue(
            report["trust_validation"]["validation_passed"]
        )

    def test_human_authority(self):

        report = generate_district_report(
            "Raichur",
            self.evidence
        )

        self.assertEqual(
            report["governance"]["decision_authority"],
            "HUMAN_OFFICER"
        )

    def test_summary_generation(self):

        report = generate_district_report(
            "Raichur",
            self.evidence
        )

        summary = create_decision_summary(report)

        self.assertEqual(summary["district"], "Raichur")

    def test_query(self):

        report = generate_district_report(
            "Raichur",
            self.evidence
        )

        result = query_district(
            "DGPI 2023-24",
            report
        )

        self.assertEqual(
            result["status"],
            "EVIDENCE_RETRIEVED"
        )

    def test_empty_district_rejected(self):

        with self.assertRaises(ValueError):
            generate_district_report("", self.evidence)

    def test_invalid_evidence_rejected(self):

        with self.assertRaises(TypeError):
            generate_district_report("Raichur", "invalid")

    def test_empty_evidence_abstains(self):

        report = generate_district_report("Raichur", [])

        self.assertEqual(
            report["status"],
            "INSUFFICIENT_EVIDENCE"
        )


if __name__ == "__main__":
    unittest.main()
