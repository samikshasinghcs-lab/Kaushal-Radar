"""Generate 120 reproducible synthetic evaluation cases."""

import json
from pathlib import Path


def generate_cases():

    categories = [
        "factual",
        "numeric",
        "hallucination",
        "source_attribution",
        "contradiction",
        "missing_data",
        "stale_data",
        "abstention",
        "robustness",
        "injection"
    ]

    cases = []

    for category in categories:
        for index in range(12):

            cases.append({
                "case_id": f"{category.upper()}_{index + 1:03d}",
                "category": category,
                "synthetic": True,
                "input": {
                    "indicator": "DGPI",
                    "value": 4.03,
                    "source": "SYNTHETIC_SOURCE_A",
                    "period": "2023-24",
                    "stale": False
                }
            })

    return cases


def save_dataset(path="evaluation/kaushal_eval_dataset.jsonl"):

    cases = generate_cases()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    with target.open("w", encoding="utf-8") as file:
        for case in cases:
            file.write(json.dumps(case) + "\n")

    return len(cases)


if __name__ == "__main__":
    print("Generated:", save_dataset(), "synthetic cases.")
