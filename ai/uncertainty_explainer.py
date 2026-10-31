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
