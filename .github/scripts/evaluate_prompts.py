"""Summarize supplied prompt evaluations; never launch models or invent usage."""

import argparse
import json
import math
from pathlib import Path


def summarize(cases, records):
    expected = {case["id"]: case for case in cases["cases"]}
    if len(expected) != len(cases["cases"]) or not expected:
        raise ValueError("Case identifiers must be unique and nonempty.")
    indexed = {}
    for row in records:
        key = (row["variant"], row["case_id"])
        if row["variant"] not in ("baseline", "candidate") or row["case_id"] not in expected:
            raise ValueError("Unknown variant or case.")
        if key in indexed or row.get("language") != cases["language"]:
            raise ValueError("Duplicate result or language mismatch.")
        if not isinstance(row.get("response"), str) or not row["response"].strip():
            raise ValueError("An observed response is required.")
        checks = row.get("checks", {})
        if set(checks) != set(expected[key[1]]["checks"]) or any(type(v) is not bool for v in checks.values()):
            raise ValueError("Every expected check needs an explicit boolean grade.")
        if row.get("mode") not in ("simulation", "isolated"):
            raise ValueError("Declare simulation or isolated execution.")
        for metric in ("total_tokens", "latency_ms", "tool_calls"):
            value = row.get(metric)
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
                raise ValueError("Metrics must be nonnegative finite numbers or null.")
        indexed[key] = row
    required = {(variant, case) for variant in ("baseline", "candidate") for case in expected}
    if set(indexed) != required:
        raise ValueError("Provide both variants for every case; incomplete runs are not a pass.")
    failures = [{"variant": v, "case_id": c, "checks": [k for k, ok in r["checks"].items() if not ok]}
                for (v, c), r in indexed.items() if not all(r["checks"].values())]
    comparable = all(
        indexed[("baseline", case)]["mode"] == indexed[("candidate", case)]["mode"] == "isolated"
        and all(isinstance(indexed[("baseline", case)].get(key), str)
                and indexed[("baseline", case)][key].strip()
                and indexed[("baseline", case)].get(key) == indexed[("candidate", case)].get(key)
                for key in ("model", "effort", "input_digest"))
        for case in expected
    )
    metrics = {}
    for metric in ("total_tokens", "latency_ms", "tool_calls"):
        if comparable and all(row.get(metric) is not None for row in records):
            totals = {v: sum(indexed[(v, c)][metric] for c in expected) for v in ("baseline", "candidate")}
            metrics[metric] = {**totals, "candidate_minus_baseline": totals["candidate"] - totals["baseline"]}
        else:
            metrics[metric] = None
    return {
        "language": cases["language"], "responses": len(records),
        "behavior_pass": not failures, "failures": failures,
        "metrics_comparable": comparable, "metrics": metrics,
        "note": "Grades and telemetry are caller-supplied. Null metrics mean unmeasured/non-comparable, not zero. No billing or optimality claim.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = summarize(json.loads(args.cases.read_text(encoding="utf-8")),
                           json.loads(args.results.read_text(encoding="utf-8")))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f"FAIL: {error}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["behavior_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
