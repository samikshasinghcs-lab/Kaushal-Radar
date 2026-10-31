"""Deterministic anomaly detection and evidence-grounded explanations."""

from numbers import Real


def analyse_anomalies(
    observations,
    change_threshold=30.0
):
    if not isinstance(observations, list):
        raise TypeError("Observations must be a list.")

    if not isinstance(change_threshold, Real) or change_threshold < 0:
        raise ValueError("Threshold must be a non-negative number.")

    grouped = {}
    warnings = []
    anomalies = []

    for index, item in enumerate(observations):
        if not isinstance(item, dict):
            warnings.append(f"Record {index} is malformed.")
            continue

        indicator = item.get("indicator")
        period = item.get("period")
        source = item.get("source")
        value = item.get("value")

        if not indicator or not period or not source:
            warnings.append(f"Record {index} has missing metadata.")
            continue

        if isinstance(value, bool) or not isinstance(value, Real):
            warnings.append(f"{indicator}: invalid numeric observation.")
            continue

        grouped.setdefault(indicator, []).append({
            "period": str(period),
            "value": float(value),
            "source": str(source),
            "stale": bool(item.get("stale", False))
        })

    for indicator, records in grouped.items():
        records.sort(key=lambda x: x["period"])

        if len(records) < 2:
            warnings.append(
                f"{indicator}: insufficient periods for comparison."
            )
            continue

        for previous, current in zip(records, records[1:]):
            if previous["stale"] or current["stale"]:
                warnings.append(
                    f"{indicator}: stale observation excluded from comparison."
                )
                continue

            old = previous["value"]
            new = current["value"]

            absolute_change = new - old

            percentage_change = (
                None if old == 0
                else (absolute_change / abs(old)) * 100
            )

            unusual = (
                percentage_change is not None
                and abs(percentage_change) >= change_threshold
            )

            result = {
                "indicator": indicator,
                "previous_period": previous["period"],
                "current_period": current["period"],
                "previous_value": old,
                "current_value": new,
                "absolute_change": round(absolute_change, 4),
                "percentage_change": (
                    round(percentage_change, 2)
                    if percentage_change is not None else None
                ),
                "previous_source": previous["source"],
                "current_source": current["source"],
                "requires_investigation": unusual
            }

            if unusual:
                result["explanation"] = (
                    "The observed change exceeds the configured "
                    "percentage threshold. Verify source definitions, "
                    "reporting periods and data quality before "
                    "drawing conclusions."
                )
                anomalies.append(result)

    return {
        "status": (
            "ANOMALIES_DETECTED" if anomalies
            else "NO_THRESHOLD_EXCEEDANCE_DETECTED"
        ),
        "threshold_percentage": float(change_threshold),
        "anomalies": anomalies,
        "warnings": warnings,
        "human_review_required": bool(anomalies or warnings),
        "limitations": [
            "Threshold exceedance is not proof of an error.",
            "The method does not establish causation.",
            "Different source definitions may explain changes.",
            "A threshold-based detector may miss other anomalies."
        ]
    }


def explain_anomaly(observation):
    """Compatibility adapter for single-observation anomaly checks."""
    if not isinstance(observation, dict):
        raise TypeError("observation must be a dictionary")

    required = ("indicator", "observed_value", "expected_value")
    missing = [key for key in required if key not in observation]
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")

    observed = observation["observed_value"]
    expected = observation["expected_value"]

    if (
        isinstance(observed, bool)
        or isinstance(expected, bool)
        or not isinstance(observed, (int, float))
        or not isinstance(expected, (int, float))
    ):
        raise ValueError("Observed and expected values must be numeric")

    status = (
        "REQUIRES_REVIEW"
        if observed != expected
        else "NO_ANOMALY_DETECTED"
    )

    return {
        "indicator": observation["indicator"],
        "observed_value": observed,
        "expected_value": expected,
        "status": status,
        "method": observation.get("method", "unspecified"),
        "explanation": (
            "Observed value differs from expected value; human review required."
            if status == "REQUIRES_REVIEW"
            else "Observed value matches expected value."
        ),
    }
