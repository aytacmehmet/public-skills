"""Report bounded Claude failure categories without publishing raw execution text."""
import argparse
import json
from pathlib import Path
import re
import sys


def summarize(messages, requested_model, expect=None):
    results = [message for message in messages if isinstance(message, dict) and message.get("type") == "result"]
    if not results:
        return {"status": "NOT_RUN", "category": "missing_result", "requested_model": requested_model}
    result = results[-1]
    text = result.get("result", "")
    errors = result.get("errors", [])
    if isinstance(errors, list):
        text = str(text) + " " + " ".join(item for item in errors if isinstance(item, str))
    failed = result.get("is_error") is not False or result.get("subtype") != "success"
    category = "completed"
    if failed:
        category = "execution_error"
        for pattern, label in (
            (r"OAuth.*(?:invalid|expired)|invalid.*OAuth|authentication_failed|Failed to authenticate|API Error:\s*401", "authentication_failed"),
            (r"usage limit|rate.limit|API Error:\s*429", "usage_limit"),
            (r"model.*(?:not found|not available|does not exist|not supported)|API Error:\s*404", "model_unavailable"),
            (r"Unknown (?:skill|command)|skill.*not found", "command_not_found"),
            (r"API Error:\s*403|permission.denied|not authorized", "permission_denied"),
            (r"API Error:\s*5\d\d|overloaded", "provider_unavailable"),
        ):
            if re.search(pattern, text, re.I):
                category = label
                break
    elif expect is not None and result.get("result", "").strip() != expect:
        failed, category = True, "unexpected_response"
    status = next((int(value) for value in re.findall(r"API Error:\s*([1-5]\d\d)", text)), None)
    return {"status": "FAIL" if failed else "PASS", "category": category, "requested_model": requested_model,
            "http_status": status, "is_error": result.get("is_error") is not False,
            "num_turns": result.get("num_turns") if type(result.get("num_turns")) is int else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execution-file", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--expect")
    args = parser.parse_args()
    try:
        raw = Path(args.execution_file).read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except ValueError:
            data = [json.loads(line) for line in raw.splitlines() if line.strip()]
        if not isinstance(data, list):
            raise ValueError("Execution envelope must be an array")
        summary = summarize(data, args.model, args.expect)
    except (OSError, ValueError, TypeError):
        summary = {"status": "NOT_RUN", "category": "unreadable_execution", "requested_model": args.model}
    Path(args.output).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
