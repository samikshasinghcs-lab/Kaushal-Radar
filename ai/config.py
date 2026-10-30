import os
from dataclasses import dataclass

@dataclass(frozen=True)
class AIConfig:
    provider: str = "mock"
    model: str = "deterministic-mock-v1"
    timeout_seconds: int = 15
    max_retries: int = 2
    cache_ttl_seconds: int = 300

    @classmethod
    def from_env(cls):
        return cls(
            provider=os.getenv("KAUSHAL_AI_PROVIDER", "mock"),
            model=os.getenv("KAUSHAL_AI_MODEL", "deterministic-mock-v1"),
            timeout_seconds=max(1, int(os.getenv("KAUSHAL_AI_TIMEOUT", "15"))),
            max_retries=max(0, int(os.getenv("KAUSHAL_AI_RETRIES", "2"))),
            cache_ttl_seconds=max(0, int(os.getenv("KAUSHAL_AI_CACHE_TTL", "300")))
        )
