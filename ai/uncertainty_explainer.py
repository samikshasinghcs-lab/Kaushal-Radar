def explain_uncertainty(evidence):
    issues = []
    for item in evidence:
        if item.get("stale"):
            issues.append("Stale evidence: " + item["indicator"])
        if item.get("valid") is False:
            issues.append("Invalid evidence: " + item["indicator"])
        if item.get("missing"):
            issues.append("Missing evidence: " + item["indicator"])
        if item.get("denominator_sensitive"):
            issues.append("Denominator sensitivity: " + item["indicator"])

    return {
        "issues": issues,
        "status": "UNCERTAINTY_PRESENT" if issues else "NO_RECORDED_ISSUES"
    }
