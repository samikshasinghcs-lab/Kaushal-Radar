"""Check numeric claims against evidence without recalculating indicators."""


def validate_numeric_claims(claims, evidence):
    results = []

    for claim in claims:
        matches = [
            item for item in evidence
            if item.get("indicator") == claim.get("indicator")
            and item.get("source") == claim.get("source")
            and item.get("period") == claim.get("period")
        ]

        valid = any(
            item.get("value") == claim.get("value")
            for item in matches
        )

        results.append({
            "indicator": claim.get("indicator"),
            "claimed_value": claim.get("value"),
            "valid": valid,
            "reason": (
                "Value matches supplied evidence."
                if valid else "Value does not match supplied evidence."
            )
        })

    return results


def verify_numbers(claims, evidence):
    """Backward-compatible interface for the original AI modules."""
    result = validate_numeric_claims(claims, evidence)

    return {
        "accepted": result["valid_numeric_claims"],
        "rejected": result["invalid_numeric_claims"],
        "passed": result["passed"]
    }


def verify_numbers(claims, evidence):
    """Return one numeric validation result per claim."""

    results = []

    for claim in claims:
        valid = False

        if isinstance(claim, dict):
            for item in evidence:
                if not isinstance(item, dict):
                    continue

                if (
                    claim.get("indicator") == item.get("indicator")
                    and claim.get("value") == item.get("value")
                    and claim.get("period") == item.get("period")
                ):
                    valid = True
                    break

        results.append({"valid": valid})

    return results


# Compatibility implementation: evidence matching is not official verification.
def verify_numbers(claims, evidence):
    results = []
    for claim in claims:
        matched = False
        value = claim.get("value")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            for item in evidence:
                if (
                    item.get("indicator") == claim.get("indicator")
                    and isinstance(item.get("value"), (int, float))
                    and not isinstance(item.get("value"), bool)
                    and item.get("value") == value
                    and (
                        "source" not in claim
                        or item.get("source") == claim.get("source")
                    )
                    and (
                        "period" not in claim
                        or item.get("period") == claim.get("period")
                    )
                ):
                    matched = True
                    break

        results.append({
            **claim,
            "valid": matched,
            "evidence_match": matched,
            "verification_status": (
                "MATCHED_SYNTHETIC_EVIDENCE"
                if matched and "synthetic" in str(claim.get("source", "")).lower()
                else "MATCHED_EVIDENCE"
                if matched
                else "UNVERIFIED"
            ),
        })
    return results
