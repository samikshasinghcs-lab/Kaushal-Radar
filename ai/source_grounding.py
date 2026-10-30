def verify_sources(claims, evidence):
    valid = {x["source"] for x in evidence}
    results = []
    for claim in claims:
        source = claim.get("source")
        results.append({
            "claim": claim,
            "grounded": source in valid
        })
    return results
