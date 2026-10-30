def evaluate(evidence, required_indicators):
    present = {x.get("indicator") for x in evidence}
    missing = sorted(set(required_indicators) - present)
    return {
        "missing": missing,
        "complete": not missing,
        "missing_count": len(missing)
    }
