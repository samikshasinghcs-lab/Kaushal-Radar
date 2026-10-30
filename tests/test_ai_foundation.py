import unittest
from ai.config import AIConfig
from ai.provider import MockProvider
from ai.schemas import validate_evidence, validate_response
from ai.exceptions import ValidationError
from ai.cache import ResponseCache
from ai.retry import with_retry

class TestAIFoundation(unittest.TestCase):
    def setUp(self):
        self.evidence = [
            {"indicator": "DGPI", "value": 4.03, "source": "synthetic_source"}
        ]

    def test_mock_provider_returns_structured_output(self):
        result = MockProvider().generate("evidence", self.evidence)
        self.assertTrue(validate_response(result))
        self.assertEqual(result["claims"][0]["value"], 4.03)

    def test_mock_provider_labels_its_limitations(self):
        result = MockProvider().generate("evidence", self.evidence)
        self.assertTrue(any("Mock provider" in x for x in result["limitations"]))

    def test_empty_evidence_abstains(self):
        result = MockProvider().generate("evidence", [])
        self.assertTrue(result["abstain"])

    def test_missing_source_rejected(self):
        with self.assertRaises(ValidationError):
            validate_evidence([{"indicator": "DGPI", "value": 4}])

    def test_invalid_response_rejected(self):
        with self.assertRaises(ValidationError):
            validate_response({"summary": "bad"})

    def test_config_defaults_to_mock(self):
        self.assertEqual(AIConfig().provider, "mock")

    def test_cache_round_trip(self):
        cache = ResponseCache(30)
        cache.set("evidence", self.evidence, {"ok": True})
        self.assertEqual(cache.get("evidence", self.evidence), {"ok": True})

    def test_cache_separates_tasks(self):
        cache = ResponseCache(30)
        cache.set("evidence", self.evidence, {"ok": True})
        self.assertIsNone(cache.get("brief", self.evidence))

    def test_retry_success(self):
        self.assertEqual(with_retry(lambda: 42), 42)

    def test_retry_failure(self):
        def fail():
            raise ValueError("failure")
        with self.assertRaises(Exception):
            with_retry(fail, attempts=2, delay=0)

if __name__ == "__main__":
    unittest.main()
