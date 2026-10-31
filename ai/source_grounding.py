"""Verify claims against supplied evidence records."""


def verify_claims(claims, evidence):
    results = []

    for claim in claims:
        matches = [
            item for item in evidence
            if item.get("indicator") == claim.get("indicator")
            and item.get("value") == claim.get("value")
            and item.get("source") == claim.get("source")
            and item.get("period") == claim.get("period")
        ]

        results.append({
            "claim": claim,
            "grounded": bool(matches),
            "matched_source": matches[0].get("source") if matches else None,
            "reason": (
                "Exact evidence record found."
                if matches else "No matching evidence record."
            )
        })

    return results


def verify_sources(claims, evidence):
    """Return one source-grounding result per claim."""

    results = []

    for claim in claims:
        grounded = False

        if isinstance(claim, dict):
            for item in evidence:
                if not isinstance(item, dict):
                    continue

                if (
                    claim.get("indicator") == item.get("indicator")
                    and claim.get("value") == item.get("value")
                    and claim.get("source") == item.get("source")
                    and claim.get("period") == item.get("period")
                ):
                    grounded = True
                    break

        results.append({"grounded": grounded})

    return results


# Compatibility implementation: source matching is not source authentication.
def verify_sources(claims, evidence):
    available = {
        str(item.get("source", "")).strip()
        for item in evidence
        if item.get("source")
    }

    results = []
    for claim in claims:
        source = str(claim.get("source", "")).strip()
        grounded = bool(source) and source in available

        results.append({
            **claim,
            "grounded": grounded,
            "evidence_match": grounded,
            "verification_status": (
                "MATCHED_SYNTHETIC_SOURCE"
                if grounded and "synthetic" in source.lower()
                else "MATCHED_SOURCE"
                if grounded
                else "UNVERIFIED"
            ),
        })
    return results
