"""Evidence-grounded district policy brief generator."""

from .district_intelligence import analyse_district
from .source_grounding import verify_claims
from .numeric_guard import validate_numeric_claims
from .uncertainty_explainer import explain_uncertainty


def generate_brief(district, evidence, expected_indicators=None):
    analysis = analyse_district(
        district,
        evidence,
        expected_indicators
    )

    grounding = verify_claims(analysis["claims"], evidence)
    numeric_checks = validate_numeric_claims(
        analysis["claims"], evidence
    )

    unsupported = [
        result for result in grounding if not result["grounded"]
    ]

    invalid_numbers = [
        result for result in numeric_checks if not result["valid"]
    ]

    uncertainty = explain_uncertainty(analysis)

    if unsupported or invalid_numbers:
        status = "VALIDATION_FAILED"
        summary = (
            "One or more claims failed source or numeric validation. "
            "Do not rely on this brief until the issue is resolved."
        )
    else:
        status = analysis["status"]
        if status == "INSUFFICIENT_EVIDENCE":
            summary = "Insufficient valid evidence for interpretation."
        elif analysis["contradictions"]:
            summary = (
                "Conflicting observations were detected. "
                "Officer verification is required."
            )
        elif analysis["missing_indicators"]:
            summary = (
                "Expected indicators are missing. "
                "The diagnostic picture is incomplete."
            )
        else:
            summary = (
                "Evidence is available for diagnostic review. "
                "It does not establish causation."
            )

    return {
        "title": f"District Diagnostic Brief: {district}",
        "district": district,
        "status": status,
        "executive_summary": summary,
        "findings": analysis["claims"],
        "source_validation": grounding,
        "numeric_validation": numeric_checks,
        "unsupported_claims": unsupported,
        "invalid_numeric_claims": invalid_numbers,
        "contradictions": analysis["contradictions"],
        "missing_indicators": analysis["missing_indicators"],
        "data_quality_warnings": analysis["warnings"],
        "uncertainty": uncertainty,
        "source_register": analysis["sources"],
        "human_review_required": (
            analysis["human_review_required"]
            or bool(unsupported)
            or bool(invalid_numbers)
            or uncertainty["human_review_required"]
        ),
        "decision_authority": "HUMAN_OFFICER",
        "ai_authority": "ADVISORY_ONLY",
        "limitations": analysis["limitations"],
    }
