"""Input validation."""

MAX_QUERY_LENGTH = 2000
MAX_RECORDS = 10000


def sanitise_query(query):
    if not isinstance(query, str):
        raise TypeError("Query must be text.")

    query = query.strip()

    if not query:
        raise ValueError("Query cannot be empty.")

    if len(query) > MAX_QUERY_LENGTH:
        raise ValueError("Query too long.")

    if "\x00" in query:
        raise ValueError("Null bytes prohibited.")

    return query


def validate_records(records):
    if not isinstance(records, list):
        raise TypeError("Records must be a list.")

    if len(records) > MAX_RECORDS:
        raise ValueError("Too many records.")

    if not all(isinstance(x, dict) for x in records):
        raise ValueError("Every record must be an object.")

    return {"valid": True, "record_count": len(records)}
