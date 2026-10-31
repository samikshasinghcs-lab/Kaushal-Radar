"""Allowlist-based evidence minimisation."""

ALLOWED_FIELDS = {
    "indicator",
    "value",
    "period",
    "source",
    "stale"
}


def minimise_evidence(records):

    if not isinstance(records, list):
        raise TypeError("Evidence must be a list.")

    output = []

    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Invalid evidence record.")

        output.append({
            key: record[key]
            for key in ALLOWED_FIELDS
            if key in record
        })

    return {
        "records": output,
        "input_count": len(records),
        "output_count": len(output)
    }
