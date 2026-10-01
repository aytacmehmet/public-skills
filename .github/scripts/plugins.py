"""Validate complete plugins without weakening standalone skill discovery."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

import yaml

NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
VERSION = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")
REQUIRED = ("README.md", "README.tr.md", "CHANGELOG.md", "CHANGELOG.tr.md", "LICENSE",
            ".claude-plugin/plugin.json", ".codex-plugin/plugin.json", "PACKAGE-MANIFEST.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def version_tuple(version):
    require(isinstance(version, str) and VERSION.fullmatch(version), "Invalid plugin version")
    return tuple(map(int, version.split(".")))


def git(root, *args):
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=False)
    require(result.returncode == 0, result.stderr.decode("utf-8", errors="replace"))
    return result.stdout


def validate_plugins(root, base=None):
    root = Path(root).resolve()
    plugin_root = root / "plugins"
    marketplace_paths = (root / ".claude-plugin/marketplace.json", root / ".agents/plugins/marketplace.json")
    previous = set()
    records = []
    if base:
        require(base and not base.startswith("-"), "Invalid base revision")
        commit = git(root, "rev-parse", "--verify", f"{base}^{{commit}}").decode().strip()
        records = git(root, "ls-tree", "-r", "--name-only", commit, "--", "plugins").decode().splitlines()
        previous = {path.split("/")[1] for path in records if re.fullmatch(r"plugins/[^/]+/\.claude-plugin/plugin\.json", path)}
    if not plugin_root.exists() and not any(path.exists() for path in marketplace_paths):
        require(not previous, "Previously published plugin removed")
        return set()
    require(plugin_root.is_dir() and not plugin_root.is_symlink() and plugin_root.resolve().is_relative_to(root), "Missing real plugins directory")
    folders = sorted(plugin_root.iterdir())
    require(folders, "Empty plugins directory")
    for folder in folders:
        require(folder.is_dir() and not folder.is_symlink() and folder.resolve().is_relative_to(plugin_root.resolve()) and NAME.fullmatch(folder.name), "Invalid plugin directory")
    names = {folder.name for folder in folders}
    for path in marketplace_paths:
        require(path.is_file() and not path.is_symlink(), f"Missing marketplace: {path}")
    claude, codex = map(read, marketplace_paths)
    require(claude.get("name") == codex.get("name") == "aytacmehmet-public", "Marketplace names differ")
    entries = {}
    for host, marketplace in (("claude", claude), ("codex", codex)):
        plugins = marketplace.get("plugins", [])
        require(isinstance(plugins, list) and len(plugins) == len(names), "Marketplace plugin count mismatch")
        entries[host] = {entry["name"]: entry for entry in plugins}
        require(set(entries[host]) == names, "Unregistered or duplicate marketplace plugin")

    skill_paths = set()
    for folder in folders:
        label = "plugins/" + folder.name
        for item in folder.rglob("*"):
            require(not item.is_symlink() and item.resolve().is_relative_to(folder.resolve()), f"Unsafe package entry: {label}")
        for relative in REQUIRED:
            require((folder / relative).is_file(), f"{label}: missing {relative}")
        plugin, native = (read(folder / f".{host}-plugin/plugin.json") for host in ("claude", "codex"))
        version = plugin.get("version")
        version_tuple(version)
        require(plugin.get("name") == native.get("name") == folder.name and native.get("version") == version, "Host manifests differ")
        require((folder / "LICENSE").read_bytes() == (root / "LICENSE").read_bytes(), "Plugin license differs")
        for language in ("", ".tr"):
            for kind in ("README", "CHANGELOG"):
                require(version in (folder / f"{kind}{language}.md").read_text(encoding="utf-8"), "Missing localized release version")
        for host in ("claude", "codex"):
            entry = entries[host][folder.name]
            source = f"./plugins/{folder.name}"
            expected = source if host == "claude" else {"source": "local", "path": source}
            require(entry.get("source") == expected, "Marketplace source differs")
            if host == "claude":
                require(entry.get("version") == version, "Marketplace version differs")
            else:
                require(entry.get("policy") == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "Marketplace policy differs")
        for catalog in ("README.md", "en/README.md", "tr/README.md"):
            require("plugins/" + folder.name + "/README" in (root / catalog).read_text(encoding="utf-8"), f"Missing plugin catalog entry: {catalog}")
        manifest = read(folder / "PACKAGE-MANIFEST.json")
        payload = {p.relative_to(folder).as_posix(): p for p in folder.rglob("*") if p.is_file() and p != folder / "PACKAGE-MANIFEST.json"}
        require(manifest.get("version") == version and set(manifest.get("files", {})) == set(payload), "Plugin package manifest inventory differs")
        for name, path in payload.items():
            metadata = manifest["files"][name]
            require(metadata == {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}, f"Plugin hash/size mismatch: {name}")
        skills_dir = folder / "skills"
        require(skills_dir.is_dir(), "Missing plugin skills directory")
        skill_folders = sorted(skills_dir.iterdir())
        require(skill_folders, "Plugin must contain skills")
        for skill in skill_folders:
            require(skill.is_dir() and NAME.fullmatch(skill.name), "Invalid plugin skill directory")
            for relative in ("SKILL.md", "README.md", "README.tr.md", "agents/openai.yaml"):
                require((skill / relative).is_file(), f"Incomplete plugin skill: {skill.name}")
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
            require(match, "Missing plugin skill frontmatter")
            metadata = yaml.safe_load(match.group(1))
            require(metadata.get("name") == skill.name and metadata.get("metadata", {}).get("version") == version, "Plugin skill version/name differs")
            require(isinstance(metadata.get("description"), str) and 0 < len(metadata["description"]) <= 1024, "Invalid plugin skill description")
            ui = yaml.safe_load((skill / "agents/openai.yaml").read_text(encoding="utf-8"))["interface"]
            require(25 <= len(ui["short_description"]) <= 64, "Invalid plugin skill UI description")
            require(re.search(r"(?<![\w$/.-])\$" + re.escape(skill.name) + r"(?![\w-])", ui.get("default_prompt", "")), "Invalid plugin skill invocation")
            skill_paths.add(str((skill / "SKILL.md").resolve()))
        require({str(path.resolve()) for path in folder.rglob("SKILL.md")} <= skill_paths, "Unexpected nested plugin skill")
    if base:
        require(previous <= names, "Previously published plugin removed")
        for name in previous:
            prefix = f"plugins/{name}/"
            old = {p.removeprefix(prefix): git(root, "show", f"{commit}:{p}") for p in records if p.startswith(prefix)}
            new = {p.relative_to(plugin_root / name).as_posix(): p.read_bytes() for p in (plugin_root / name).rglob("*") if p.is_file()}
            if old != new:
                before = json.loads(old[".claude-plugin/plugin.json"])["version"]
                after = read(plugin_root / name / ".claude-plugin/plugin.json")["version"]
                require(version_tuple(after) > version_tuple(before), "Changed plugin needs a version bump")
    return skill_paths
