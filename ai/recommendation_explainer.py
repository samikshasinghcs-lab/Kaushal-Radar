def explain_decision(status, reasons, sources=None):
    return {
        "deterministic_status": status,
        "reasons": list(reasons),
        "sources": list(sources or []),
        "authority": "EXPLANATION_ONLY",
        "human_review_required": True
    }
