def compare(previous, current, tolerance=0.0):
    changes = {}
    for metric, old in previous.items():
        new = current.get(metric)
        if isinstance(old, (int, float)) and isinstance(new, (int, float)):
            changes[metric] = {
                "previous": old,
                "current": new,
                "delta": new - old,
                "regression": new < old - tolerance
            }
    return changes
