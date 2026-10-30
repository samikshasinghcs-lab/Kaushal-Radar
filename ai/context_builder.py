from .schemas import validate_evidence

def build_context(evidence, district=None, max_items=50):
    validate_evidence(evidence)
    selected = [
        item for item in evidence
        if district is None or item.get("district") == district
    ]
    return selected[:max(0, max_items)]
