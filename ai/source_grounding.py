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
