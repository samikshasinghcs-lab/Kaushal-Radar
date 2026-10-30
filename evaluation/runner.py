import json
from pathlib import Path
from evaluation.generate_cases import generate_cases
from evaluation.abstention import evaluate as eval_abstention
from evaluation.factual_accuracy import evaluate as eval_factual

def run_evaluation(dataset_path="evaluation/dataset.jsonl"):
    path = Path(dataset_path)

    if not path.exists():
        generate_cases(100, dataset_path)

    cases = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    results = []
    for case in cases:
        category = case["category"]
        expected = case["expected"]

        # Evaluate the labelled abstention behaviour.
        evidence = case["evidence"]
        if category == "missing":
            evidence = []

        abstention_result = eval_abstention(
            evidence, expected["abstain"]
        )

        results.append({
            "id": case["id"],
            "category": category,
            "abstention": abstention_result
        })

    summary = eval_factual(
        [x["abstention"]["actual"] for x in results],
        [x["abstention"]["expected"] for x in results]
    )

    return {
        "dataset": str(path),
        "synthetic_cases": len(cases),
        "abstention_test_accuracy": summary["accuracy"],
        "correct": summary["correct"],
        "total": summary["total"],
        "results": results,
        "interpretation": (
            "Synthetic harness result only; not an LLM accuracy score."
        )
    }

if __name__ == "__main__":
    result = run_evaluation()
    print(json.dumps(result, indent=2))
