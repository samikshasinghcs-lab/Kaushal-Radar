ALLOWED_FIELDS = {
    "district", "indicator", "value",
    "source", "period", "stale",
    "valid", "missing", "denominator_sensitive"
}

def minimise_evidence(records):
    cleaned = []
    for record in records:
        cleaned.append({
            key: value for key, value in record.items()
            if key in ALLOWED_FIELDS
        })
    return cleaned
