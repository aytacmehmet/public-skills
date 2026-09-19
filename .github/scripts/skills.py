"""Validate bilingual skill packages, archive committed releases, and export a package for another host."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote
import zipfile

import yaml


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = "ARCHIVE-MANIFEST.json"
SKILL_PATH = re.compile(r"^(en|tr)/[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
INVOCATION = re.compile(r"(?<![\w$/\\.-])\$([a-z0-9]+(?:-[a-z0-9]+)*)(?![\w-])")
REQUIRED = (
    "SKILL.md", "README.md", "CHANGELOG.md", "LICENSE",
    "agents/openai.yaml", "archived/README.md",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(root, *args):
    result = subprocess.run(
        ["git", *args], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False,
    )
    require(result.returncode == 0, result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def resolve_ref(root, ref):
    require(ref and not ref.startswith("-"), "Expected a Git commit, branch, or tag.")
    return git(root, "rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()


def checked_path(root, relative):
    require(SKILL_PATH.fullmatch(relative), f"Invalid skill path: {relative}")
    target = root / relative
    require(target.resolve().is_relative_to(root.resolve()), "Skill path leaves the repository.")
    require(not target.is_symlink(), "Skill directories must not be symlinks.")
    return target


def version_tuple(value):
    require(isinstance(value, str) and VERSION.fullmatch(value), f"Invalid version: {value!r}")
    return tuple(map(int, value.split(".")))


def frontmatter(data):
    text = data.decode("utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    require(match is not None, "SKILL.md requires YAML frontmatter.")
    parsed = yaml.safe_load(match.group(1))
    require(isinstance(parsed, dict), "Frontmatter must be a mapping.")
    return parsed


def tracked_paths(root, commit, prefix):
    records = git(root, "ls-tree", "-r", "-z", commit, "--", prefix).split(b"\0")
    paths = []
    for record in filter(None, records):
        header, path = record.split(b"\t", 1)
        mode, kind, _ = header.decode().split()
        name = path.decode("utf-8")
        require(kind == "blob" and mode in ("100644", "100755"), f"Unsupported Git entry: {name}")
        paths.append(name)
    return paths


def committed_payload(root, relative, commit):
    checked_path(root, relative)
    prefix = relative + "/"
    result = {}
    for path in tracked_paths(root, commit, relative):
        local = path.removeprefix(prefix)
        if local.startswith("archived/"):
            continue
        result[local] = git(root, "show", f"{commit}:{path}")
    require("SKILL.md" in result, f"No committed skill at {relative} in {commit}.")
    return result


def working_payload(folder):
    result = {}
    for item in folder.rglob("*"):
        local = item.relative_to(folder).as_posix()
        if local.startswith("archived/"):
            continue
        require(not item.is_symlink(), f"Package symlinks are unsupported: {item}")
        if item.is_file():
            result[local] = item.read_bytes()
    return result


def archive(root, relative, ref="HEAD"):
    folder = checked_path(root, relative)
    require(folder.is_dir(), f"Missing skill folder: {relative}")
    commit = resolve_ref(root, ref)
    payload = committed_payload(root, relative, commit)
    meta = frontmatter(payload["SKILL.md"])
    version = meta["metadata"]["version"]
    version_tuple(version)
    require(meta["name"] == folder.name, "Committed skill name does not match its folder.")
    archive_dir = folder / "archived"
    require(archive_dir.is_dir() and not archive_dir.is_symlink(), "A real archived/ directory is required.")
    destination = archive_dir / f"v{version}.zip"
    require(not destination.exists(), f"Archive already exists and is immutable: {destination}")
    require(MANIFEST not in payload, f"{MANIFEST} is reserved for snapshots.")
    manifest = {
        "schema_version": 1,
        "skill_path": relative,
        "name": meta["name"],
        "version": version,
        "source_commit": commit,
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(payload.items())},
    }
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as target:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            target.writestr(info, data)
        target.writestr(MANIFEST, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    read_archive(destination)
    return destination


def export(root, relative, destination, name=None, overlay=None):
    """Copy the active package for another host; downstream copies are produced, never edited by hand."""
    folder = checked_path(root, relative)
    require(folder.is_dir(), f"Missing skill folder: {relative}")
    destination = Path(destination).resolve()
    require(not destination.is_relative_to(root.resolve()), "Export outside this repository: an exported copy is not a package here.")
    require(not destination.exists() or not any(destination.iterdir()), f"Export destination is not empty: {destination}")
    source_name = folder.name
    name = name or source_name
    require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) and len(name) <= 64, f"Invalid skill name: {name}")
    payload = working_payload(folder)
    meta = frontmatter(payload["SKILL.md"])
    skill = payload["SKILL.md"].decode("utf-8")
    if name != source_name:
        skill = re.sub(rf"(?m)^name: {re.escape(source_name)}$", f"name: {name}", skill, count=1)
        payload["agents/openai.yaml"] = payload["agents/openai.yaml"].decode("utf-8").replace(f"${source_name}", f"${name}").encode("utf-8")
    if overlay:
        skill = skill.rstrip("\n") + "\n\n" + Path(overlay).read_text(encoding="utf-8").strip("\n") + "\n"
    payload["SKILL.md"] = skill.encode("utf-8")
    require(frontmatter(payload["SKILL.md"])["name"] == name, "Exported SKILL.md lost its name.")
    dirty = bool(git(root, "status", "--porcelain", "--", relative).strip())
    payload["EXPORT-MANIFEST.json"] = (json.dumps({
        "schema_version": 1, "source": relative, "source_name": source_name, "name": name,
        "version": meta["metadata"]["version"], "source_commit": resolve_ref(root, "HEAD"),
        "uncommitted_changes": dirty, "overlay": Path(overlay).name if overlay else None,
    }, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    for local, data in sorted(payload.items()):
        target = destination / local
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    shutil.rmtree(destination / "__pycache__", ignore_errors=True)
    return destination


def read_archive(path):
    with zipfile.ZipFile(path) as source:
        names = source.namelist()
        require(len(names) == len(set(names)), f"Duplicate ZIP entries: {path}")
        for name in names:
            parts = PurePosixPath(name)
            require(
                name and parts.parts and ":" not in parts.parts[0]
                and not name.startswith("/") and "\\" not in name
                and ".." not in parts.parts and not name.endswith("/")
                and parts.parts[0] != "archived",
                f"Invalid snapshot entry: {name}",
            )
        require(MANIFEST in names and "SKILL.md" in names, f"Incomplete snapshot: {path}")
        manifest = json.loads(source.read(MANIFEST))
        require(manifest.get("schema_version") == 1, "Unsupported archive manifest version.")
        payload = {name: source.read(name) for name in names if name != MANIFEST}
    hashes = {name: hashlib.sha256(data).hexdigest() for name, data in payload.items()}
    require(hashes == manifest.get("files"), f"Snapshot hashes do not match: {path}")
    meta = frontmatter(payload["SKILL.md"])
    require(meta["name"] == manifest.get("name"), "Archive name mismatch.")
    require(meta["metadata"]["version"] == manifest.get("version"), "Archive version mismatch.")
    return manifest, payload


def validate_links(root):
    for path in root.rglob("*.md"):
        if ".git" in path.relative_to(root).parts:
            continue
        text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
        for raw in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", text):
            link = raw.strip().strip("<>")
            if link.startswith(("https://", "http://", "mailto:", "#")):
                continue
            target = (path.parent / unquote(link.split("#", 1)[0])).resolve()
            require(target.is_relative_to(root.resolve()) and target.exists(), f"Broken local link in {path}: {link}")


def validate(root, base=None):
    root = root.resolve()
    skills = {}
    for language in ("en", "tr"):
        require((root / language / "README.md").is_file(), f"Missing {language} catalog.")
        # Every directory immediately under a language root is a package.
        # Discovering only SKILL.md would silently omit incomplete packages.
        for folder in sorted(p for p in (root / language).iterdir() if p.is_dir()):
            skill_file = folder / "SKILL.md"
            relative = folder.relative_to(root).as_posix()
            checked_path(root, relative)
            for name in REQUIRED:
                require((folder / name).is_file(), f"{relative}: missing {name}")
            meta = frontmatter(skill_file.read_bytes())
            require(meta.get("name") == folder.name and len(folder.name) <= 64, f"Invalid name: {relative}")
            description = meta.get("description")
            require(isinstance(description, str) and 0 < len(description) <= 1024, f"Invalid description: {relative}")
            version = meta.get("metadata", {}).get("version")
            version_tuple(version)
            require(meta["metadata"].get("language") == language, f"Wrong language: {relative}")
            require(meta["metadata"].get("family"), f"Missing translation family: {relative}")
            require(version in (folder / "CHANGELOG.md").read_text(encoding="utf-8"), f"Missing changelog version: {relative}")
            ui = yaml.safe_load((folder / "agents/openai.yaml").read_text(encoding="utf-8"))["interface"]
            require(25 <= len(ui["short_description"]) <= 64, f"Invalid UI description: {relative}")
            prompt = ui.get("default_prompt")
            require(isinstance(prompt, str) and folder.name in INVOCATION.findall(prompt), f"Invalid default invocation: {relative}")
            require((folder / "LICENSE").read_bytes() == (root / "LICENSE").read_bytes(), f"License differs: {relative}")
            working_payload(folder)
            archives = folder / "archived"
            require(not archives.is_symlink(), "archived/ must not be a symlink.")
            for item in archives.iterdir():
                if item.name == "README.md":
                    continue
                require(item.is_file() and not item.is_symlink() and item.suffix == ".zip", f"Only ZIP snapshots are allowed in {archives}")
                manifest, _ = read_archive(item)
                require(manifest["skill_path"] == relative, f"Wrong archive owner: {item}")
                require(item.name == f"v{manifest['version']}.zip", f"Wrong archive filename: {item}")
                require(version_tuple(manifest["version"]) < version_tuple(version), f"Archive must precede current version: {item}")
            skills[relative] = meta
    require(skills, "No skills found.")
    active = {str((root / relative / "SKILL.md").resolve()) for relative in skills}
    require(all(str(p.resolve()) in active for p in root.rglob("SKILL.md")), "Unexpected nested SKILL.md; keep old versions zipped.")
    for relative, meta in skills.items():
        pair = meta["metadata"].get("counterpart")
        require(pair in skills, f"Missing language counterpart: {relative}")
        other = skills[pair]["metadata"]
        require(other.get("counterpart") == relative, f"Non-reciprocal counterpart: {relative}")
        require(other["language"] != meta["metadata"]["language"], f"Counterpart must use the other language: {relative}")
        require(other["family"] == meta["metadata"]["family"], f"Translation family mismatch: {relative}")
        require(other["version"] == meta["metadata"]["version"], f"Translation version mismatch: {relative}")
    validate_links(root)
    if base:
        validate_history(root, skills, resolve_ref(root, base))
    return len(skills)


def validate_history(root, skills, base):
    for language in ("en", "tr"):
        paths = tracked_paths(root, base, language)
        previous = {str(PurePosixPath(p).parent) for p in paths if len(PurePosixPath(p).parts) == 3 and p.endswith("/SKILL.md")}
        for relative in sorted(previous):
            require(relative in skills, f"Previously published skill was removed: {relative}")
            before = committed_payload(root, relative, base)
            after = working_payload(root / relative)
            if before != after:
                old_version = frontmatter(before["SKILL.md"])["metadata"]["version"]
                new_version = skills[relative]["metadata"]["version"]
                require(version_tuple(new_version) > version_tuple(old_version), f"Changed package needs a version bump: {relative}")
                snapshot = root / relative / "archived" / f"v{old_version}.zip"
                require(snapshot.is_file(), f"Archive previous version first: {snapshot}")
                _, payload = read_archive(snapshot)
                require(payload == before, f"Archive does not match the previous committed package: {snapshot}")
        for path in paths:
            parts = PurePosixPath(path).parts
            if len(parts) == 4 and parts[2] == "archived" and path.endswith(".zip"):
                current = root / path
                require(current.is_file() and current.read_bytes() == git(root, "show", f"{base}:{path}"), f"Published archive changed or was removed: {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    checker = commands.add_parser("validate", help="Validate packages and optional release history.")
    checker.add_argument("--base", help="Compare packages with this commit, branch, or tag.")
    archiver = commands.add_parser("archive", help="Snapshot a committed version without editing the active package.")
    archiver.add_argument("skill", help="For example, en/prompter or tr/yordamla.")
    archiver.add_argument("--ref", default="HEAD", help="Committed source; defaults to HEAD, never uncommitted files.")
    exporter = commands.add_parser("export", help="Produce a copy of an active package for another host.")
    exporter.add_argument("skill", help="For example, tr/sap-fiori-tasarim.")
    exporter.add_argument("--dest", required=True, help="Empty or new folder outside this repository.")
    exporter.add_argument("--name", help="Skill name on the target host; defaults to the folder name.")
    exporter.add_argument("--overlay", help="Markdown file with host-specific rules, appended to SKILL.md.")
    args = parser.parse_args()
    try:
        if args.command == "export":
            print(f"Exported: {export(ROOT, args.skill, args.dest, args.name, args.overlay)}")
        elif args.command == "archive":
            print(f"Archived: {archive(ROOT, args.skill, args.ref).relative_to(ROOT).as_posix()}")
        else:
            print(f"PASS: {validate(ROOT, args.base)} active skill packages; structure, links, language pairing, and archives validated.")
    except (ValueError, KeyError, TypeError, OSError, yaml.YAMLError, zipfile.BadZipFile) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
