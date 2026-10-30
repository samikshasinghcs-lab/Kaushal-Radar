def explain_anomaly(anomaly):
    required = ("indicator", "observed_value", "expected_value", "method")
    missing = [x for x in required if x not in anomaly]
    if missing:
        raise ValueError(f"Missing anomaly fields: {missing}")

    return {
        "indicator": anomaly["indicator"],
        "observed_value": anomaly["observed_value"],
        "expected_value": anomaly["expected_value"],
        "detection_method": anomaly["method"],
        "explanation": "A deterministic check detected an unusual value. Investigate the source before interpreting it.",
        "status": "REQUIRES_REVIEW"
    }
