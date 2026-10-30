def evaluate(predictions, expected):
    total = min(len(predictions), len(expected))
    if total == 0:
        return {"accuracy": None, "correct": 0, "total": 0}

    correct = sum(
        predictions[i] == expected[i] for i in range(total)
    )
    return {
        "accuracy": correct / total,
        "correct": correct,
        "total": total
    }
