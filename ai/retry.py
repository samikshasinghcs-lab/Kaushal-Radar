import time
from .exceptions import ProviderError

def with_retry(operation, attempts=2, delay=0.1):
    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    last_error = None
    for index in range(attempts):
        try:
            return operation()
        except Exception as exc:
            last_error = exc
            if index + 1 < attempts:
                time.sleep(delay * (2 ** index))

    raise ProviderError("Operation failed after retries.") from last_error
