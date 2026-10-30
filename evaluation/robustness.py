def evaluate(function, inputs):
    results = []
    for item in inputs:
        try:
            function(item)
            results.append({"input": repr(item), "handled": True})
        except (ValueError, TypeError, KeyError):
            results.append({"input": repr(item), "handled": True})
        except Exception as exc:
            results.append({
                "input": repr(item),
                "handled": False,
                "error": type(exc).__name__
            })

    return {
        "total": len(results),
        "handled": sum(x["handled"] for x in results),
        "failures": [x for x in results if not x["handled"]]
    }
