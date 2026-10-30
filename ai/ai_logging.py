import logging

logger = logging.getLogger("kaushal_radar.ai")

def log_event(event, **metadata):
    safe = {
        key: value for key, value in metadata.items()
        if key.lower() not in {"name", "phone", "aadhaar", "email", "password"}
    }
    logger.info("%s | %s", event, safe)
