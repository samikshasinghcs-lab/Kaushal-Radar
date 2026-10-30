import re

PATTERNS = {
    "email": r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
    "phone": r"(?<!\d)(?:\+91[- ]?)?[6-9]\d{9}(?!\d)",
    "aadhaar_like": r"(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{4}(?!\d)"
}

def detect_pii(text):
    return [
        name for name, pattern in PATTERNS.items()
        if re.search(pattern, str(text))
    ]

def reject_pii(text):
    found = detect_pii(text)
    if found:
        raise ValueError("Potential personal information detected: " + ", ".join(found))
    return True
