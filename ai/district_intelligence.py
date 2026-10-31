"""Evidence-grounded district intelligence for Kaushal Radar.

This module does not invent official statistics or make policy decisions.
"""

from collections import defaultdict
from numbers import Real


def analyse_district(district, evidence, expected_indicators=None):
    if not isinstance(district, str) or not district.strip():
        raise ValueError("A valid district name is required.")

    if not isinstance(evidence, list):
        raise TypeError("Evidence must be a list.")

    expected_indicators = expected_indicators or []

    valid = []
    warnings = []
    missing = []
    contradictions = []
    grouped = defaultdict(list)

    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            warnings.append(f"Evidence item {index} is malformed.")
            continue

        indicator = item.get("indicator")
        value = item.get("value")
        source = item.get("source")
        period = item.get("period")

        if not indicator or value is None or not source or not period:
            warnings.append(
                f"Evidence item {index} has missing required fields."
            )
            continue

        if isinstance(value, bool) or not isinstance(value, Real):
            warnings.append(
                f"{indicator}: value is not a valid numeric observation."
            )
            continue

        record = {
            "indicator": str(indicator),
            "value": float(value),
            "source": str(source),
            "period": str(period),
            "stale": bool(item.get("stale", False)),
        }

        valid.append(record)
        grouped[(record["indicator"], record["period"])].append(record)

        if record["stale"]:
            warnings.append(
                f"{indicator}: evidence for {period} is marked stale."
            )

    for indicator in expected_indicators:
        if not any(x["indicator"] == indicator for x in valid):
            missing.append(indicator)

    for (indicator, period), records in grouped.items():
        distinct_values = {x["value"] for x in records}

        if len(distinct_values) > 1:
            contradictions.append({
                "indicator": indicator,
                "period": period,
                "observations": [
                    {
                        "value": x["value"],
                        "source": x["source"],
                    }
                    for x in records
                ],
                "reason": "Different sources report different values "
                          "for the same indicator and period.",
            })

    sources = list(dict.fromkeys(x["source"] for x in valid))

    if not valid:
        status = "INSUFFICIENT_EVIDENCE"
    elif missing or warnings or contradictions:
        status = "REVIEW_REQUIRED"
    else:
        status = "EVIDENCE_AVAILABLE"

    claims = [
        {
            "claim": (
                f"{x['indicator']} is recorded as {x['value']} "
                f"for period {x['period']}."
            ),
            "indicator": x["indicator"],
            "value": x["value"],
            "period": x["period"],
            "source": x["source"],
            "evidence_status": (
                "STALE" if x["stale"] else "SOURCE_RECORDED"
            ),
        }
        for x in valid
    ]

    return {
        "district": district,
        "status": status,
        "evidence_count": len(valid),
        "claims": claims,
        "sources": sources,
        "contradictions": contradictions,
        "missing_indicators": missing,
        "warnings": warnings,
        "human_review_required": status != "EVIDENCE_AVAILABLE",
        "decision_authority": "HUMAN_OFFICER",
        "limitations": [
            "Evidence interpretation does not establish causation.",
            "No official status or funding decision is generated.",
            "Source values must be independently verified.",
        ],
    }
