"""
Kaushal Radar — Integrated District Intelligence Engine.

Combines evidence diagnostics and deterministic anomaly detection.
This system is advisory: final decisions belong to human officers.
"""

from ai.district_intelligence import analyse_district
from ai.anomaly_explainer import analyse_anomalies


def run_district_intelligence(
    district,
    evidence,
    expected_indicators=None,
    anomaly_threshold=30.0
):
    """
    Run the district intelligence pipeline.

    Parameters
    ----------
    district : str
        District name.
    evidence : list[dict]
        Observations containing indicator, value, period and source.
    expected_indicators : list[str]
        Indicators expected in the district assessment.
    anomaly_threshold : float
        Percentage-change threshold for anomaly investigation.

    Returns
    -------
    dict
        Combined diagnostic report.
    """

    if not isinstance(district, str) or not district.strip():
        raise ValueError("A valid district name is required.")

    if not isinstance(evidence, list):
        raise TypeError("Evidence must be a list.")

    if not isinstance(anomaly_threshold, (int, float)):
        raise TypeError("Anomaly threshold must be numeric.")

    if anomaly_threshold < 0:
        raise ValueError("Anomaly threshold cannot be negative.")

    expected_indicators = expected_indicators or []

    # 1. Evidence intelligence
    district_report = analyse_district(
        district=district,
        evidence=evidence,
        expected_indicators=expected_indicators
    )

    # 2. Anomaly intelligence
    anomaly_report = analyse_anomalies(
        observations=evidence,
        change_threshold=anomaly_threshold
    )

    # 3. Consolidate warnings
    warnings = (
        district_report.get("warnings", [])
        + anomaly_report.get("warnings", [])
    )

    # 4. Consolidate investigation triggers
    investigation_required = bool(
        district_report.get("contradictions")
        or district_report.get("missing_indicators")
        or anomaly_report.get("anomalies")
        or warnings
    )

    # 5. Construct the integrated report
    return {
        "system": "KAUSHAL_RADAR",
        "module": "DISTRICT_INTELLIGENCE_ENGINE",
        "district": district,

        "overall_status": (
            "HUMAN_INVESTIGATION_REQUIRED"
            if investigation_required
            else district_report.get("status", "REVIEW_REQUIRED")
        ),

        "evidence_intelligence": district_report,

        "anomaly_intelligence": anomaly_report,

        "summary": {
            "evidence_records": district_report.get(
                "evidence_count", 0
            ),
            "claims_generated": len(
                district_report.get("claims", [])
            ),
            "missing_indicators": district_report.get(
                "missing_indicators", []
            ),
            "conflicting_observations": district_report.get(
                "contradictions", []
            ),
            "anomalies_detected": len(
                anomaly_report.get("anomalies", [])
            ),
            "warnings": warnings
        },

        "governance": {
            "human_review_required": investigation_required,
            "decision_authority": "HUMAN_OFFICER",
            "ai_authority": "ADVISORY_ONLY",
            "automatic_policy_decisions": False
        },

        "limitations": [
            "Anomaly detection identifies unusual changes, not their causes.",
            "Conflicting values require source-definition reconciliation.",
            "Source labels are not independent proof of authenticity.",
            "Missing data can limit the reliability of conclusions.",
            "The system does not independently verify official datasets."
        ]
    }


if __name__ == "__main__":
    import json

    # Synthetic demonstration data — NOT official Karnataka data.
    sample_evidence = [
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
        },
        {
            "indicator": "TRAINING",
            "value": 1200,
            "period": "2023-24",
            "source": "SYNTHETIC_SOURCE_C",
            "stale": True
        }
    ]

    report = run_district_intelligence(
        district="Synthetic Raichur",
        evidence=sample_evidence,
        expected_indicators=[
            "DGPI",
            "TRAINING",
            "PLACEMENT"
        ]
    )

    print(json.dumps(report, indent=2))
