from .evidence_analyst import analyse
from .uncertainty_explainer import explain_uncertainty

def generate_brief(district, evidence):
    analysis = analyse(evidence)
    uncertainty = explain_uncertainty(evidence)

    return {
        "district": district,
        "evidence_status": analysis["status"],
        "summary": analysis["summary"],
        "claims": analysis["claims"],
        "sources": analysis["sources"],
        "uncertainty": uncertainty,
        "decision": "HUMAN_REVIEW_REQUIRED"
    }
