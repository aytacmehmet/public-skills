#!/usr/bin/env python3
"""Read-only host and Python checks. Does not install or alter host settings."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", choices=("claude", "codex", "both"), required=True)
    args = parser.parse_args()
    report = {"plugin": "yula", "checks": {}, "errors": []}
    versions = []
    for host, file in (("claude", ".claude-plugin/plugin.json"), ("codex", ".codex-plugin/plugin.json")):
        metadata = json.loads((ROOT / file).read_text(encoding="utf-8-sig"))
        versions.append(metadata["version"])
        if metadata.get("name") != "yula":
            report["errors"].append("Plugin names must agree across host manifests.")
        if args.host not in (host, "both"):
            continue
        executable = shutil.which(host)
        if not executable:
            report["errors"].append(host + " CLI is not on PATH.")
            continue
        proc = subprocess.run([executable, "--version"], capture_output=True, timeout=15)
        report["checks"][host] = {"available": proc.returncode == 0, "version": proc.stdout.decode("utf-8", errors="replace").strip()}
        if proc.returncode:
            report["errors"].append(host + " --version failed.")
    if len(set(versions)) != 1:
        report["errors"].append("Host manifest versions disagree.")
    report["version"] = versions[0]
    mcp = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8-sig"))["mcpServers"]["yula"]
    executable = shutil.which(mcp["command"])
    if executable:
        probe = "import sys,sqlite3,json; c=sqlite3.connect(':memory:'); c.execute('create virtual table t using fts5(x)'); print(json.dumps({'version':list(sys.version_info[:3]),'fts5':True})); sys.exit(0 if sys.version_info>=(3,11) else 1)"
        proc = subprocess.run([executable, "-I", "-B", "-c", probe], capture_output=True, timeout=15)
        try:
            report["checks"]["python"] = json.loads(proc.stdout)
        except ValueError:
            report["checks"]["python"] = {"available": False}
        if proc.returncode:
            report["errors"].append("The MCP launch command requires Python 3.11+ with SQLite FTS5.")
    else:
        report["errors"].append("The MCP command '" + mcp["command"] + "' is not on PATH. See references/installation.md.")
    sys.path.insert(0, str(ROOT / "runtime"))
    from yula.common import YulaError
    from yula.seed import archive_info
    try:
        manifest, archive = archive_info()
        report["checks"]["bundledDatabase"] = {"archiveVerified": True, "sqliteBytes": manifest["bytes"]}
    except (YulaError, ValueError, OSError, KeyError) as exc:
        report["checks"]["bundledDatabase"] = False
        report["errors"].append("Bundled seed archive validation failed: " + type(exc).__name__)
    report["checks"]["skills"] = len(list((ROOT / "skills").glob("*/SKILL.md")))
    if report["checks"]["skills"] != 3:
        report["errors"].append("Expected all three Yula skills.")
    report["status"] = "PASS" if not report["errors"] else "BLOCKED"
    sys.stdout.buffer.write(json.dumps(report, ensure_ascii=False, separators=(",", ":")).encode() + b"\n")
    return 0 if not report["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
