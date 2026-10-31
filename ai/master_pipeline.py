"""
KAUSHAL RADAR — Unified Intelligence Pipeline.

Deterministic, evidence-grounded decision-support foundation.
No external LLM is assumed or falsely represented as connected.
"""

from collections import defaultdict
from numbers import Real
from datetime import datetime


class EvidenceError(ValueError):
    pass


def validate_evidence(evidence):
    if not isinstance(evidence, list):
        raise EvidenceError("Evidence must be a list.")

    valid = []
    warnings = []

    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            warnings.append(f"Record {index}: invalid structure.")
            continue

        indicator = item.get("indicator")
        value = item.get("value")
        period = item.get("period")
        source = item.get("source")

        if not all([indicator, period, source]):
            warnings.append(f"Record {index}: missing metadata.")
            continue

        if isinstance(value, bool) or not isinstance(value, Real):
            warnings.append(f"Record {index}: invalid numeric value.")
            continue

        valid.append({
            "indicator": str(indicator),
            "value": float(value),
            "period": str(period),
            "source": str(source),
            "stale": bool(item.get("stale", False))
        })

    return valid, warnings


def analyse_evidence(evidence, expected_indicators=None):
    valid, warnings = validate_evidence(evidence)

    grouped = defaultdict(list)

    for item in valid:
        grouped[(item["indicator"], item["period"])].append(item)

    conflicts = []

    for (indicator, period), records in grouped.items():
        values = sorted(set(x["value"] for x in records))

        if len(values) > 1:
            conflicts.append({
                "indicator": indicator,
                "period": period,
                "observations": [
                    {
                        "value": x["value"],
                        "source": x["source"]
                    }
                    for x in records
                ],
                "status": "UNRESOLVED_SOURCE_DISAGREEMENT"
            })

    available = sorted(set(x["indicator"] for x in valid))

    missing = [
        x for x in (expected_indicators or [])
        if x not in available
    ]

    stale = [x for x in valid if x["stale"]]

    return {
        "evidence_count": len(valid),
        "indicators_available": available,
        "missing_indicators": missing,
        "conflicts": conflicts,
        "stale_observations": stale,
        "warnings": warnings,
        "sources": sorted(set(x["source"] for x in valid)),
        "validated_evidence": valid
    }


def analyse_anomalies(evidence, threshold=30.0):
    if isinstance(threshold, bool) or not isinstance(threshold, Real):
        raise ValueError("Threshold must be numeric.")

    if threshold < 0:
        raise ValueError("Threshold cannot be negative.")

    grouped = defaultdict(list)

    for item in evidence:
        if not item["stale"]:
            grouped[item["indicator"]].append(item)

    anomalies = []
    warnings = []

    for indicator, records in grouped.items():
        records.sort(key=lambda x: x["period"])

        if len(records) < 2:
            continue

        for previous, current in zip(records, records[1:]):
            if previous["source"] != current["source"]:
                warnings.append(
                    f"{indicator}: comparison uses different sources."
                )

            old = previous["value"]
            new = current["value"]
            difference = new - old

            percentage = (
                None if old == 0
                else difference / abs(old) * 100
            )

            if percentage is not None and abs(percentage) >= threshold:
                anomalies.append({
                    "indicator": indicator,
                    "previous_period": previous["period"],
                    "current_period": current["period"],
                    "previous_value": old,
                    "current_value": new,
                    "absolute_change": round(difference, 4),
                    "percentage_change": round(percentage, 2),
                    "source_previous": previous["source"],
                    "source_current": current["source"],
                    "status": "INVESTIGATION_REQUIRED"
                })

    return {
        "threshold_percentage": float(threshold),
        "anomalies": anomalies,
        "warnings": warnings
    }


