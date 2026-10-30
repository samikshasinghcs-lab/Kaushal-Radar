import json
from pathlib import Path

def generate_cases(count=100, output=None):
    if count < 1:
        raise ValueError("count must be positive")

    cases = []
    categories = [
        "factual", "numeric", "hallucination", "source",
        "contradiction", "missing", "stale", "abstention",
        "robustness", "clean"
    ]

    for i in range(count):
        category = categories[i % len(categories)]
        cases.append({
            "id": f"SYN-{i+1:03d}",
            "category": category,
            "synthetic": True,
            "district": f"Synthetic District {i % 31 + 1}",
            "evidence": [{
                "indicator": "DGPI",
                "value": round(1.0 + (i % 50) / 10, 2),
                "source": "SYNTHETIC_SOURCE_A",
                "period": "2022-23"
            }],
            "expected": {
                "abstain": category in ("missing", "stale", "abstention"),
                "source_valid": category not in ("source", "hallucination"),
                "numeric_valid": category != "numeric",
                "contradiction": category == "contradiction"
            }
        })

    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for case in cases:
                f.write(json.dumps(case) + "\n")

    return cases

if __name__ == "__main__":
    generate_cases(100, "evaluation/dataset.jsonl")
    print("Generated 100 labelled synthetic cases.")
