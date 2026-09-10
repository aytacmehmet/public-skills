import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("prompt_evaluation", ROOT / ".github/scripts/evaluate_prompts.py")
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.cases = {"language": "en", "cases": [{"id": "example", "checks": ["scope"]}]}
        self.records = [{"variant": v, "case_id": "example", "language": "en", "response": "Observed output",
                         "checks": {"scope": True}, "mode": "simulation"} for v in ("baseline", "candidate")]

    def test_missing_usage_is_not_zero_or_savings(self):
        result = evaluation.summarize(self.cases, self.records)
        self.assertTrue(result["behavior_pass"])
        self.assertFalse(result["metrics_comparable"])
        self.assertIsNone(result["metrics"]["total_tokens"])

    def test_incomplete_or_duplicate_run_is_rejected(self):
        for rows in (self.records[:1], self.records + self.records[:1]):
            with self.subTest(rows=len(rows)), self.assertRaises(ValueError):
                evaluation.summarize(self.cases, rows)

    def test_failed_behavior_cannot_pass(self):
        self.records[1]["checks"]["scope"] = False
        self.assertFalse(evaluation.summarize(self.cases, self.records)["behavior_pass"])

    def test_comparable_telemetry_uses_total_only(self):
        for index, row in enumerate(self.records):
            row.update(mode="isolated", model="fixture", effort="low", input_digest="same-input",
                       total_tokens=100 - index * 20, cached_input_tokens=50, reasoning_tokens=10)
        result = evaluation.summarize(self.cases, self.records)
        self.assertEqual(result["metrics"]["total_tokens"]["candidate_minus_baseline"], -20)
        self.records[1]["model"] = "different-model"
        self.assertIsNone(evaluation.summarize(self.cases, self.records)["metrics"]["total_tokens"])

    def test_negative_or_nonfinite_metrics_rejected(self):
        for value in (-1, float("nan"), True):
            records = copy.deepcopy(self.records)
            records[0]["total_tokens"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                evaluation.summarize(self.cases, records)

    def test_translations_share_case_ids_and_checks(self):
        paths = [ROOT / "tr/yordamla/references/evaluation-cases.json", ROOT / "en/prompter/references/evaluation-cases.json"]
        pairs = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
        self.assertEqual(pairs[0]["language"], "tr")
        self.assertEqual(pairs[1]["language"], "en")
        maps = [{case["id"]: case["checks"] for case in data["cases"]} for data in pairs]
        self.assertEqual(maps[0], maps[1])
        self.assertEqual(len(maps[0]), 6)


if __name__ == "__main__":
    unittest.main()
