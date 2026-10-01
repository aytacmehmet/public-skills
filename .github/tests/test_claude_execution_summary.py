"""Guard against false success and disclosure in Claude execution diagnostics."""
import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("claude_summary", Path(__file__).parents[1] / "scripts/claude_execution_summary.py")
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


class ExecutionSummaryTests(unittest.TestCase):
    def test_is_error_overrides_success_subtype_and_hides_raw_result(self):
        secret = "PRIVATE_TOKEN_VALUE_NOT_FOR_OUTPUT"
        result = summary.summarize([{"type": "result", "subtype": "success", "is_error": True,
            "result": "API Error: 401 OAuth access token is invalid. " + secret, "num_turns": 1}], "fixture")
        self.assertEqual(("FAIL", "authentication_failed", 401), (result["status"], result["category"], result["http_status"]))
        self.assertNotIn(secret, json.dumps(result))
        self.assertNotIn("result", result)

    def test_missing_or_unexpected_result_never_passes(self):
        self.assertEqual("NOT_RUN", summary.summarize([], "fixture")["status"])
        self.assertEqual("FAIL", summary.summarize([{"type": "result", "subtype": "success", "result": "OK"}], "fixture")["status"])
        self.assertEqual("unexpected_response", summary.summarize([{"type": "result", "subtype": "success", "is_error": False, "result": "wrong"}], "fixture", "AUTH_CHECK_OK")["category"])

    def test_exact_completed_response_passes(self):
        result = summary.summarize([{"type": "result", "subtype": "success", "is_error": False, "result": "AUTH_CHECK_OK", "num_turns": 1}], "fixture", "AUTH_CHECK_OK")
        self.assertEqual("PASS", result["status"])

    def test_provider_errors_stay_distinct(self):
        for text, category in (("API Error: 429 usage limit", "usage_limit"), ("API Error: 404 model not found", "model_unavailable"),
                               ("Unknown skill: code-review:code-review", "command_not_found"), ("API Error: 403", "permission_denied"),
                               ("API Error: 503 overloaded", "provider_unavailable"), ("unspecified failure", "execution_error")):
            result = summary.summarize([{"type": "result", "subtype": "success", "is_error": True, "result": text}], "fixture")
            self.assertEqual(category, result["category"])


if __name__ == "__main__":
    unittest.main()
