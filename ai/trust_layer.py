"""
KAUSHAL RADAR — Trust and Validation Layer.

Deterministic safeguards for evidence-grounded decision support.

This module does not authenticate external sources or guarantee
the truth of supplied data. It verifies consistency with supplied
evidence and enforces conservative output rules.
"""

import json
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone


class TrustValidationError(ValueError):
    pass


# ---------------------------------------------------------
# 1. SOURCE GROUNDING
# ---------------------------------------------------------

def verify_claims(claims, evidence):

    if not isinstance(claims, list):
        raise TypeError("Claims must be a list.")

    if not isinstance(evidence, list):
        raise TypeError("Evidence must be a list.")

    verified = []
    unsupported = []

    for claim in claims:

        if not isinstance(claim, dict):
            unsupported.append({
                "claim": claim,
                "reason": "Claim is not a structured record."
            })
            continue

        required = ["indicator", "value", "period", "source"]

        if not all(key in claim for key in required):
            unsupported.append({
                "claim": claim,
                "reason": "Required claim fields are missing."
            })
            continue

        match = any(
            isinstance(item, dict)
            and item.get("indicator") == claim["indicator"]
            and item.get("value") == claim["value"]
            and item.get("period") == claim["period"]
            and item.get("source") == claim["source"]
            for item in evidence
        )

        if match:
            verified.append(claim)
        else:
            unsupported.append({
                "claim": claim,
                "reason": "No exact matching evidence record."
            })

    return {
        "verified_claims": verified,
        "unsupported_claims": unsupported,
        "passed": len(unsupported) == 0
    }


# ---------------------------------------------------------
# 2. NUMERIC INTEGRITY
# ---------------------------------------------------------

def validate_numeric_claims(claims, evidence):

    valid = []
    invalid = []

    for claim in claims:

        if not isinstance(claim, dict):
            invalid.append({
                "claim": claim,
                "reason": "Invalid claim structure."
            })
            continue

        value = claim.get("value")

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            invalid.append({
                "claim": claim,
                "reason": "Claim does not contain a valid number."
            })
            continue

        matching = [
            item for item in evidence
            if isinstance(item, dict)
            and item.get("indicator") == claim.get("indicator")
            and item.get("period") == claim.get("period")
            and item.get("source") == claim.get("source")
        ]

        if any(item.get("value") == value for item in matching):
            valid.append(claim)
        else:
            invalid.append({
                "claim": claim,
                "reason": "Numeric value does not match supplied evidence."
            })

    return {
        "valid_numeric_claims": valid,
        "invalid_numeric_claims": invalid,
        "passed": len(invalid) == 0
    }


# ---------------------------------------------------------
# 3. HALLUCINATION GUARD
# ---------------------------------------------------------

def detect_unsupported_claims(claims, evidence):

    grounding = verify_claims(claims, evidence)

    return {
        "accepted": grounding["verified_claims"],
        "rejected": grounding["unsupported_claims"],
        "hallucination_risk_detected": bool(
            grounding["unsupported_claims"]
        ),
        "passed": grounding["passed"]
    }


# ---------------------------------------------------------
# 4. STRUCTURED OUTPUT VALIDATION
# ---------------------------------------------------------

def validate_district_report(report):

    required = {
        "system",
        "district",
        "status",
        "evidence",
        "anomalies",
        "uncertainty",
        "claims",
        "governance"
    }

    if not isinstance(report, dict):
        raise TrustValidationError("Report must be a JSON object.")

    missing = required - set(report.keys())

    if missing:
        raise TrustValidationError(
            f"Missing report fields: {sorted(missing)}"
        )

    if not isinstance(report["district"], str):
        raise TrustValidationError("District must be a string.")

    if not isinstance(report["claims"], list):
        raise TrustValidationError("Claims must be a list.")

    if not isinstance(report["evidence"], dict):
        raise TrustValidationError("Evidence must be an object.")

    if not isinstance(report["anomalies"], dict):
        raise TrustValidationError("Anomalies must be an object.")

    if not isinstance(report["uncertainty"], dict):
        raise TrustValidationError("Uncertainty must be an object.")

    governance = report["governance"]

    if not isinstance(governance, dict):
        raise TrustValidationError("Governance must be an object.")

    if governance.get("decision_authority") != "HUMAN_OFFICER":
        raise TrustValidationError(
            "Human decision authority must be preserved."
        )

    if governance.get("automatic_funding_approval") is not False:
        raise TrustValidationError(
            "Automatic funding approval must be disabled."
        )

    return {
        "valid": True,
        "schema_version": "1.0",
        "errors": []
    }


