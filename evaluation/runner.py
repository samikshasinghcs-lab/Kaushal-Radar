import json
from pathlib import Path

from evaluation.factual_accuracy import evaluate as factual
from evaluation.numeric_accuracy import evaluate as numeric
from evaluation.hallucination import evaluate as hallucination
from evaluation.source_grounding import evaluate as grounding
from evaluation.contradiction import evaluate as contradiction
from evaluation.missing_data import evaluate as missing
from evaluation.stale_data import evaluate as stale
from evaluation.abstention import evaluate as abstention
from evaluation.robustness import evaluate as robustness
from evaluation.regression import compare


def run_evaluation(dataset_path="evaluation/dataset.jsonl"):
    path = Path(dataset_path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    cases = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not cases:
        raise ValueError("Evaluation dataset is empty.")

    # Explicitly synthetic fixtures.
    evidence = [{
        "district": "Synthetic Raichur",
        "indicator": "DGPI",
        "value": 4.03,
        "source": "SYNTHETIC_SOURCE_A",
        "period": "2022-23"
    }]

    valid_claim = {
        "indicator": "DGPI",
        "value": 4.03,
        "source": "SYNTHETIC_SOURCE_A"
    }

    unsupported_claim = {
        "indicator": "DGPI",
        "value": 999,
        "source": "INVENTED_SOURCE"
    }

    conflict_evidence = evidence + [{
        **evidence[0],
        "value": 5.0,
        "source": "SYNTHETIC_SOURCE_B"
    }]

    stale_evidence = [{
        **evidence[0],
        "stale": True
    }]

    from security.input_validation import validate_request

    results = {
        "factual_accuracy": factual(
            [valid_claim], [valid_claim]
        ),

        "numeric_accuracy": numeric(
            [valid_claim, unsupported_claim], evidence
        ),

        "hallucination": hallucination(
            [valid_claim, unsupported_claim], evidence
        ),

        "source_grounding": grounding(
            [valid_claim, unsupported_claim], evidence
        ),

        "contradiction": contradiction(
            conflict_evidence, True
        ),

        "missing_data": missing(
            evidence, ["DGPI", "TRAINING"]
        ),

        "stale_data": stale(stale_evidence),

        "abstention": {
            "empty_evidence": abstention([], True),
            "stale_evidence": abstention(stale_evidence, True),
            "valid_evidence": abstention(evidence, False)
        },

        "robustness": robustness(
            validate_request,
            ["valid question", "", None, "x" * 1001]
        ),

        "regression": compare(
            {"accuracy": 0.90, "grounding": 0.90},
            {"accuracy": 0.95, "grounding": 0.95}
        )
    }

    return {
        "dataset": str(path),
        "synthetic_cases": len(cases),
        "evaluation_dimensions": len(results),
        "results": results,
        "limitations": [
            "All evaluation fixtures are synthetic.",
            "No real government dataset was evaluated.",
            "No connected LLM was evaluated.",
            "Factual accuracy measures fixture matching, not semantic truth.",
            "Regression uses demonstration baselines, not historical model runs."
        ]
    }


if __name__ == "__main__":
    from evaluation.report import save_report

    result = run_evaluation()

    print(json.dumps(result, indent=2))
    print("\nREPORTS:")
    print(save_report(result))
