from .numeric_guard import verify_numbers
from .source_grounding import verify_sources

def validate_claims(claims, evidence):
    numeric = verify_numbers(claims, evidence)
    sources = verify_sources(claims, evidence)
    accepted = []
    rejected = []

    for claim, number, source in zip(claims, numeric, sources):
        if number["valid"] and source["grounded"]:
            accepted.append(claim)
        else:
            rejected.append({
                "claim": claim,
                "numeric_valid": number["valid"],
                "source_valid": source["grounded"]
            })

    return {"accepted": accepted, "rejected": rejected}
