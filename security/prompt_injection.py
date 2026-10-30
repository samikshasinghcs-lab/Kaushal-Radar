import re

PATTERNS = [
    r"ignore (all )?(previous|prior) instructions",
    r"reveal (the )?(system prompt|hidden instructions)",
    r"act as (a )?system",
    r"override (all )?safety",
    r"disregard (all )?rules"
]

def detect_injection(text):
    value = str(text).lower()
    return [
        pattern for pattern in PATTERNS
        if re.search(pattern, value)
    ]

def reject_injection(text):
    matches = detect_injection(text)
    if matches:
        raise ValueError("Potential prompt injection detected.")
    return True
