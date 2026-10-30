import hashlib
import json
import time

class ResponseCache:
    def __init__(self, ttl_seconds=300):
        self.ttl = max(0, ttl_seconds)
        self._items = {}

    def _key(self, task, evidence, context):
        raw = json.dumps(
            [task, evidence, context],
            sort_keys=True,
            default=str
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, task, evidence, context=None):
        key = self._key(task, evidence, context)
        item = self._items.get(key)
        if item is None:
            return None
        expires, value = item
        if time.monotonic() >= expires:
            self._items.pop(key, None)
            return None
        return value

    def set(self, task, evidence, value, context=None):
        if self.ttl == 0:
            return
        key = self._key(task, evidence, context)
        self._items[key] = (time.monotonic() + self.ttl, value)

    def clear(self):
        self._items.clear()
