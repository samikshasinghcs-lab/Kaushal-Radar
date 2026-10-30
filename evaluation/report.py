import json
from pathlib import Path
from html import escape

def save_report(results, directory="evaluation/reports"):
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)

    json_path = path / "evaluation_report.json"
    html_path = path / "evaluation_dashboard.html"

    json_path.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8"
    )

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Kaushal Radar Evaluation</title>
      <style>
        body {{ font-family: Arial; margin: 35px; background: #f3f5f9; }}
        main {{ background: white; padding: 25px; border-radius: 12px; }}
        h1 {{ color: #14294b; }}
        .metric {{ font-size: 24px; font-weight: bold; }}
        pre {{ white-space: pre-wrap; }}
      </style>
    </head>
    <body>
    <main>
      <h1>Kaushal Radar Evaluation Laboratory</h1>
      <p>Dataset: SYNTHETIC TEST CASES</p>
      <p class="metric">Cases: {results["synthetic_cases"]}</p>
      <p>Abstention test accuracy:
      {results["abstention_test_accuracy"]}</p>
      <p>Correct: {results["correct"]} / {results["total"]}</p>
      <p>{escape(results["interpretation"])}</p>
      <h2>Individual results</h2>
      <pre>{escape(json.dumps(results["results"], indent=2))}</pre>
    </main>
    </body>
    </html>
    """

    html_path.write_text(html_content, encoding="utf-8")
    return {"json": str(json_path), "html": str(html_path)}
