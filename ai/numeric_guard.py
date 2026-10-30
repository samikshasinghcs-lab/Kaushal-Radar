def verify_numbers(claims, evidence):
    results = []
    for claim in claims:
        matches = [
            x for x in evidence
            if x["indicator"] == claim.get("indicator")
            and x["source"] == claim.get("source")
        ]
        valid = any(
            str(x["value"]) == str(claim.get("value"))
            for x in matches
        )
        results.append({"claim": claim, "valid": valid})
    return results
