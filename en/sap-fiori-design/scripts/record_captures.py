#!/usr/bin/env python3
"""Record the SHA-256 and size of reviewed PNG captures in <delivery-root>/visuals/capture-report.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SIGNATURE = b"\x89PNG\r\n\x1a\n"


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="backslashreplace")


def record(root: Path, ui5_version: str | None) -> dict:
    root = root.resolve()
    if root == SKILL_ROOT or SKILL_ROOT in root.parents:
        raise ValueError("Record captures in a delivery folder outside the skill")
    visuals = root / "visuals"
    captures = sorted(visuals.glob("*.png")) if visuals.is_dir() else []
    if not captures:
        raise ValueError(f"No PNG capture in {visuals}")
    rows = []
    for path in captures:
        data = path.read_bytes()
        if len(data) < 24 or data[:8] != SIGNATURE or data[12:16] != b"IHDR":
            raise ValueError(f"Not a valid PNG: {path.name}")
        width, height = struct.unpack(">II", data[16:24])
        rows.append({"file": path.name, "sha256": hashlib.sha256(data).hexdigest(), "width": width, "height": height})
    app_id = "unknown"
    contract = root / "design-contract.json"
    if contract.is_file():
        try:
            app_id = json.loads(contract.read_text(encoding="utf-8")).get("project", {}).get("id") or "unknown"
        except (json.JSONDecodeError, AttributeError):
            app_id = "unknown"
    report = {
        "schemaVersion": 1,
        "appId": app_id,
        "prototypeUi5Version": ui5_version or "unknown",
        "scope": "Reviewed local prototype captures; not tenant, role or accessibility-conformance evidence",
        "files": rows,
    }
    (visuals / "capture-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


def main() -> int:
    configure_stdio()
    parser = argparse.ArgumentParser(description="Record reviewed PNG captures so the delivery gate can detect later changes")
    parser.add_argument("root", type=Path, help="Delivery root that contains visuals/")
    parser.add_argument("--ui5-version", help="SAPUI5 version the running prototype reported (sap.ui.version)")
    parser.add_argument("--json", action="store_true", help="Print the report")
    args = parser.parse_args()
    try:
        report = record(args.root, args.ui5_version)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Recorded {len(report['files'])} capture(s): {args.root.resolve() / 'visuals' / 'capture-report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
