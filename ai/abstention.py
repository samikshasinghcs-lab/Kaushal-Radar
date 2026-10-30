def should_abstain(evidence, minimum=1):
    if len(evidence) < minimum:
        return True
    return any(
        x.get("stale", False) or x.get("valid", True) is False
        for x in evidence
    )
