from abc import ABC, abstractmethod
from .exceptions import ProviderError
from .schemas import validate_evidence

class BaseProvider(ABC):
    @abstractmethod
    def generate(self, task, evidence, context=None):
        pass

class MockProvider(BaseProvider):
    """Offline provider for reproducible development and testing."""

    def generate(self, task, evidence, context=None):
        try:
            validate_evidence(evidence)
            if not evidence:
                return {
                    "summary": "Insufficient evidence to produce an interpretation.",
                    "claims": [],
                    "sources": [],
                    "limitations": ["No evidence supplied."],
                    "abstain": True
                }

            sources = list(dict.fromkeys(
                item["source"] for item in evidence
            ))

            claims = [
                {
                    "indicator": item["indicator"],
                    "value": item["value"],
                    "source": item["source"]
                }
                for item in evidence
            ]

            return {
                "summary": (
                    f"Offline demonstration for task '{task}'. "
                    f"{len(evidence)} evidence item(s) supplied. "
                    "This is a structured evidence summary, not an LLM interpretation."
                ),
                "claims": claims,
                "sources": sources,
                "limitations": [
                    "Mock provider: no language model interpretation performed.",
                    "No policy recommendation or government decision is made."
                ],
                "abstain": False
            }
        except Exception as exc:
            raise ProviderError(str(exc)) from exc
