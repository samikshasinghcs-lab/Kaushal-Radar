import json
from pathlib import Path
from html import escape

def save_report(results, directory="evaluation/reports"):
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)

    json_path = path / "evaluation_report.json"
    html_path = path / "evaluation_dashboard.html"

    json_path.write_text(
        json.dumps(results, indent=2, default=str),
        encoding="utf-8"
    )

    dimensions = results.get("results", {})

    rows = ""
    for name, result in dimensions.items():
        rows += (
            "<tr><td>" + escape(str(name)) +
            "</td><td><pre>" +
            escape(json.dumps(result, indent=2, default=str)) +
            "</pre></td></tr>"
        )

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kaushal Radar Evaluation Laboratory</title>
<style>
body {{font-family:Arial,sans-serif;background:#f2f4f8;padding:20px}}
main {{background:white;padding:22px;border-radius:12px}}
h1 {{color:#17345c}}
table {{width:100%;border-collapse:collapse}}
td,th {{padding:10px;border:1px solid #ddd;text-align:left;vertical-align:top}}
pre {{white-space:pre-wrap;overflow-wrap:anywhere}}
.badge {{background:#e7efff;padding:8px;border-radius:6px}}
</style>
</head>
<body>
<main>
<h1>Kaushal Radar — Evaluation Laboratory</h1>
<p class="badge">SYNTHETIC EVALUATION — NOT PRODUCTION ACCURACY</p>
<p>Dataset cases: {results.get("synthetic_cases", 0)}</p>
<p>Evaluation dimensions: {results.get("evaluation_dimensions", 0)}</p>
<h2>Results</h2>
<table>
<tr><th>Dimension</th><th>Evaluation output</th></tr>
{rows}
</table>
<h2>Limitations</h2>
<ul>
{''.join('<li>'+escape(str(x))+'</li>' for x in results.get('limitations', []))}
</ul>
</main>
</body>
</html>"""

    html_path.write_text(html_content, encoding="utf-8")

    return {
        "json": str(json_path),
        "html": str(html_path)
    }
