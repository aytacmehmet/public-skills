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
    if not isinstance(text, str):
        text = ""
    errors = result.get("errors", [])
    if isinstance(errors, list):
        text = str(text) + " " + " ".join(item for item in errors if isinstance(item, str))
    failed = result.get("is_error") is not False or result.get("subtype") != "success"
    # Claude can put the API error in a synthetic assistant turn and leave result.result empty.
    if failed:
        for message in messages:
            if not isinstance(message, dict) or message.get("type") != "assistant" or not message.get("error"):
                continue
            text += " " + str(message.get("error"))
            payload = message.get("message")
            if not isinstance(payload, dict) or not isinstance(payload.get("content"), list):
                continue
            for block in payload["content"]:
                if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str):
                    text += " " + block["text"]
    category = "completed"
    if failed:
        category = "execution_error"
        for pattern, label in (
            (r"OAuth.*(?:invalid|expired)|invalid.*OAuth|authentication_failed|Failed to authenticate|API Error:\s*401", "authentication_failed"),
            (r"only authorized for use with Claude Code|credential.*scope", "credential_scope"),
            (r"usage limit|rate.limit|API Error:\s*429", "usage_limit"),
            (r"model.*(?:not found|not available|does not exist|not supported)|API Error:\s*404", "model_unavailable"),
            (r"Unknown (?:skill|command)|skill.*not found", "command_not_found"),
            (r"API Error:\s*403|permission.denied|not authorized", "permission_denied"),
            (r"API Error:\s*5\d\d|overloaded", "provider_unavailable"),
        ):
            if re.search(pattern, text, re.I):
                category = label
                break
    elif expect is not None and (not isinstance(result.get("result"), str) or result["result"].strip() != expect):
        failed, category = True, "unexpected_response"
    status = next((int(value) for value in re.findall(r"API Error:\s*([1-5]\d\d)", text)), None)
    quota_exhausted = bool(re.search(r"you(?:'|’)ve hit your limit|you have (?:hit|reached|exceeded).*limit|usage limit|weekly limit|extra usage", text, re.I))
    reset_hint = re.search(r"\bresets?\s+((?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+)?\d{1,2}(?::\d{2})?\s*(?:am|pm)(?:\s*\((?:[A-Za-z_]+/[A-Za-z_]+|UTC)\))?)", text, re.I)
    return {"status": "FAIL" if failed else "PASS", "category": category, "requested_model": requested_model,
            "http_status": status, "is_error": result.get("is_error") is not False,
            "quota_exhausted": quota_exhausted, "reset_hint": reset_hint.group(1) if reset_hint else None,
            "num_turns": result.get("num_turns") if type(result.get("num_turns")) is int else None,
            "result_fields": sorted(key for key in result if re.fullmatch(r"[a-zA-Z_]{1,40}", key)),
            "assistant_error_codes": sorted({message["error"] for message in messages if isinstance(message, dict)
                and message.get("type") == "assistant" and message.get("error") in
                {"authentication_failed", "billing_error", "rate_limit", "invalid_request", "server_error", "unknown"}})}


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
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            raise ValueError("Execution envelope must be an array")
        summary = summarize(data, args.model, args.expect)
    except (OSError, ValueError, TypeError):
        summary = {"status": "NOT_RUN", "category": "unreadable_execution", "requested_model": args.model}
    Path(args.output).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    if summary["status"] != "PASS":
        reasons = {"usage_limit": "Claude reported a usage or rate limit. Restore available usage and rerun the review.",
                   "authentication_failed": "Claude rejected the repository credential. Renew CLAUDE_CODE_OAUTH_TOKEN through the account owner.",
                   "model_unavailable": "Claude rejected the selected model. Check the account model availability.",
                   "missing_result": "No completed Claude execution result was produced."}
        reason = reasons.get(summary["category"], "Claude did not complete successfully; inspect the bounded execution summary.")
        print("::error title=Claude review " + summary["category"] + "::" + reason)
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
