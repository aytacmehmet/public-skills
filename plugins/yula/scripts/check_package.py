#!/usr/bin/env python3
"""Verify package hashes, dual-host metadata and the decoded SQLite seed."""
import argparse
import json
from pathlib import Path
import re
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from yula import VERSION
from yula.common import data_root, file_hash, load_json, validate_database
from yula.seed import unpack_seed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", required=True, help="External temporary validation directory")
    args = parser.parse_args()
    work = data_root(args.work_dir)
    work.mkdir(parents=True, exist_ok=True)
    manifest = load_json(ROOT / "PACKAGE-MANIFEST.json")
    assert manifest["version"] == VERSION
    files = {p.relative_to(ROOT).as_posix(): p for p in ROOT.rglob("*") if p.is_file()}
    assert set(manifest["files"]) == set(files) - {"PACKAGE-MANIFEST.json"}, "Unlisted/missing package file"
    for name, expected in manifest["files"].items():
        assert files[name].stat().st_size == expected["bytes"], name + ": size mismatch"
        assert file_hash(files[name]) == expected["sha256"], name + ": hash mismatch"
    for host in ("claude", "codex"):
        plugin = load_json(ROOT / ("." + host + "-plugin/plugin.json"))
        assert (plugin["name"], plugin["version"]) == ("yula", VERSION)
    skills = list((ROOT / "skills").glob("*/SKILL.md"))
    assert len(skills) == 3
    for skill in skills:
        assert '  version: "' + VERSION + '"' in skill.read_text(encoding="utf-8")
        for readme in ("README.md", "README.tr.md"):
            assert (skill.parent / readme).is_file()
    assert not (ROOT / ".claude-plugin/marketplace.json").exists(), "Marketplace belongs to repository root"
    mcp = load_json(ROOT / ".mcp.json")["mcpServers"]["yula"]
    assert mcp["args"][-3:] == ["--data-root", "@user/yula", "mcp"]
    # Codex does not expand ${CLAUDE_PLUGIN_ROOT}; it resolves "cwd" against the installed plugin root.
    codex = load_json(ROOT / ".codex-plugin/plugin.json")["mcpServers"]["yula"]
    assert codex["args"] == [arg.replace("${CLAUDE_PLUGIN_ROOT}/", "./") for arg in mcp["args"]], "Codex MCP arguments differ"
    assert (codex["command"], codex["cwd"]) == (mcp["command"], ".") and "${" not in json.dumps(codex), "Codex MCP must start from the plugin root"
    assert "YULA_DATA_ROOT" in codex["env_vars"], "Codex must forward YULA_DATA_ROOT"
    # Scan the decoded artifact too; compression must not bypass repository secret checks.
    secret = re.compile(rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|AKIA[A-Z0-9]{16}|sk-(?:proj-|ant-)?[A-Za-z0-9_-]{30,}|xox[baprs]-[A-Za-z0-9-]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")
    private_path = re.compile(rb"(?:[A-Za-z]:[\\/]Users[\\/]|/Users/|/home/)[A-Za-z0-9_-]{2,}")
    with tempfile.TemporaryDirectory(prefix="yula-check-", dir=work) as temp:
        with unpack_seed(temp) as database:
            with database.open("rb") as stream:
                previous = b""
                while chunk := stream.read(1024 * 1024):
                    block = previous + chunk
                    assert not secret.search(block), "Possible credential in seed (value not shown)"
                    for match in private_path.finditer(block):
                        # SAP Help's ODBC setup example uses this literal placeholder path.
                        sample = b"/home/myuser/.odbc.ini"
                        assert block[match.start():match.start() + len(sample)] == sample, "Private workstation path in seed (value not shown)"
                    previous = block[-4096:]
            counts = validate_database(database, full=True)
    print(json.dumps({"status": "LOCAL_PASS", "version": VERSION, "files": len(files),
                      "skills": len(skills), "seedHash": load_json(ROOT / "data/manifest.json")["sha256"],
                      "sqliteIntegrity": "PASS", "decodedSecretScan": "PASS", "counts": counts}, separators=(",", ":")))


if __name__ == "__main__":
    main()
