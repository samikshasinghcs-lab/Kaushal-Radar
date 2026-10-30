from .schemas import validate_evidence
from .abstention import should_abstain

def analyse(evidence):
    validate_evidence(evidence)

    if should_abstain(evidence):
        return {
            "status": "INSUFFICIENT_EVIDENCE",
            "summary": "Evidence is insufficient or requires validation.",
            "claims": [],
            "sources": []
        }

    return {
        "status": "EVIDENCE_AVAILABLE",
        "summary": f"{len(evidence)} evidence records supplied for interpretation.",
        "claims": [
            {
                "indicator": x["indicator"],
                "value": x["value"],
                "source": x["source"]
            } for x in evidence
        ],
        "sources": list(dict.fromkeys(x["source"] for x in evidence))
    }
