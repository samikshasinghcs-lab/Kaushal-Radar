def evaluate(evidence, expected_abstention):
    from ai.abstention import should_abstain
    actual = should_abstain(evidence)
    expected = bool(expected_abstention)
    return {
        "expected": expected,
        "actual": actual,
        "correct": expected == actual
    }
