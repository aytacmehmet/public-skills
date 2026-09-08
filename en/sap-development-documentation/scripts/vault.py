#!/usr/bin/env python3
"""Project-scoped Obsidian documentation helpers. Python 3.12+, PyYAML 6.x."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
from string import Template
import sys
import uuid

import yaml

ASSETS = Path(__file__).resolve().parent.parent / "assets"
CORE = {"overview": "Overview", "current-state": "Current-State", "history": "History", "open-items": "Open-Items"}
DETAIL = {k.lower(): k for k in ("Design", "Process", "Objects", "UI", "Verification", "Sources", "Handover")}
STATES = ("planned", "active", "blocked", "review", "done", "archived")
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".obsidian"}
WIKI = re.compile(r"(!?)\[\[([^\]\n]+)\]\]")
ID = re.compile(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*\Z")
RESERVED = re.compile(r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?\Z", re.I)


class VaultError(ValueError):
    pass


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise VaultError(f"Duplicate YAML property: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def js(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def is_link(path):
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def safe(root, rel):
    """Reject lexical escapes and linked directories before reading or writing."""
    rel = str(rel)
    if not rel or "\\" in rel or rel.startswith("/"):
        raise VaultError(f"Use a root-relative path with forward slashes: {rel}")
    parts = rel.split("/")
    for part in parts:
        if part in ("", ".", "..") or re.search(r'[<>:"|?*\x00-\x1f]', part) or part.endswith((".", " ")) or RESERVED.fullmatch(part):
            raise VaultError(f"Unsafe path component: {part!r}")
    current = root
    for part in parts:
        current = current / part
        if is_link(current):
            raise VaultError(f"Linked path is not supported: {current}")
    if not current.resolve().is_relative_to(root.resolve()):
        raise VaultError(f"Path leaves the selected root: {rel}")
    return current


def walk(root):
    if not root.exists():
        return
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not is_link(Path(base) / d))
        for name in sorted(files):
            path = Path(base) / name
            if not is_link(path):
                yield path


def unpack(text):
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise VaultError("Missing YAML frontmatter")
    meta = yaml.load(match[1], Loader=UniqueLoader)
    if not isinstance(meta, dict):
        raise VaultError("Frontmatter must be a mapping")
    return meta, text[match.end():]


def pack(meta, body):
    return "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=120).rstrip() + "\n---\n" + body


def block(text, name, content):
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if text.count(start) != 1 or text.count(end) != 1 or text.index(start) > text.index(end):
        raise VaultError(f"Missing or duplicate managed block: {name}")
    a, b = text.index(start) + len(start), text.index(end)
    return text[:a] + "\n" + content.rstrip() + "\n" + text[b:]


def wikilink(path, label=None):
    target = str(path).removesuffix(".md")
    return f"[[{target}{'|' + label if label else ''}]]"


def wiki_target(value):
    match = WIKI.fullmatch(value)
    if not match or match[1]:
        raise VaultError(f"Expected a note wikilink: {value}")
    target = match[2].replace("\\|", "|").split("|", 1)[0].split("#", 1)[0]
    return target if target.endswith(".md") else target + ".md"


class Vault:
    def __init__(self, project):
        self.project = Path(project).resolve(strict=True)
        if not self.project.is_dir() or self.project.name.lower() == "obsidian":
            raise VaultError("Select the project directory, not the Obsidian Vault")
        if any((p / "vault.json").is_file() and p.name.lower() == "obsidian" for p in self.project.parents):
            raise VaultError("Nested projects inside an existing documentation Vault are not supported")
        self.root = safe(self.project, "obsidian")
        self.changes = {}
        self.before = {}

    def path(self, rel):
        return safe(self.root, rel)

    def read(self, rel):
        path = self.path(rel)
        data = self.changes.get(path, path.read_bytes() if path.exists() else None)
        if data is None:
            raise VaultError(f"Missing file: {rel}")
        return data.decode("utf-8-sig").replace("\r\n", "\n")

    def write(self, rel, content, create=False):
        if isinstance(content, str) and rel.endswith(".md") and not rel.startswith(("templates/", "assets/")) and self.path(rel).exists():
            if content != self.read(rel):
                content = re.sub(r"(?m)^updated: .+$", "updated: " + now()[:10], content, count=1)
        self.stage(self.path(rel), content.encode("utf-8") if isinstance(content, str) else content, create)

    def stage(self, path, data, create=False):
        previous = self.changes.get(path, path.read_bytes() if path.exists() else None)
        if previous == data:
            return
        if create and previous is not None:
            raise VaultError(f"Existing content differs; inspect before adopting: {path}")
        if path not in self.before:
            self.before[path] = path.read_bytes() if path.exists() else None
        self.changes[path] = data

    def config(self):
        config = json.loads(self.read("vault.json"))
        if config.get("schema_version") != 1 or config.get("language") != "en":
            raise VaultError("Unsupported Vault schema or language; inspect before migration")
        return config

    def notes(self):
        paths = {p.relative_to(self.root).as_posix() for p in walk(self.root) if p.suffix == ".md"}
        paths.update(p.relative_to(self.root).as_posix() for p in self.changes if p.is_relative_to(self.root) and p.suffix == ".md")
        return sorted(p for p in paths if not p.startswith(("templates/", "assets/")))

    def entities(self):
        result = {}
        for rel in self.notes():
            if not rel.endswith("/Overview.md"):
                continue
            meta, _ = unpack(self.read(rel))
            if meta.get("kind") not in ("development", "shared", "architecture"):
                continue
            key = meta.get("entity")
            if not isinstance(key, str) or not ID.fullmatch(key) or key in result:
                raise VaultError(f"Invalid or duplicate entity: {key}")
            result[key] = {"path": rel, **meta}
        return result

    def entity(self, key):
        entities = self.entities()
        if key not in entities:
            raise VaultError(f"Unknown entity: {key}")
        return entities[key]

    def note(self, folder, key, name, title, kind, extra=None):
        rel = f"{folder}/{name}.md"
        template_name = "Decision" if name.startswith("decisions/") else name
        body = Template((ASSETS / "templates" / f"{template_name}.md").read_text(encoding="utf-8")).substitute(title=title, entity_id=key)
        nav = " · ".join((wikilink("Home", "Home"), wikilink("Development-Index", "Developments"), wikilink(f"{folder}/Overview", key), wikilink(f"{folder}/Current-State", "Current state")))
        meta = {"id": f"{key}.{name.replace('/', '.').lower()}", "entity": key, "kind": kind, "updated": now()[:10]}
        meta.update(extra or {})
        return rel, pack(meta, nav + "\n\n" + body)

    def reindex(self):
        entities = self.entities()
        note_paths = self.notes()
        for key, item in entities.items():
            folder = item["path"].rsplit("/", 1)[0]
            text = self.read(item["path"])
            children = [p for p in note_paths if p.startswith(folder + "/") and p != item["path"]]
            text = block(text, "pages", "\n".join("- " + wikilink(p, p.removesuffix(".md").rsplit("/", 1)[-1]) for p in children) or "No additional pages.")
            deps = item.get("dependencies", [])
            if not isinstance(deps, list) or not all(isinstance(d, str) for d in deps):
                raise VaultError(f"Dependencies must be a list of wikilinks: {key}")
            consumers = [other for other in entities.values() if item["path"] in [wiki_target(d) for d in other.get("dependencies", [])]]
            text = block(text, "relations", "Dependencies: " + (", ".join(deps) or "None recorded.") + "\n\nConsumers: " + (", ".join(wikilink(c["path"], c["entity"]) for c in consumers) or "None recorded."))
            self.write(item["path"], text)
        for kind, rel in (("development", "Development-Index.md"), ("shared", "Shared-Index.md")):
            rows = []
            for key, item in sorted(entities.items()):
                if item["kind"] != kind:
                    continue
                folder = item["path"].rsplit("/", 1)[0]
                state, _ = unpack(self.read(f"{folder}/Current-State.md"))
                link = wikilink(item["path"], key).replace("|", "\\|")
                current = wikilink(f"{folder}/Current-State", "Resume").replace("|", "\\|")
                rows.append(f"| {link} | {item['title'].replace('|', '/')} | {state.get('status', 'unknown')} | {current} |")
            table = "| ID | Title | Status | Continue |\n| --- | --- | --- | --- |\n" + "\n".join(rows) if rows else "No entries yet."
            self.write(rel, block(self.read(rel), "index", table))

    def apply(self, dry_run=False):
        changes = {p: d for p, d in self.changes.items() if self.before[p] != d}
        listing = [p.relative_to(self.project).as_posix() for p in changes]
        if dry_run or not changes:
            return {"dry_run": dry_run, "changed": listing}
        safe(self.project, "obsidian")
        self.root.mkdir(exist_ok=True)
        lock = self.path(".documentation.lock")
        written = []
        try:
            handle = lock.open("x", encoding="utf-8")
        except FileExistsError as exc:
            raise VaultError("Another writer holds the Vault lock; inspect it before retrying") from exc
        try:
            with handle:
                handle.write(js({"pid": os.getpid(), "started": now()}))
            for path in changes:
                safe(self.project, path.relative_to(self.project).as_posix())
                actual = path.read_bytes() if path.exists() else None
                if actual != self.before[path]:
                    raise VaultError(f"Concurrent change detected: {path}")
            for path, data in changes.items():
                safe(self.project, path.relative_to(self.project).as_posix())
                if (path.read_bytes() if path.exists() else None) != self.before[path]:
                    raise VaultError(f"Concurrent change detected: {path}")
                path.parent.mkdir(parents=True, exist_ok=True)
                temp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
                try:
                    with temp.open("xb") as stream:
                        stream.write(data)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.replace(temp, path)
                    written.append(path)
                finally:
                    temp.unlink(missing_ok=True)
        except Exception:
            for path in reversed(written):
                if path.read_bytes() == changes[path]:
                    previous = self.before[path]
                    if previous is None:
                        path.unlink()
                    else:
                        path.write_bytes(previous)
            raise
        finally:
            lock.unlink(missing_ok=True)
        return {"dry_run": False, "changed": listing}


def init(v, args):
    if not ID.fullmatch(args.key):
        raise VaultError("Use a stable uppercase project key, for example ACME-ERP")
    marker = v.path("vault.json")
    if marker.exists():
        config = v.config()
        if config["project_key"] != args.key:
            raise VaultError("The existing Vault belongs to a different project key")
    else:
        if v.root.exists() and any(v.root.iterdir()):
            raise VaultError("Existing unmanaged Vault: map and adopt its content before initialization")
        config = {"schema_version": 1, "project_key": args.key, "language": "en", "allowed_markdown": ["AGENTS.md", "AGENTS.override.md", "**/AGENTS.md", "**/AGENTS.override.md", "README.md", "**/README.md", "CHANGELOG.md", "**/CHANGELOG.md", "LICENSE.md", ".agents/skills/**", ".codex/skills/**"]}
        v.write("vault.json", js(config), create=True)
        for name in ("Home", "Development-Index", "Shared-Index", "Documentation-Policy"):
            body = Template((ASSETS / f"{name}.md").read_text(encoding="utf-8")).substitute(project_key=args.key)
            v.write(f"{name}.md", pack({"id": f"{args.key}.{name.lower()}", "kind": "guide", "updated": now()[:10]}, body), create=True)
        for template in (ASSETS / "templates").glob("*.md"):
            v.write("templates/" + template.name, template.read_bytes(), create=True)
        for kind, name in CORE.items():
            extra = {"title": "Shared Architecture", "dependencies": []} if kind == "overview" else {"status": "planned"} if kind == "current-state" else None
            rel, content = v.note("architecture", "ARCH", name, "Shared Architecture", "architecture" if kind == "overview" else kind, extra)
            v.write(rel, content, create=True)
    if args.install_guidance:
        rel = "AGENTS.override.md" if (v.project / "AGENTS.override.md").exists() else "AGENTS.md"
        path = safe(v.project, rel)
        previous = path.read_bytes() if path.exists() else b""
        text = previous.decode("utf-8-sig").replace("\r\n", "\n")
        instruction = (ASSETS / "AGENTS-snippet.md").read_text(encoding="utf-8").rstrip()
        if "<!-- sap-documentation:start -->" not in text:
            text = text.rstrip() + "\n\n<!-- sap-documentation:start -->\n<!-- sap-documentation:end -->\n"
        text = block(text, "sap-documentation", instruction)
        if previous and previous != text.encode("utf-8"):
            v.write(f"assets/guidance-backups/{rel}.{digest(previous)[:16]}.txt", previous, create=True)
        v.stage(path, text.encode("utf-8"))
    v.reindex()


def add(v, args):
    entities = v.entities()
    if not ID.fullmatch(args.id) or args.id == "ARCH" or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.slug):
        raise VaultError("Use a stable uppercase ID and lowercase hyphenated slug; ARCH is reserved")
    if not args.title.strip() or any(c in args.title for c in "\r\n[]|#"):
        raise VaultError("Use a single-line title without wikilink delimiters")
    folder = f"{'developments' if args.kind == 'development' else 'shared'}/{args.id}-{args.slug}"
    if args.id in entities:
        old = entities[args.id]
        if old["path"] != folder + "/Overview.md" or old["title"] != args.title or old["kind"] != args.kind:
            raise VaultError("ID already exists with different identity; inspect before renaming")
        return
    if v.path(folder).exists():
        raise VaultError("Target folder already exists; inspect before adoption")
    for kind, name in CORE.items():
        extra = {"title": args.title, "dependencies": []} if kind == "overview" else {"status": "planned"} if kind == "current-state" else None
        rel, content = v.note(folder, args.id, name, args.title, args.kind if kind == "overview" else kind, extra)
        v.write(rel, content, create=True)
    v.reindex()


def page(v, args):
    item = v.entity(args.id)
    folder = item["path"].rsplit("/", 1)[0]
    if args.template == "decision":
        if not args.record_id or not re.fullmatch(r"ADR-[0-9]{3,}", args.record_id):
            raise VaultError("A decision needs --record-id ADR-001 (or another unused number)")
        name = f"decisions/{args.record_id}"
        extra = {"status": "proposed"}
    else:
        name, extra = DETAIL[args.template], None
    rel, content = v.note(folder, args.id, name, args.title or item["title"], args.template, extra)
    if not v.path(rel).exists():
        v.write(rel, content, create=True)
    v.reindex()


def relate(v, args):
    source, target = v.entity(args.from_id), v.entity(args.to_id)
    if args.from_id == args.to_id:
        raise VaultError("Self-dependency is not meaningful")
    meta, body = unpack(v.read(source["path"]))
    refs = meta.setdefault("dependencies", [])
    if target["path"] not in [wiki_target(x) for x in refs]:
        refs.append(wikilink(target["path"]))
        meta["updated"] = now()[:10]
        v.write(source["path"], pack(meta, body))
    v.reindex()


def checkpoint(v, args):
    if not ID.fullmatch(args.event_id):
        raise VaultError("Use a stable event ID, for example EVT-20260908-001")
    item = v.entity(args.id)
    folder = item["path"].rsplit("/", 1)[0]
    if args.occurred_at:
        datetime.fromisoformat(args.occurred_at.replace("Z", "+00:00"))
    payload = {k: getattr(args, k) for k in ("event_id", "summary", "next", "status", "occurred_at", "evidence")}
    signature = digest(js(payload).encode("utf-8"))
    history_rel = f"{folder}/History.md"
    history = v.read(history_rel)
    marker = f"<!-- event:{args.event_id} sha256:{signature} -->"
    if f"<!-- event:{args.event_id} " in history:
        if marker not in history:
            raise VaultError("Event ID has a different payload; use a new correction event")
        return
    recorded = now()
    entry = f"{marker}\n## {args.event_id}\n\nRecorded at: {recorded}  \nOccurred at: {args.occurred_at or 'unknown'}  \nStatus: {args.status}\n\n{args.summary}\n\nNext action: {args.next}\n\nEvidence: {args.evidence or 'Not supplied; verification remains unproven.'}\n"
    v.write(history_rel, history.rstrip() + "\n\n" + entry)
    state_rel = f"{folder}/Current-State.md"
    meta, body = unpack(v.read(state_rel))
    meta.update(status=args.status, updated=recorded[:10])
    body = block(body, "checkpoint", f"{args.summary}\n\nStatus: **{args.status}**  \nNext action: {args.next}\n\n{wikilink(history_rel + '#' + args.event_id, 'Checkpoint record')}")
    v.write(state_rel, pack(meta, body))
    v.reindex()


def source(v, args):
    item = v.entity(args.id)
    rel = item["path"].rsplit("/", 1)[0] + "/source-snapshots.json"
    records = json.loads(v.read(rel)) if v.path(rel).exists() else {}
    for source_rel in args.source:
        if source_rel.startswith("obsidian/"):
            raise VaultError("Track original project evidence, not a self-referential Vault copy")
        path = safe(v.project, source_rel)
        value = digest(path.read_bytes())
        if records.get(source_rel, {}).get("sha256") != value:
            records[source_rel] = {"sha256": value, "observed_at": now()}
    v.write(rel, js(records))


def drift(v, item):
    rel = item["path"].rsplit("/", 1)[0] + "/source-snapshots.json"
    if not v.path(rel).exists():
        return []
    result = []
    for source_rel, old in json.loads(v.read(rel)).items():
        path = safe(v.project, source_rel)
        if not path.is_file() or digest(path.read_bytes()) != old["sha256"]:
            result.append(source_rel)
    return result


def context(v, args):
    entities = v.entities()
    item = v.entity(args.id)
    by_path = {x["path"]: key for key, x in entities.items()}
    deps = [by_path.get(wiki_target(d), "unresolved") for d in item.get("dependencies", [])]
    dependency_drift = {}
    for dep in deps:
        if dep in entities:
            changed = drift(v, entities[dep])
            if changed:
                dependency_drift[dep] = changed
    current = item["path"].rsplit("/", 1)[0] + "/Current-State.md"
    text = v.read(current)
    if args.max_chars < 1000:
        raise VaultError("--max-chars must be at least 1000")
    result = {"project": v.config()["project_key"], "entity": args.id, "overview": item["path"], "current_state_path": current,
              "dependencies": deps, "changed_sources": drift(v, item), "dependency_changed_sources": dependency_drift, "current_state": text[:args.max_chars],
              "truncated": len(text) > args.max_chars, "read_next": "Read the omitted state if truncated, then only sources and dependency pages needed for this task."}
    return result


def impact(v, args):
    entities = v.entities()
    v.entity(args.id)
    found, pending = {}, [(args.id, 0)]
    visited = {args.id}
    while pending:
        key, depth = pending.pop(0)
        for candidate, item in entities.items():
            if candidate not in visited and entities[key]["path"] in [wiki_target(d) for d in item.get("dependencies", [])]:
                visited.add(candidate)
                found[candidate] = {"depth": depth + 1, "overview": item["path"]}
                pending.append((candidate, depth + 1))
    return {"entity": args.id, "affected_consumers": found, "meaning": "Recorded dependency reachability; assess actual contract impact before changing consumers."}


def visible(text):
    text = re.sub(r"(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1\s*$", "", text)
    return re.sub(r"`[^`\n]+`", "", text)


def check(v, args):
    issues = []
    notes, ids = {}, {}
    def report(level, code, path, detail):
        issues.append({"level": level, "code": code, "path": path, "detail": detail})
    for rel in v.notes():
        try:
            text = v.read(rel)
            meta, body = unpack(text)
            for field in ("id", "kind", "updated"):
                if not meta.get(field):
                    report("error", "missing_property", rel, field)
            if meta.get("id") in ids:
                report("error", "duplicate_id", rel, str(meta.get("id")))
            ids[meta.get("id")] = rel
            if any(isinstance(val, dict) for val in meta.values()):
                report("error", "nested_property", rel, "Use flat properties")
            if meta.get("kind") == "current-state":
                if meta.get("status") not in STATES:
                    report("error", "invalid_status", rel, str(meta.get("status")))
                if len(body) > 6500:
                    report("warning", "large_resume", rel, "Shorten the active state; retain history in History.md")
            notes[rel] = (meta, text)
        except (ValueError, yaml.YAMLError) as exc:
            report("error", "invalid_note", rel, str(exc))
    for rel, (meta, text) in notes.items():
        links = list(WIKI.finditer(visible(text)))
        for match in links:
            target = match[2].replace("\\|", "|").split("|", 1)[0]
            name, _, anchor = target.partition("#")
            target_rel = name or rel
            if not Path(target_rel).suffix:
                target_rel += ".md"
            try:
                path = v.path(target_rel)
                exists = path.is_file() or target_rel in notes
                if not exists:
                    report("error", "broken_link", rel, target)
                elif anchor and target_rel in notes:
                    destination = notes[target_rel][1]
                    if anchor.startswith("^"):
                        exists = bool(re.search(r"\^" + re.escape(anchor[1:]) + r"\s*$", destination, re.M))
                    else:
                        exists = all(re.search(r"^#{1,6}\s+" + re.escape(a) + r"\s*#*\s*$", destination, re.M | re.I) for a in anchor.split("#"))
                    if not exists:
                        report("error", "broken_anchor", rel, target)
            except VaultError as exc:
                report("error", "unsafe_link", rel, str(exc))
        if meta.get("entity") and "[[Home|Home]]" not in text:
            report("error", "missing_navigation", rel, "Missing Home navigation")
    try:
        entities = v.entities()
        overview_paths = {item["path"] for item in entities.values()}
        root_notes = {"Home.md", "Development-Index.md", "Shared-Index.md", "Documentation-Policy.md"}
        for rel, (meta, _) in notes.items():
            if rel in root_notes:
                continue
            owner = entities.get(meta.get("entity"))
            if not owner or not rel.startswith(owner["path"].rsplit("/", 1)[0] + "/"):
                report("error", "misplaced_note", rel, "Use the owning entity folder or a registered root guide")
        for key, item in entities.items():
            folder = item["path"].rsplit("/", 1)[0]
            expected_prefix = "developments/" if item["kind"] == "development" else "shared/" if item["kind"] == "shared" else "architecture/"
            if not item["path"].startswith(expected_prefix):
                report("error", "wrong_location", item["path"], expected_prefix)
            for dep in item.get("dependencies", []):
                if wiki_target(dep) not in overview_paths:
                    report("error", "invalid_dependency", item["path"], "Dependency must reference a registered entity Overview")
            for name in CORE.values():
                if f"{folder}/{name}.md" not in notes:
                    report("error", "missing_core", folder, name)
            for changed in drift(v, item):
                report("warning", "source_changed", item["path"], changed)
        staged = Vault(v.project)
        staged.reindex()
        for path in staged.changes:
            report("error", "stale_index", path.relative_to(v.root).as_posix(), "Run reindex after reviewing relationships")
    except (VaultError, ValueError, yaml.YAMLError) as exc:
        report("error", "invalid_registry", "obsidian", str(exc))
    if args.audit_project:
        allowed = v.config()["allowed_markdown"]
        for path in walk(v.project):
            rel = path.relative_to(v.project).as_posix()
            if path.suffix.lower() == ".md" and not rel.startswith("obsidian/") and not any(fnmatch.fnmatchcase(rel, pattern) for pattern in allowed):
                report("error", "outside_vault", rel, "Classify this file; do not silently move or delete it")
    errors = sum(i["level"] == "error" for i in issues)
    return {"ok": errors == 0, "notes_checked": len(notes), "errors": errors, "warnings": len(issues) - errors, "issues": issues[:50], "omitted_issues": max(0, len(issues) - 50), "limits": "Structural checks only. English prose quality, semantic truth, Markdown links, Mermaid rendering, Obsidian UI, and SAP tenant behavior require separate review."}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", required=True, help="Explicit project root (not its obsidian subfolder)")
    p.add_argument("--dry-run", action="store_true", help="Preview writes without creating files")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("init")
    s.add_argument("--key", required=True)
    s.add_argument("--install-guidance", action="store_true")
    s = sub.add_parser("add")
    s.add_argument("--kind", choices=("development", "shared"), required=True)
    s.add_argument("--id", required=True)
    s.add_argument("--slug", required=True)
    s.add_argument("--title", required=True)
    s = sub.add_parser("page")
    s.add_argument("--id", required=True)
    s.add_argument("--template", choices=tuple(DETAIL) + ("decision",), required=True)
    s.add_argument("--record-id")
    s.add_argument("--title")
    s = sub.add_parser("relate")
    s.add_argument("--from-id", required=True, help="Consumer")
    s.add_argument("--to-id", required=True, help="Provider")
    s = sub.add_parser("checkpoint")
    s.add_argument("--id", required=True)
    s.add_argument("--event-id", required=True)
    s.add_argument("--summary", required=True)
    s.add_argument("--next", required=True)
    s.add_argument("--status", choices=STATES, required=True)
    s.add_argument("--occurred-at")
    s.add_argument("--evidence")
    s = sub.add_parser("source")
    s.add_argument("--id", required=True)
    s.add_argument("--source", action="append", required=True, help="Original project-relative source file")
    s = sub.add_parser("context")
    s.add_argument("--id", required=True)
    s.add_argument("--max-chars", type=int, default=5500)
    s = sub.add_parser("impact")
    s.add_argument("--id", required=True)
    sub.add_parser("reindex")
    s = sub.add_parser("check")
    s.add_argument("--audit-project", action="store_true")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        v = Vault(args.project)
        if args.command != "init":
            v.config()
        actions = {"init": init, "add": add, "page": page, "relate": relate, "checkpoint": checkpoint, "source": source}
        if args.command in actions:
            actions[args.command](v, args)
            result = v.apply(args.dry_run)
        elif args.command == "reindex":
            v.reindex()
            result = v.apply(args.dry_run)
        else:
            result = {"context": context, "impact": impact, "check": check}[args.command](v, args)
        print(js(result), end="")
        return 1 if result.get("ok") is False else 0
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        print(js({"error": str(exc)}), end="")
        return 2


if __name__ == "__main__":
    sys.exit(main())
