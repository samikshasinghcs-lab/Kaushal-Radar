"""Explain evidence limitations and uncertainty."""


def explain_uncertainty(analysis):
    reasons = []

    if not analysis.get("evidence_count"):
        reasons.append("No valid evidence records were available.")

    if analysis.get("missing_indicators"):
        reasons.append(
            "Missing indicators: "
            + ", ".join(analysis["missing_indicators"])
        )

    if analysis.get("contradictions"):
        reasons.append(
            "Conflicting observations exist for one or more indicators."
        )

    if analysis.get("warnings"):
        reasons.extend(analysis["warnings"])

    stale_claims = [
        claim for claim in analysis.get("claims", [])
        if claim.get("evidence_status") == "STALE"
    ]

    if stale_claims:
        reasons.append("Some supplied evidence is marked stale.")

    return {
        "uncertain": bool(reasons),
        "reasons": reasons,
        "interpretation": (
            "Evidence is incomplete or requires verification."
            if reasons else
            "No specified data-quality warning was detected. "
            "This does not establish that the evidence is complete "
            "or factually correct."
        ),
        "human_review_required": bool(reasons),
    }


# Compatibility adapter for callers passing evidence records directly.
_explain_uncertainty_original = explain_uncertainty

def explain_uncertainty(analysis):
    if isinstance(analysis, list):
        records = analysis
        analysis = {
            "evidence_count": len(records),
            "evidence": records,
            "stale_evidence": [
                item for item in records
                if isinstance(item, dict) and item.get("stale") is True
            ],
            "missing_evidence": [],
            "warnings": [],
        }

    if not isinstance(analysis, dict):
        raise TypeError("analysis must be a dictionary or list of evidence records")

    return _explain_uncertainty_original(analysis)


# Ensure a consistent status field for downstream consumers.
_explain_uncertainty_with_adapter = explain_uncertainty

def explain_uncertainty(analysis):
    result = _explain_uncertainty_with_adapter(analysis)

    if not isinstance(result, dict):
        raise TypeError("Uncertainty analysis must return a dictionary")

    if "status" not in result:
        has_uncertainty = bool(
            result.get("stale_evidence")
            or result.get("missing_evidence")
            or result.get("warnings")
            or result.get("uncertainties")
        )
        result["status"] = (
            "UNCERTAINTY_PRESENT"
            if has_uncertainty
            else "NO_UNCERTAINTY_DETECTED"
        )

    return result


# Final correction: stale evidence must always be surfaced as uncertainty.
_previous_uncertainty_function = explain_uncertainty

def explain_uncertainty(analysis):
    result = _previous_uncertainty_function(analysis)

    if isinstance(analysis, list):
        stale_records = [
            item for item in analysis
            if isinstance(item, dict) and item.get("stale") is True
        ]
        if stale_records:
            result["status"] = "UNCERTAINTY_PRESENT"
            result["stale_evidence"] = stale_records

    return result
