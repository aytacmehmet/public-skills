from __future__ import annotations
import argparse
import json
import sqlite3
import sys

from .common import YulaError, data_root, encode


def main(argv=None):
    parser = argparse.ArgumentParser(prog="yula")
    parser.add_argument("--data-root", help="External corpus directory or @user/yula; otherwise requires YULA_DATA_ROOT")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("mcp", help="Start the read-only stdio MCP server")
    sub.add_parser("init", help="Seed an empty data root; preserve an existing installation")
    sub.add_parser("status", help="Source freshness and corpus coverage")
    sub.add_parser("migrate", help="Stage the additive storage revision; publish with apply --plan/--hash")
    sub.add_parser("doctor", help="Validate active snapshot hash, schema and SQLite integrity")
    p = sub.add_parser("check", help="Fetch/validate selected sources and stage a hash-bound update plan")
    p.add_argument("--config"); p.add_argument("--source", action="append", dest="sources")
    p = sub.add_parser("apply", help="Publish a checked plan atomically")
    p.add_argument("--plan", required=True); p.add_argument("--hash", required=True)
    p = sub.add_parser("rollback", help="Atomically restore a verified immutable backup")
    p.add_argument("--expected-active", required=True); p.add_argument("--to")
    p = sub.add_parser("query", help="Call a read tool using a JSON argument object")
    p.add_argument("tool", choices=["yula_search", "yula_get", "yula_check", "yula_status"])
    p.add_argument("--json", default="{}"); p.add_argument("--input", help="UTF-8 JSON file instead of shell JSON")
    args = parser.parse_args(argv)
    try:
        root = data_root(args.data_root)
        from . import mcp, snapshots, updates
        if args.command == "mcp":
            mcp.serve(root); return 0
        if args.command == "init":
            result = snapshots.init(root)
        elif args.command in ("status", "doctor"):
            result = snapshots.status(root, verify=args.command == "doctor")
        elif args.command == "migrate":
            from .migrations import prepare
            result = prepare(root)
        elif args.command == "check":
            result = updates.check(root, args.config, args.sources)
        elif args.command == "apply":
            result = snapshots.apply(root, args.plan, args.hash)
        elif args.command == "rollback":
            result = snapshots.rollback(root, args.expected_active, args.to)
        else:
            from .common import load_json
            arguments = load_json(args.input) if args.input else json.loads(args.json)
            result = mcp.call(root, args.tool, arguments)
        sys.stdout.buffer.write(encode(result) + b"\n")
        return 0
    except YulaError as exc:
        sys.stdout.buffer.write(encode(exc.result()) + b"\n"); return 2
    except (ValueError, OSError, sqlite3.Error, KeyError, TypeError) as exc:
        # Error type is useful without echoing private paths, request payloads or credentials.
        sys.stdout.buffer.write(encode({"error": type(exc).__name__, "message": "Local input or database operation failed; check configured source format and access."}) + b"\n")
        return 2
