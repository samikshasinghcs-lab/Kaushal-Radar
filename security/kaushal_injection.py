"""Heuristic prompt-injection detection."""

import re

PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"override\s+(your\s+)?instructions",
    r"disregard\s+(all\s+)?rules",
    r"exfiltrate\s+data",
    r"bypass\s+(security|authentication|access control)"
]


def inspect_untrusted_text(text):
    if not isinstance(text, str):
        raise TypeError("Text must be a string.")

    matches = [
        pattern for pattern in PATTERNS
        if re.search(pattern, text, re.IGNORECASE)
    ]

    return {
        "suspicious": bool(matches),
        "matched_patterns": matches,
        "treatment": (
            "QUARANTINE_FOR_REVIEW"
            if matches else "NO_KNOWN_PATTERN_DETECTED"
        ),
        "limitation": "Heuristic detection cannot catch every attack."
    }
