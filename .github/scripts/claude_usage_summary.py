"""Read OAuth quota buckets without printing credentials, identity or response bodies."""
import json
import os
import urllib.error
import urllib.request

request = urllib.request.Request("https://api.anthropic.com/api/oauth/usage", headers={
    "Authorization": "Bearer " + os.environ["CLAUDE_CODE_OAUTH_TOKEN"],
    "anthropic-beta": "oauth-2025-04-20", "User-Agent": "claude-review-diagnostic/1"})
try:
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.load(response)
    buckets = {}
    for key in ("five_hour", "seven_day", "seven_day_sonnet", "seven_day_opus"):
        value = data.get(key)
        if isinstance(value, dict):
            reset = value.get("resets_at")
            utilization = value.get("utilization")
            buckets[key] = {"utilization": utilization if isinstance(utilization, (int, float)) else None,
                            "resets_at": reset if isinstance(reset, str) and len(reset) <= 40 else None}
    print(json.dumps({"status": "PASS", "buckets": buckets}))
except urllib.error.HTTPError as error:
    print(json.dumps({"status": "UNAVAILABLE", "http_status": error.code}))
except (OSError, ValueError):
    print(json.dumps({"status": "UNAVAILABLE", "category": "usage_endpoint_error"}))