def build_uncertainty(evidence_report, anomaly_report):
    reasons = []

    if not evidence_report["evidence_count"]:
        reasons.append("No valid evidence supplied.")

    if evidence_report["missing_indicators"]:
        reasons.append("Expected indicators are missing.")

    if evidence_report["conflicts"]:
        reasons.append("Sources contain unresolved disagreements.")

    if evidence_report["stale_observations"]:
        reasons.append("Some observations are marked stale.")

    if evidence_report["warnings"]:
        reasons.append("Some evidence records failed validation.")

    if anomaly_report["warnings"]:
        reasons.append("Some comparisons have source differences.")

    if anomaly_report["anomalies"]:
        reasons.append("Unusual changes require investigation.")

    return {
        "uncertainty_present": bool(reasons),
        "reasons": reasons,
        "human_review_required": bool(reasons)
    }


def generate_claims(evidence_report):
    claims = []

    for item in evidence_report["validated_evidence"]:
        claims.append({
            "claim": (
                f"{item['indicator']} was {item['value']} "
                f"for {item['period']}."
            ),
            "indicator": item["indicator"],
            "value": item["value"],
            "period": item["period"],
            "source": item["source"],
            "status": (
                "STALE" if item["stale"]
                else "SOURCE_RECORDED"
            )
        })

    return claims


def generate_policy_brief(district, report):
    evidence = report["evidence"]
    anomalies = report["anomalies"]
    uncertainty = report["uncertainty"]

    return {
        "title": f"District Diagnostic Brief: {district}",
        "district": district,
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "evidence_summary": {
            "records": evidence["evidence_count"],
            "indicators": evidence["indicators_available"],
            "sources": evidence["sources"]
        },
        "key_findings": report["claims"],
        "conflicting_observations": evidence["conflicts"],
        "anomalies": anomalies["anomalies"],
        "missing_indicators": evidence["missing_indicators"],
        "uncertainty": uncertainty,
        "recommended_verification": (
            "Verify source definitions, reporting periods, "
            "denominators and data quality before policy action."
        ),
        "decision_authority": "HUMAN_OFFICER",
        "ai_authority": "ADVISORY_ONLY"
    }


def answer_query(question, report):
    """
    Conservative natural-language query interface.
    Retrieves supplied evidence; does not pretend to be an LLM.
    """

    if not isinstance(question, str) or not question.strip():
        raise ValueError("A question is required.")

    terms = question.lower().split()
    matches = []

    for claim in report["claims"]:
        searchable = (
            claim["indicator"] + " " + claim["period"]
        ).lower()

        if any(term in searchable for term in terms):
            matches.append(claim)

    if not matches:
        return {
            "status": "INSUFFICIENT_MATCHING_EVIDENCE",
            "answer": (
                "No matching evidence was found in the supplied records."
            ),
            "claims": [],
            "human_review_required": True
        }

    return {
        "status": "EVIDENCE_RETRIEVED",
        "answer": "The following supplied observations match your query.",
        "claims": matches,
        "human_review_required": True
    }


def run_pipeline(
    district,
    evidence,
    expected_indicators=None,
    anomaly_threshold=30.0
):
    if not isinstance(district, str) or not district.strip():
        raise ValueError("A valid district is required.")

    evidence_report = analyse_evidence(
        evidence,
        expected_indicators
    )

    anomaly_report = analyse_anomalies(
        evidence_report["validated_evidence"],
        anomaly_threshold
    )

    uncertainty = build_uncertainty(
        evidence_report,
        anomaly_report
    )

    claims = generate_claims(evidence_report)

    status = (
        "INSUFFICIENT_EVIDENCE"
        if not evidence_report["evidence_count"]
        else (
            "HUMAN_REVIEW_REQUIRED"
            if uncertainty["uncertainty_present"]
            else "EVIDENCE_AVAILABLE"
        )
    )

    report = {
        "system": "KAUSHAL_RADAR",
        "district": district,
        "status": status,
        "evidence": evidence_report,
        "anomalies": anomaly_report,
        "uncertainty": uncertainty,
        "claims": claims,
        "governance": {
            "human_review_required": True,
            "decision_authority": "HUMAN_OFFICER",
            "ai_authority": "ADVISORY_ONLY",
            "automatic_funding_approval": False
        }
    }

    report["policy_brief"] = generate_policy_brief(
        district,
        report
    )

    return report
