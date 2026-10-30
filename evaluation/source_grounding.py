def evaluate(claims, evidence):
    from ai.source_grounding import verify_sources
    results = verify_sources(claims, evidence)
    total = len(results)
    valid = sum(x["grounded"] for x in results)
    return {
        "grounded": valid,
        "ungrounded": total - valid,
        "total": total,
        "rate": valid / total if total else None
    }
