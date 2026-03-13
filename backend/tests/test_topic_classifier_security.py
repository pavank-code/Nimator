import unittest
import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace


fake_config = types.ModuleType("app.config")
fake_config.settings = SimpleNamespace(LLM_PROVIDER="auto", NVIDIA_API_KEY=None)
sys.modules["app.config"] = fake_config

test_file = Path(__file__).resolve()
backend_root = next(
    parent for parent in test_file.parents
    if (parent / "app" / "services" / "topic_classifier.py").exists()
)
module_path = backend_root / "app" / "services" / "topic_classifier.py"
spec = importlib.util.spec_from_file_location("topic_classifier_under_test", module_path)
topic_classifier_module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(topic_classifier_module)
LLMClient = topic_classifier_module.LLMClient


class TestLLMClientSanitization(unittest.TestCase):
    def test_redacts_explicit_api_key_value(self):
        original = "request failed with key=supersecretvalue"
        sanitized = LLMClient._sanitize_error_message(original, "supersecretvalue")
        self.assertNotIn("supersecretvalue", sanitized)
        self.assertIn("[REDACTED_API_KEY]", sanitized)

    def test_redacts_query_string_keys(self):
        original = "403 for https://example.com/path?key=abc123&x=1"
        sanitized = LLMClient._sanitize_error_message(original)
        self.assertIn("?key=[REDACTED_API_KEY]", sanitized)
        self.assertNotIn("abc123", sanitized)

    def test_redacts_api_key_variants(self):
        original = "403 for https://example.com/path?api_key=abc123&apiKey=xyz456"
        sanitized = LLMClient._sanitize_error_message(original)
        self.assertIn("?api_key=[REDACTED_API_KEY]", sanitized)
        self.assertIn("&apiKey=[REDACTED_API_KEY]", sanitized)
        self.assertNotIn("abc123", sanitized)
        self.assertNotIn("xyz456", sanitized)

    def test_redacts_bearer_token(self):
        original = "Authorization failed: Bearer token-secret-value"
        sanitized = LLMClient._sanitize_error_message(original)
        self.assertIn("Bearer [REDACTED_API_KEY]", sanitized)
        self.assertNotIn("token-secret-value", sanitized)


if __name__ == "__main__":
    unittest.main()
