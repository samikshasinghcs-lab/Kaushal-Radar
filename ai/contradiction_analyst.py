def analyse_contradictions(evidence):
    groups = {}
    for item in evidence:
        key = (
            item.get("district"),
            item.get("indicator"),
            item.get("period")
        )
        groups.setdefault(key, []).append(item)

    conflicts = []
    for key, items in groups.items():
        values = {str(x["value"]) for x in items}
        if len(values) > 1:
            conflicts.append({
                "district": key[0],
                "indicator": key[1],
                "period": key[2],
                "values": sorted(values),
                "sources": list(dict.fromkeys(x["source"] for x in items)),
                "status": "REQUIRES_REVIEW"
            })
    return conflicts
