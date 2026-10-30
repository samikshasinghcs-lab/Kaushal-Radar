def evaluate(claims, evidence):
    from ai.numeric_guard import verify_numbers
    results = verify_numbers(claims, evidence)
    total = len(results)
    valid = sum(x["valid"] for x in results)
    return {
        "accuracy": valid / total if total else None,
        "valid": valid,
        "invalid": total - valid,
        "total": total
    }
