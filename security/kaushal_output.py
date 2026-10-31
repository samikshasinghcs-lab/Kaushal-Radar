"""Restrict automatic government decisions."""

PROHIBITED_FIELDS = {
    "approve_funding",
    "automatic_funding_approval",
    "authorise_payment",
    "automatic_departmental_action"
}


def validate_policy_output(output):

    if not isinstance(output, dict):
        raise TypeError("Output must be an object.")

    violations = []

    for field in PROHIBITED_FIELDS:
        if output.get(field) is True:
            violations.append(field)

    governance = output.get("governance", {})

    if not isinstance(governance, dict):
        violations.append("invalid_governance_structure")
    elif governance.get("decision_authority") not in (
        None, "HUMAN_OFFICER"
    ):
        violations.append("unauthorised_decision_authority")

    return {
        "passed": not violations,
        "violations": violations,
        "human_review_required": True
    }
