"""
Kaushal Radar — Evidence Intelligence Layer.

Produces source-grounded evidence summaries.
Does not invent explanations or automatically resolve conflicts.
"""

from collections import defaultdict
from numbers import Real


def analyse_evidence(district, observations, expected_indicators=None):

    if not isinstance(district, str) or not district.strip():
        raise ValueError("District name is required.")

    if not isinstance(observations, list):
        raise TypeError("Observations must be a list.")

    expected_indicators = expected_indicators or []

    grouped = defaultdict(list)
    warnings = []
    claims = []
    sources = set()

    for index, item in enumerate(observations):

        if not isinstance(item, dict):
            warnings.append(f"Record {index}: invalid record.")
            continue

        indicator = item.get("indicator")
        value = item.get("value")
        period = item.get("period")
        source = item.get("source")

        if not indicator or not period or not source:
            warnings.append(
                f"Record {index}: missing indicator, period or source."
            )
            continue

        if isinstance(value, bool) or not isinstance(value, Real):
            warnings.append(
                f"{indicator}: invalid numeric value."
            )
            continue

        record = {
            "indicator": str(indicator),
            "value": float(value),
            "period": str(period),
            "source": str(source),
            "stale": bool(item.get("stale", False))
        }

        grouped[(record["indicator"], record["period"])].append(record)
        sources.add(record["source"])

        claims.append({
            "statement": (
                f"{district}: {record['indicator']} was "
                f"{record['value']} in {record['period']}."
            ),
            "indicator": record["indicator"],
            "value": record["value"],
            "period": record["period"],
            "source": record["source"],
            "evidence_status": (
                "STALE" if record["stale"] else "SOURCE_RECORDED"
            )
        })

    conflicts = []
    comparisons = []

    for (indicator, period), records in grouped.items():

        values = sorted(set(r["value"] for r in records))

        comparisons.append({
            "indicator": indicator,
            "period": period,
            "observations": len(records),
            "distinct_values": len(values),
            "sources": sorted(set(r["source"] for r in records))
        })

        if len(values) > 1:
            conflicts.append({
                "indicator": indicator,
                "period": period,
                "observations": [
                    {
                        "value": r["value"],
                        "source": r["source"]
                    }
                    for r in records
                ],
                "status": "UNRESOLVED_SOURCE_DISAGREEMENT",
                "explanation": (
                    "Sources report different values. Check definitions, "
                    "geographic coverage, methodology and reporting "
                    "periods before treating them as comparable."
                )
            })

    available = sorted(set(
        indicator for indicator, _ in grouped
    ))

    missing = [
        indicator for indicator in expected_indicators
        if indicator not in available
    ]

    stale_count = sum(
        1
        for records in grouped.values()
        for record in records
        if record["stale"]
    )

    if not claims:
        status = "INSUFFICIENT_EVIDENCE"
    elif conflicts or missing or warnings or stale_count:
        status = "REVIEW_REQUIRED"
    else:
        status = "EVIDENCE_AVAILABLE"

    return {
        "system": "KAUSHAL_RADAR",
        "module": "EVIDENCE_INTELLIGENCE",
        "district": district,
        "status": status,
        "evidence_count": len(claims),
        "indicators_available": available,
        "missing_indicators": missing,
        "source_register": sorted(sources),
        "evidence_claims": claims,
        "cross_source_comparisons": comparisons,
        "unresolved_conflicts": conflicts,
        "stale_observation_count": stale_count,
        "warnings": warnings,
        "human_review_required": status != "EVIDENCE_AVAILABLE",
        "decision_authority": "HUMAN_OFFICER",
        "limitations": [
            "Source labels do not independently authenticate data.",
            "Different values may reflect different definitions.",
            "No conflicting value is automatically selected.",
            "No causal explanation is inferred from these observations.",
            "Claims describe supplied observations, not independently "
            "verified official statistics."
        ]
    }


if __name__ == "__main__":
    import json

    # Synthetic data for testing only.
    sample = [
        {
            "indicator": "DGPI",
            "value": 4.03,
            "period": "2023-24",
            "source": "SYNTHETIC_SOURCE_A"
        },
        {
            "indicator": "DGPI",
            "value": 3.80,
            "period": "2023-24",
            "source": "SYNTHETIC_SOURCE_B"
        },
        {
            "indicator": "TRAINING",
            "value": 1200,
            "period": "2023-24",
            "source": "SYNTHETIC_SOURCE_C",
            "stale": True
        }
    ]

    result = analyse_evidence(
        district="Synthetic Raichur",
        observations=sample,
        expected_indicators=[
            "DGPI",
            "TRAINING",
            "PLACEMENT"
        ]
    )

    print(json.dumps(result, indent=2))
