# Bounded behavior and cost comparison

This file is for maintenance/evaluation only. Do not run tests or benchmarks during ordinary prompt preparation.

The [six paired scenarios](evaluation-cases.json) cover short text, ambiguity, code, source authority, model-note-only changes, and uncertain external outcomes. Turkish counterparts use the same identifiers and check keys. When adding behavior, also add relevant counterexamples to the [behavior list](behavior-checks.md).

For an initial screen, evaluate the same six inputs under old and new instructions: 12 responses. Treat each scenario independently. Grade every `checks` criterion by observing the responses; keyword matching is not behavioral evidence. A batched conversation simulation does not measure real isolated execution cost.

The comparison tool makes no model calls; it summarizes externally produced results. From the repository root:

```text
python .github/scripts/evaluate_prompts.py --cases en/prompter/references/evaluation-cases.json --results <results.json>
```

The results file is a JSON array with `baseline` and `candidate` records for every case. Each record contains `variant`, `case_id`, `language`, the full observed `response`, boolean grades in `checks` for every required criterion, and `mode`. Use `simulation` or `isolated` for mode. Missing/duplicate records, missing checks, or failed behavior are not a pass. Do not invent observations or grades.

For real measurements, use separate runs of the same input and record verified `model`, `effort`, `input_digest`, and available `total_tokens`, `latency_ms`, `tool_calls`. The input identity denotes identical input/context apart from skill version. Different models, effort, or inputs are not compared for cost. Omit unknown metrics or use `null`, never invented zeros. Obtain total tokens from the environment; do not add cache and reasoning breakdowns to that total again.

Null summary metrics mean unmeasured/non-comparable. The tool cannot independently verify supplied grades or telemetry and makes no billing or model-optimality guarantee. A candidate with reduced quality is not an improvement even if it uses fewer tokens. Repeat variable cases instead of launching broad model comparisons on every invocation.
