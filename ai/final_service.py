"""Kaushal Radar final integration service."""

from ai.master_pipeline import run_pipeline, answer_query
from ai.trust_layer import validate_ai_output


class ServiceError(Exception):
    pass


def generate_district_report(
    district,
    evidence,
    expected_indicators=None,
    anomaly_threshold=30.0
):
    if not isinstance(district, str) or not district.strip():
        raise ValueError("District is required.")

    if not isinstance(evidence, list):
        raise TypeError("Evidence must be a list.")

    report = run_pipeline(
        district=district,
        evidence=evidence,
        expected_indicators=expected_indicators or [],
        anomaly_threshold=anomaly_threshold
    )

    validation = validate_ai_output(report, evidence)

    report["trust_validation"] = validation

    report["system_health"] = {
        "pipeline_executed": True,
        "trust_validation_passed": validation["validation_passed"],
        "human_review_required": True,
        "deployment_status": "PROTOTYPE"
    }

    if not validation["validation_passed"]:
        report["status"] = "VALIDATION_FAILED"

    return report


def query_district(question, report):
    return answer_query(question, report)


def create_decision_summary(report):

    return {
        "district": report["district"],
        "status": report["status"],
        "evidence_count": report["evidence"]["evidence_count"],
        "missing_indicators": (
            report["evidence"]["missing_indicators"]
        ),
        "conflicts": report["evidence"]["conflicts"],
        "anomalies": report["anomalies"]["anomalies"],
        "uncertainty": report["uncertainty"],
        "trust_validation": report["trust_validation"],
        "decision_authority": "HUMAN_OFFICER",
        "ai_authority": "ADVISORY_ONLY",
        "automatic_funding_approval": False
    }


if __name__ == "__main__":
    import json

    # Synthetic demonstration data only.
    evidence = [
        {
            "indicator": "DGPI",
            "value": 2.50,
            "period": "2022-23",
            "source": "SYNTHETIC_SOURCE_A"
        },
        {
            "indicator": "DGPI",
            "value": 4.03,
            "period": "2023-24",
            "source": "SYNTHETIC_SOURCE_A"
        },
        {
            "indicator": "DGPI",
            "value": 3.80,
            "period": "2023-24",
            "source": "SYNTHETIC_SOURCE_B"
        }
    ]

    result = generate_district_report(
        "Synthetic Raichur",
        evidence,
        ["DGPI", "TRAINING", "PLACEMENT"]
    )

    print(json.dumps(create_decision_summary(result), indent=2))
