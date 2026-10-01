#!/usr/bin/env python3
"""Build a deterministic self-contained marketplace ZIP in explicit external storage."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from yula.common import data_root, file_hash, load_json


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, help="External artifact directory; plugin source is never changed")
    args = parser.parse_args()
    output = data_root(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    plugin = load_json(ROOT / ".claude-plugin/plugin.json")
    paths = sorted(ROOT.rglob("*"))
    if any(path.is_symlink() for path in paths):
        raise ValueError("Package source cannot contain symlinks")
    files = {p.relative_to(ROOT).as_posix(): p for p in paths if p.is_file() and
             "__pycache__" not in p.parts and p.name != "PACKAGE-MANIFEST.json"}
    manifest = {"format": "yula-package/1", "version": plugin["version"], "excluded": ["PACKAGE-MANIFEST.json"],
                "files": {name: {"sha256": file_hash(path), "bytes": path.stat().st_size} for name, path in files.items()}}
    manifest_bytes = encoded(manifest)
    (output / "PACKAGE-MANIFEST.json").write_bytes(manifest_bytes)
    marketplace = {"name": "aytacmehmet-public", "owner": {"name": "aytacmehmet"},
                   "metadata": {"description": "Yula offline distribution: SAP evidence skills, MCP and the complete SQLite corpus."}, "plugins": [
        {"name": "yula", "source": "./plugins/yula", "description": plugin["description"], "version": plugin["version"]}]}
    native = {"name": marketplace["name"], "interface": {"displayName": "Yula Offline Distribution"}, "plugins": [
        {"name": "yula", "source": {"source": "local", "path": "./plugins/yula"},
         "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Productivity"}]}
    destination = output / ("yula-" + plugin["version"] + ".zip")
    prefix = "yula-marketplace/"
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        def put(name, content=None, source=None):
            info = zipfile.ZipInfo(prefix + name, date_time=(2026, 9, 23, 0, 0, 0))
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_STORED if name.endswith(".zip") else zipfile.ZIP_DEFLATED
            info._compresslevel = 9
            if source is None:
                bundle.writestr(info, content)
            else:
                with source.open("rb") as src, bundle.open(info, "w", force_zip64=True) as out:
                    shutil.copyfileobj(src, out, 1024 * 1024)
        put(".claude-plugin/marketplace.json", encoded(marketplace))
        put(".agents/plugins/marketplace.json", encoded(native))
        put("plugins/yula/PACKAGE-MANIFEST.json", manifest_bytes)
        for name, source in files.items():
            put("plugins/yula/" + name, source=source)
    with zipfile.ZipFile(destination) as bundle:
        if bundle.testzip() is not None:
            raise ValueError("Built ZIP failed CRC verification")
        for name, metadata in manifest["files"].items():
            with bundle.open(prefix + "plugins/yula/" + name) as src:
                if hashlib.file_digest(src, "sha256").hexdigest() != metadata["sha256"]:
                    raise ValueError("Built ZIP differs from source: " + name)
    print(json.dumps({"version": plugin["version"], "files": len(files) + 1,
                      "zip": destination.name, "bytes": destination.stat().st_size,
                      "sha256": file_hash(destination), "crcAndHashParity": "PASS"}, separators=(",", ":")))


if __name__ == "__main__":
    main()
