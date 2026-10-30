def evaluate(evidence):
    stale = [
        x.get("indicator") for x in evidence
        if x.get("stale", False)
    ]
    return {
        "stale_indicators": stale,
        "stale_count": len(stale),
        "requires_review": bool(stale)
    }
