"""Build the complete offline public marketplace ZIP without modifying source."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def build(output):
    output = Path(output).resolve()
    source_tree = ROOT.parent.parent if ROOT.parent.name == "plugins" else ROOT
    if output.is_relative_to(source_tree):
        raise ValueError("Delivery artifacts must stay outside the source tree")
    paths = sorted(ROOT.rglob("*"), key=lambda path: path.relative_to(ROOT).as_posix())
    if any(path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()) for path in paths):
        raise ValueError("Unsafe package path")
    payload = {path.relative_to(ROOT).as_posix(): path.read_bytes() for path in paths
               if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc" and path != ROOT / "PACKAGE-MANIFEST.json"}
    plugin = json.loads(payload[".claude-plugin/plugin.json"])
    manifest = {"format": "plugin-package/1", "version": plugin["version"], "excluded": ["PACKAGE-MANIFEST.json"],
                "files": {name: {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)} for name, data in payload.items()}}
    manifest_bytes = encoded(manifest)
    claude = {"name": "aytacmehmet-public", "owner": {"name": "aytacmehmet"}, "plugins": [
        {"name": plugin["name"], "source": "./plugins/" + plugin["name"], "description": plugin["description"], "version": plugin["version"]}]}
    codex = {"name": "aytacmehmet-public", "interface": {"displayName": "Belirtim Yazmanı Distribution"}, "plugins": [
        {"name": plugin["name"], "source": {"source": "local", "path": "./plugins/" + plugin["name"]},
         "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Productivity"}]}
    files = {".claude-plugin/marketplace.json": encoded(claude), ".agents/plugins/marketplace.json": encoded(codex),
             "plugins/" + plugin["name"] + "/PACKAGE-MANIFEST.json": manifest_bytes}
    files.update({"plugins/" + plugin["name"] + "/" + name: data for name, data in payload.items()})
    output.mkdir(parents=True, exist_ok=True)
    (output / "PACKAGE-MANIFEST.json").write_bytes(manifest_bytes)
    destination = output / (plugin["name"] + "-" + plugin["version"] + ".zip")
    prefix = plugin["name"] + "-marketplace/"
    # Stored entries avoid compression-library differences between operating systems.
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(prefix + name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None and len(archive.namelist()) == len(files)
        assert all(archive.read(prefix + name) == data for name, data in files.items())
    return {"version": plugin["version"], "payloadFiles": len(payload), "zipEntries": len(files), "zip": destination.name,
            "bytes": destination.stat().st_size, "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(), "crcAndHashParity": "PASS"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    print(json.dumps(build(parser.parse_args().output_dir), ensure_ascii=False))
