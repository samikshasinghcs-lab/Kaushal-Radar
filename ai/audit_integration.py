from .ai_logging import log_event

def record_ai_action(task, sources, validation_status, model="mock"):
    event = {
        "task": task,
        "sources": list(sources),
        "validation_status": validation_status,
        "model": model,
        "human_review_required": True
    }
    log_event("AI_ACTION", task=task, model=model,
              validation_status=validation_status)
    return event
