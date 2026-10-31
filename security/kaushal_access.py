"""Deny-by-default district access demonstration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Officer:
    officer_id: str
    role: str
    districts: tuple


ALLOWED_ROLES = {
    "district_officer",
    "state_analyst",
    "administrator"
}


def authorise_district_access(officer, district):

    if not isinstance(officer, Officer):
        return {"allowed": False, "reason": "Invalid identity."}

    if officer.role not in ALLOWED_ROLES:
        return {"allowed": False, "reason": "Role not authorised."}

    if not isinstance(district, str) or not district.strip():
        return {"allowed": False, "reason": "Invalid district."}

    if officer.role == "administrator":
        return {"allowed": True, "reason": "Administrator role."}

    permitted = {x.casefold() for x in officer.districts}

    if district.casefold() not in permitted:
        return {"allowed": False, "reason": "District access denied."}

    return {"allowed": True, "reason": "District permission verified."}
