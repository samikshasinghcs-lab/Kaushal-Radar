from ai.schemas import validate_response

def validate_ai_output(output, evidence):
    validate_response(output)

    from ai.hallucination_guard import validate_claims
    checked = validate_claims(output["claims"], evidence)

    if checked["rejected"]:
        raise ValueError("Output contains unsupported claims.")

    return output
