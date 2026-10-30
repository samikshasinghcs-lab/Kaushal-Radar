from .exceptions import ValidationError

def validate_evidence(evidence):
    if not isinstance(evidence, list):
        raise ValidationError("Evidence must be a list.")

    for item in evidence:
        if not isinstance(item, dict):
            raise ValidationError("Each evidence item must be an object.")
        required = ("indicator", "value", "source")
        if any(k not in item for k in required):
            raise ValidationError("Evidence requires indicator, value and source.")
        if not isinstance(item["source"], str) or not item["source"].strip():
            raise ValidationError("Evidence source cannot be empty.")

    return evidence

def validate_response(response):
    required = {"summary", "claims", "sources", "limitations", "abstain"}

    if not isinstance(response, dict) or not required.issubset(response):
        raise ValidationError("AI response does not match required schema.")

    if not isinstance(response["summary"], str):
        raise ValidationError("summary must be text.")
    if not isinstance(response["claims"], list):
        raise ValidationError("claims must be a list.")
    if not isinstance(response["sources"], list):
        raise ValidationError("sources must be a list.")
    if not isinstance(response["limitations"], list):
        raise ValidationError("limitations must be a list.")
    if not isinstance(response["abstain"], bool):
        raise ValidationError("abstain must be boolean.")

    return response
