from .retrieval import retrieve
from .evidence_analyst import analyse

def answer_question(question, evidence, district=None):
    if not isinstance(question, str) or not question.strip():
        raise ValueError("A question is required.")

    # This initial offline version retrieves by district.
    # Indicator-aware semantic language understanding requires an LLM.
    records = retrieve(evidence, district=district)

    return {
        "question": question,
        "answer": analyse(records),
        "mode": "OFFLINE_RETRIEVAL",
        "limitation": "No semantic language model is connected."
    }
