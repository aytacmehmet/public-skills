#!/usr/bin/env python3
"""Yula entrypoint. Python 3.11+ with SQLite FTS5; no third-party runtime packages."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from yula.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
