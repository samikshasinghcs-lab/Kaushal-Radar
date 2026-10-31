"""Unified security pre-processing gate."""

from security.kaushal_input import sanitise_query
from security.kaushal_injection import inspect_untrusted_text
from security.kaushal_access import authorise_district_access
from security.kaushal_minimisation import minimise_evidence


def governance_gate(officer, district, query, evidence):

    access = authorise_district_access(officer, district)

    if not access["allowed"]:
        return {"allowed": False, "reason": access["reason"]}

    clean_query = sanitise_query(query)
    injection = inspect_untrusted_text(clean_query)

    if injection["suspicious"]:
        return {
            "allowed": False,
            "reason": "Suspicious instructions detected.",
            "injection_check": injection
        }

    minimised = minimise_evidence(evidence)

    return {
        "allowed": True,
        "district": district,
        "sanitised_query": clean_query,
        "injection_check": injection,
        "minimised_evidence": minimised["records"],
        "governance": {
            "access_control_passed": True,
            "input_validation_passed": True,
            "data_minimisation_applied": True,
            "decision_authority": "HUMAN_OFFICER"
        }
    }
