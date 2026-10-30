from .context_builder import build_context

def retrieve(evidence, district=None, indicator=None, max_items=50):
    results = build_context(evidence, district, max_items * 2)
    if indicator:
        results = [
            x for x in results
            if str(x["indicator"]).lower() == indicator.lower()
        ]
    return results[:max_items]
