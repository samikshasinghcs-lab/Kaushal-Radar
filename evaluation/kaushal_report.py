"""Create reproducible JSON and Markdown evaluation reports."""

import json
from pathlib import Path

from evaluation.kaushal_runner import run_evaluation


def generate_report():

    report = run_evaluation()
    folder = Path("evaluation/reports")
    folder.mkdir(parents=True, exist_ok=True)

    (folder / "kaushal_evaluation.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

    lines = [
        "# Kaushal Radar Evaluation",
        "",
        "**Type:** Synthetic deterministic checks",
        "",
        f"- Cases: {report['total_cases']}",
        f"- Passed: {report['passed']}",
        f"- Failed: {report['failed']}",
        f"- Pass rate: {report['pass_rate']:.1%}",
        "",
        "| Category | Passed | Total |",
        "|---|---:|---:|"
    ]

    for name, values in report["categories"].items():
        lines.append(
            f"| {name} | {values['passed']} | {values['total']} |"
        )

    lines += ["", "## Limitations", ""]

    lines += [
        "- " + item for item in report["limitations"]
    ]

    (folder / "kaushal_evaluation.md").write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    return report


if __name__ == "__main__":
    result = generate_report()
    print("Report generated.")
    print("Cases:", result["total_cases"])
    print("Passed:", result["passed"])
    print("Failed:", result["failed"])
