ROLE_PERMISSIONS = {
    "admin": {"read", "review", "manage"},
    "officer": {"read", "review"},
    "analyst": {"read"},
}

def authorize_request(role, action, district=None, user_district=None):
    if role not in ROLE_PERMISSIONS:
        return False

    if action not in ROLE_PERMISSIONS[role]:
        return False

    if role == "officer" and district != user_district:
        return False

    return True