# ---------------------------------------------------------
# 5. PII PROTECTION
# ---------------------------------------------------------

PII_PATTERNS = {
    "email": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),
    "phone": re.compile(
        r"(?<!\d)(?:\+91[- ]?)?[6-9]\d{9}(?!\d)"
    ),
    "aadhaar_like": re.compile(
        r"(?<!\d)\d{4}[ -]?\d{4}[ -]?\d{4}(?!\d)"
    ),
    "pan_like": re.compile(
        r"\b[A-Z]{5}\d{4}[A-Z]\b"
    )
}


def redact_pii(text):

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    redacted = text
    detections = []

    for category, pattern in PII_PATTERNS.items():

        matches = pattern.findall(redacted)

        if matches:
            detections.extend([category] * len(matches))
            redacted = pattern.sub(
                f"[REDACTED_{category.upper()}]",
                redacted
            )

    return {
        "redacted_text": redacted,
        "pii_detected": bool(detections),
        "categories": sorted(set(detections)),
        "detection_count": len(detections)
    }


# ---------------------------------------------------------
# 6. CONFIDENCE AND ABSTENTION
# ---------------------------------------------------------

def assess_sufficiency(
    evidence,
    expected_indicators=None,
    conflicts=None,
    minimum_records=1
):

    expected_indicators = expected_indicators or []
    conflicts = conflicts or []

    available = {
        item.get("indicator")
        for item in evidence
        if isinstance(item, dict)
    }

    missing = [
        indicator
        for indicator in expected_indicators
        if indicator not in available
    ]

    stale = [
        item for item in evidence
        if isinstance(item, dict) and item.get("stale", False)
    ]

    reasons = []

    if len(evidence) < minimum_records:
        reasons.append("Insufficient evidence records.")

    if missing:
        reasons.append("Expected indicators are missing.")

    if conflicts:
        reasons.append("Unresolved source disagreements exist.")

    if stale:
        reasons.append("Stale observations are present.")

    sufficient = not reasons

    return {
        "sufficient_evidence": sufficient,
        "abstain": not sufficient,
        "missing_indicators": missing,
        "stale_record_count": len(stale),
        "reasons": reasons,
        "confidence_score": None,
        "confidence_note": (
            "No calibrated probability of correctness is available."
        )
    }


# ---------------------------------------------------------
# 7. AI AUDIT LOGGING
# ---------------------------------------------------------

def write_audit_event(
    event_type,
    district,
    sources=None,
    validation_passed=False,
    log_path="logs/ai_audit.jsonl"
):

    if not isinstance(event_type, str) or not event_type.strip():
        raise ValueError("Event type is required.")

    if not isinstance(district, str) or not district.strip():
        raise ValueError("District is required.")

    sources = sources or []

    safe_sources = [
        str(source)[:200]
        for source in sources
    ]

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "district": district,
        "sources": safe_sources,
        "validation_passed": bool(validation_passed)
    }

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")

    return {
        "logged": True,
        "event_type": event_type,
        "timestamp": event["timestamp"]
    }


# ---------------------------------------------------------
# 8. UNIFIED TRUST VALIDATION
# ---------------------------------------------------------

def validate_ai_output(report, evidence):

    schema = validate_district_report(report)

    grounding = verify_claims(
        report["claims"],
        evidence
    )

    numeric = validate_numeric_claims(
        report["claims"],
        evidence
    )

    hallucination = detect_unsupported_claims(
        report["claims"],
        evidence
    )

    passed = (
        schema["valid"]
        and grounding["passed"]
        and numeric["passed"]
        and hallucination["passed"]
    )

    return {
        "validation_passed": passed,
        "schema_validation": schema,
        "source_grounding": grounding,
        "numeric_integrity": numeric,
        "hallucination_guard": hallucination,
        "human_review_required": True,
        "decision_authority": "HUMAN_OFFICER"
    }


if __name__ == "__main__":

    from ai.master_pipeline import run_pipeline

    sample = [
        {
            "indicator": "DGPI",
            "value": 4.03,
            "period": "2023-24",
            "source": "SYNTHETIC_SOURCE_A"
        }
    ]

    report = run_pipeline(
        "Synthetic Raichur",
        sample
    )

    result = validate_ai_output(report, sample)

    print(json.dumps(result, indent=2))
