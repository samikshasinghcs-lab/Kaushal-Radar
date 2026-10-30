def evaluate(evidence, expected_conflict):
    from ai.contradiction_analyst import analyse_contradictions
    detected = bool(analyse_contradictions(evidence))
    return {
        "expected": bool(expected_conflict),
        "detected": detected,
        "correct": detected == bool(expected_conflict)
    }
