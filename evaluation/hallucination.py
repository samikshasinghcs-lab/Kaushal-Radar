def evaluate(claims, evidence):
    from ai.hallucination_guard import validate_claims
    result = validate_claims(claims, evidence)
    total = len(claims)
    rejected = len(result["rejected"])
    return {
        "rejected_unsupported": rejected,
        "accepted": len(result["accepted"]),
        "total": total,
        "unsupported_rate": rejected / total if total else None
    }
