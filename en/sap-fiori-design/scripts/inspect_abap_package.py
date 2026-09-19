#!/usr/bin/env python3
"""Build an evidence-backed UI contract from an exported or snapshotted ABAP package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


MAX_FILE_BYTES = 2_000_000
MAX_FILES = 5_000

SUFFIX_TYPES = (
    (".ddls.asddls", "DDLS"),
    (".ddlx.asddlxs", "DDLX"),
    (".bdef.asbdef", "BDEF"),
    (".srvd.srvdsrv", "SRVD"),
    (".srvb.xml", "SRVB"),
    (".dcls.asdcls", "DCLS"),
    (".clas.abap", "CLAS"),
    (".intf.abap", "INTF"),
    (".devc.xml", "DEVC"),
    (".asddls", "DDLS"),
    (".asddlxs", "DDLX"),
    (".asbdef", "BDEF"),
    (".srvdsrv", "SRVD"),
    (".asdcls", "DCLS"),
)


@dataclass(frozen=True)
class SourceObject:
    name: str
    object_type: str
    path: str
    source: str
    version: str = "active"
    truncated: bool = False

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.source.encode("utf-8")).hexdigest()


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="backslashreplace")


def strict_json(text: str) -> object:
    def reject_pairs(pairs: list[tuple[str, object]]) -> dict:
        result: dict = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise ValueError(f"Non-standard JSON number: {value}")

    return json.loads(text, object_pairs_hook=reject_pairs, parse_constant=reject_constant)


def classify(path: str, declared_type: str | None = None) -> str | None:
    if declared_type:
        root = declared_type.upper().split("/", 1)[0]
        if root in {item[1] for item in SUFFIX_TYPES}:
            return root
    lower = path.lower()
    for suffix, object_type in SUFFIX_TYPES:
        if lower.endswith(suffix):
            return object_type
    return None


def inferred_name(path: str) -> str:
    name = PurePosixPath(path.replace("\\", "/")).name
    return name.split(".", 1)[0].upper()


def decode_source(data: bytes, label: str) -> str:
    if len(data) > MAX_FILE_BYTES:
        raise ValueError(f"Source exceeds {MAX_FILE_BYTES} bytes: {label}")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(f"Source is not UTF-8: {label}: {error}") from error


def read_directory(root: Path) -> list[SourceObject]:
    objects: list[SourceObject] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.is_symlink():
            raise ValueError(f"Symbolic links are not accepted in package input: {path}")
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError as error:
            raise ValueError(f"Package source escapes the input root: {path}") from error
        relative = path.relative_to(root).as_posix()
        object_type = classify(relative)
        if not object_type:
            continue
        objects.append(SourceObject(inferred_name(relative), object_type, relative, decode_source(path.read_bytes(), relative)))
        if len(objects) > MAX_FILES:
            raise ValueError(f"Package contains more than {MAX_FILES} supported source files")
    return objects


def read_zip(path: Path) -> list[SourceObject]:
    objects: list[SourceObject] = []
    with zipfile.ZipFile(path) as archive:
        for info in sorted(archive.infolist(), key=lambda item: item.filename):
            if info.is_dir():
                continue
            member = PurePosixPath(info.filename)
            if member.is_absolute() or ".." in member.parts:
                raise ValueError(f"Unsafe ZIP member path: {info.filename}")
            object_type = classify(info.filename)
            if not object_type:
                continue
            if info.file_size > MAX_FILE_BYTES:
                raise ValueError(f"Source exceeds {MAX_FILE_BYTES} bytes: {info.filename}")
            source = decode_source(archive.read(info), info.filename)
            objects.append(SourceObject(inferred_name(info.filename), object_type, member.as_posix(), source))
            if len(objects) > MAX_FILES:
                raise ValueError(f"Package contains more than {MAX_FILES} supported source files")
    return objects


def read_adt_snapshot(path: Path) -> tuple[list[SourceObject], str | None, list[str]]:
    payload = strict_json(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("objects"), list):
        raise ValueError("ADT snapshot must be an object containing an objects array")
    objects: list[SourceObject] = []
    gaps: list[str] = []
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(payload["objects"], 1):
        if not isinstance(item, dict):
            gaps.append(f"ADT snapshot object {index} is not an object")
            continue
        name = str(item.get("name") or item.get("objectName") or "").strip().upper()
        declared_type = str(item.get("type") or item.get("objectType") or "").strip()
        source = item.get("source")
        object_type = classify(name, declared_type)
        if not name or not object_type:
            gaps.append(f"ADT snapshot object {index} has no supported exact name/type")
            continue
        if not isinstance(source, str):
            gaps.append(f"{object_type} {name} has no readable source")
            continue
        if len(source.encode("utf-8")) > MAX_FILE_BYTES:
            gaps.append(f"{object_type} {name} exceeds the source size limit")
            continue
        identity = (object_type, name)
        if identity in seen:
            raise ValueError(f"ADT snapshot contains duplicate object {object_type} {name}")
        seen.add(identity)
        provided_hash = item.get("sha256")
        observed_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
        if provided_hash is not None and provided_hash != observed_hash:
            raise ValueError(f"ADT snapshot SHA-256 mismatch for {object_type} {name}")
        version = str(item.get("version") or "active").lower()
        truncated = bool(item.get("truncated"))
        if version != "active":
            gaps.append(f"{object_type} {name} is {version}, not active")
        if truncated:
            gaps.append(f"{object_type} {name} source is truncated")
        objects.append(SourceObject(name, object_type, str(item.get("uri") or name), source, version, truncated))
    declared_count = payload.get("objectCount")
    if isinstance(declared_count, int) and declared_count != len(payload["objects"]):
        gaps.append(f"ADT package inventory is incomplete: declared {declared_count}, snapshot has {len(payload['objects'])}")
    return objects, str(payload.get("packageName") or "").strip().upper() or None, gaps


def strip_comments(source: str, object_type: str) -> str:
    """Remove comments without touching quoted literals such as 'http://host'."""
    abap = object_type in {"CLAS", "INTF"}
    result: list[str] = []
    index, length = 0, len(source)
    line_start = True
    while index < length:
        char = source[index]
        pair = source[index:index + 2]
        if char == "'":
            closing = index + 1
            while closing < length and source[closing] not in "'\n":
                closing += 1
            result.append(source[index:closing + 1])
            index = closing + 1
            line_start = False
            continue
        if not abap and pair == "/*":
            closing = source.find("*/", index + 2)
            index = length if closing < 0 else closing + 2
            result.append(" ")
            continue
        if (not abap and pair in {"//", "--"}) or (abap and (char == '"' or (char == "*" and line_start))):
            closing = source.find("\n", index)
            index = length if closing < 0 else closing
            continue
        result.append(char)
        line_start = char == "\n"
        index += 1
    return "".join(result)


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def first_match(pattern: str, text: str, flags: int = re.I | re.S) -> str | None:
    match = re.search(pattern, text, flags)
    return match.group(1) if match else None


BRACKETS = {"(": ")", "[": "]", "{": "}"}


def skip_quoted(text: str, index: int) -> int:
    closing = text.find("'", index + 1)
    return len(text) if closing < 0 else closing + 1


def skip_balanced(text: str, index: int) -> int:
    """Return the index after the bracket group that opens at index; quoted literals are opaque."""
    stack = [BRACKETS[text[index]]]
    index += 1
    while index < len(text) and stack:
        char = text[index]
        if char == "'":
            index = skip_quoted(text, index)
            continue
        if char in BRACKETS:
            stack.append(BRACKETS[char])
        elif char == stack[-1]:
            stack.pop()
        index += 1
    return index


def strip_annotations(text: str) -> str:
    """Drop @Annotation and @Annotation: value, including nested and multi-line values."""
    result: list[str] = []
    index, length = 0, len(text)
    while index < length:
        char = text[index]
        if char == "'":
            closing = skip_quoted(text, index)
            result.append(text[index:closing])
            index = closing
            continue
        name = re.match(r"@<?[A-Za-z][A-Za-z0-9_.]*", text[index:]) if char == "@" else None
        if not name:
            result.append(char)
            index += 1
            continue
        index += name.end()
        result.append(" ")
        value = re.match(r"\s*:\s*", text[index:])
        if not value:
            continue
        index += value.end()
        if index < length and text[index] in BRACKETS:
            index = skip_balanced(text, index)
        elif index < length and text[index] == "'":
            index = skip_quoted(text, index)
        else:
            scalar = re.match(r"#?[A-Za-z0-9_.+-]+", text[index:])
            index += scalar.end() if scalar else 0
            if index < length and text[index] == "(":
                index = skip_balanced(text, index)
    return "".join(result)


def split_top_level(text: str, separator: str) -> list[str]:
    parts: list[str] = []
    start = index = 0
    while index < len(text):
        char = text[index]
        if char == "'":
            index = skip_quoted(text, index)
            continue
        if char in BRACKETS:
            index = skip_balanced(text, index)
            continue
        if char == separator:
            parts.append(text[start:index])
            start = index + 1
        index += 1
    parts.append(text[start:])
    return parts


def select_list(text: str) -> str | None:
    header = re.search(r"\bdefine\s+(?:root\s+)?(?:projection\s+)?view\s+entity\s+[A-Za-z_][A-Za-z0-9_]*", text, re.I)
    if not header:
        return None
    index = header.end()
    while index < len(text):
        char = text[index]
        if char == "'":
            index = skip_quoted(text, index)
        elif char == "{":
            return text[index + 1:skip_balanced(text, index) - 1]
        elif char in BRACKETS:
            index = skip_balanced(text, index)
        else:
            index += 1
    return None


ELEMENT_PATTERN = re.compile(
    r"[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*"
    r"(?:\s*:\s*[A-Za-z_][A-Za-z0-9_.]*(?:\([^)]*\))?)?"
)


def projection_elements(text: str) -> dict:
    """Read the element list; what the lexical reader cannot classify is reported, never dropped."""
    body = select_list(strip_annotations(text))
    fields: list[str] = []
    keys: list[str] = []
    exposed: list[str] = []
    unparsed: list[str] = []
    for segment in split_top_level(body or "", ","):
        candidate = " ".join(segment.split())
        if not candidate or re.match(r"^(?:association|composition)\b", candidate, re.I):
            continue
        is_key = bool(re.match(r"^key\s+", candidate, re.I))
        candidate = re.sub(r"^(?:key|virtual)\s+", "", candidate, flags=re.I)
        candidate = re.sub(r"\s*:\s*(?:redirected\s+to\b.*|localized)$", "", candidate, flags=re.I)
        alias = re.search(r"\bas\s+([A-Za-z_][A-Za-z0-9_]*)$", candidate, re.I)
        if alias:
            name = alias.group(1)
        elif ELEMENT_PATTERN.fullmatch(candidate):
            name = re.split(r"\s*:", candidate, maxsplit=1)[0].rsplit(".", 1)[-1]
        else:
            unparsed.append(candidate[:80])
            continue
        if name.startswith("_"):
            exposed.append(name)
            continue
        fields.append(name)
        if is_key:
            keys.append(name)
    return {"fields": unique(fields), "keys": unique(keys), "exposedAssociations": unique(exposed), "unparsed": unparsed}


SRVB_TYPE_PATTERN = re.compile(
    r"<(?:[\w.-]+:)?(?:BINDING_?)?TYPE\s*>\s*ODATA\s*<|(?<![\w])(?:[\w.-]+:)?(?:BINDING_?)?TYPE\s*=\s*[\"']ODATA[\"']"
)
SRVB_VERSION_PATTERN = re.compile(
    r"<(?:[\w.-]+:)?(?:BINDING_?)?VERSION\s*>\s*V?([24])(?:\.0)?\s*<"
    r"|(?<![\w])(?:[\w.-]+:)?(?:BINDING_?)?VERSION\s*=\s*[\"']V?([24])(?:\.0)?[\"']"
)


def detect_binding_protocol(text: str) -> str:
    """Return the OData protocol only when the service binding source states it unambiguously."""
    upper = text.upper()
    found = set()
    if re.search(r"ODATA[\s_-]?V4", upper):
        found.add("odata-v4")
    if re.search(r"ODATA[\s_-]?V2", upper):
        found.add("odata-v2")
    if not found and SRVB_TYPE_PATTERN.search(upper):
        # abapGit/ADT exports keep binding type and version in separate elements or attributes.
        for element_version, attribute_version in SRVB_VERSION_PATTERN.findall(upper):
            found.add(f"odata-v{element_version or attribute_version}")
    return found.pop() if len(found) == 1 else "unknown"


BDEF_MODIFIERS = r"(?:(?:use|internal|static|factory|repeatable|default|instance)\s+)*"
BDEF_OPTIONS = r"(?:\s*\([^)]*\))?"
NAME = r"([A-Za-z_][A-Za-z0-9_]*)"
DRAFT_ACTION_NAMES = {"edit", "activate", "discard", "resume", "prepare"}


def cut_blocks(body: str, opener: str) -> tuple[str, list[tuple[str, str]]]:
    """Cut `<opener> … { … }` groups so their inner semicolons do not end the outer statement."""
    found: list[tuple[str, str]] = []
    pattern = re.compile(opener + r"[^{};]*\{", re.I)
    while True:
        match = pattern.search(body)
        if not match:
            return body, found
        closing = skip_balanced(body, match.end() - 1)
        found.append((match.group(0), body[match.end():closing - 1]))
        body = body[:match.start()] + " ; " + body[closing:]


def parse_behavior_definitions(text: str, obj_name: str, path: str) -> list[dict]:
    """One record per `define behavior for`; operations are read statement by statement."""
    starts = [match.start() for match in re.finditer(r"\bdefine\s+behavior\s+for\b", text, re.I)]
    if not starts:
        return []
    prologue = text[:starts[0]]
    implementation = next(
        (word for word in ("unmanaged", "managed", "projection", "abstract") if re.search(rf"\b{word}\b", prologue, re.I)),
        "unknown",
    )
    file_draft = bool(re.search(r"\b(?:with|use)\s+draft\b", prologue, re.I))
    definitions: list[dict] = []
    for position, start in enumerate(starts):
        block = text[start:starts[position + 1] if position + 1 < len(starts) else len(text)]
        brace = block.find("{")
        header = block if brace < 0 else block[:brace]
        body = "" if brace < 0 else block[brace + 1:skip_balanced(block, brace) - 1]

        body, associations = cut_blocks(body, r"\b(?:use\s+)?association\s+_[A-Za-z0-9_]+")
        create_by_association = [
            re.search(r"_[A-Za-z0-9_]+", opener).group(0)
            for opener, inner in associations if re.search(r"\bcreate\b", inner, re.I)
        ]
        body, side_effects = cut_blocks(body, r"\bside\s+effects")
        body, _ = cut_blocks(body, r"\bmapping\s+for\b")
        body, _ = cut_blocks(body, r"\b(?:validation|determination)\s+[A-Za-z_][A-Za-z0-9_]*\s+on\b")

        operations = {"create": False, "update": False, "delete": False}
        dynamic: list[str] = []
        actions: list[str] = []
        draft_actions: list[str] = []
        functions: list[str] = []
        for statement in body.split(";"):
            statement = " ".join(statement.split())
            standard = re.match(rf"^{BDEF_MODIFIERS}(create|update|delete)\b({BDEF_OPTIONS})$", statement, re.I)
            draft_action = re.match(rf"^{BDEF_MODIFIERS}draft\s+(?:determine\s+)?action{BDEF_OPTIONS}\s+{NAME}", statement, re.I)
            action = re.match(rf"^{BDEF_MODIFIERS}(?:determine\s+)?action{BDEF_OPTIONS}\s+{NAME}", statement, re.I)
            function = re.match(rf"^{BDEF_MODIFIERS}function{BDEF_OPTIONS}\s+{NAME}", statement, re.I)
            if standard:
                operations[standard.group(1).lower()] = True
                if re.search(r"\bfeatures\s*:", standard.group(2), re.I):
                    dynamic.append(standard.group(1).lower())
            elif draft_action:
                draft_actions.append(draft_action.group(1))
            elif action and statement.lower().startswith("use ") and action.group(1).lower() in DRAFT_ACTION_NAMES:
                # A projection reuses the draft actions of its base with a plain `use action Edit;`.
                draft_actions.append(action.group(1))
            elif action:
                actions.append(action.group(1))
                if re.search(r"\bfeatures\s*:", statement, re.I):
                    dynamic.append(action.group(1))
            elif function:
                functions.append(function.group(1))

        definitions.append({
            "entity": first_match(rf"\bdefine\s+behavior\s+for\s+{NAME}", header) or "unknown",
            "implementation": implementation,
            "draftEnabled": file_draft or bool(re.search(r"\bdraft\s+table\b|\buse\s+draft\b", block, re.I)),
            "create": operations["create"],
            "update": operations["update"],
            "delete": operations["delete"],
            "createByAssociation": unique(create_by_association),
            "actions": unique(actions),
            "draftActions": unique(draft_actions),
            "functions": unique(functions),
            "dynamicFeatureControl": unique(dynamic),
            "validations": unique(re.findall(rf"\bvalidation\s+{NAME}", block, re.I)),
            "determinations": unique(re.findall(rf"\bdetermination\s+{NAME}", block, re.I)),
            "sideEffectsDeclared": bool(side_effects),
            "etag": first_match(rf"(?<!\btotal\s)\betag\s+(?:master\s+|dependent\s+by\s+)?{NAME}", header),
            "totalEtag": first_match(rf"\btotal\s+etag\s+{NAME}", header),
            "authorization": "declared" if re.search(r"\bauthorization\s+(?:master|dependent)\b", header, re.I) else "not-observed",
            "sourceObject": obj_name,
            "path": path,
        })
    return definitions


def package_from_devc(objects: list[SourceObject]) -> str | None:
    for obj in objects:
        if obj.object_type != "DEVC":
            continue
        match = re.search(r'(?:adtcore:)?name\s*=\s*["\']([^"\']+)', obj.source, re.I)
        if match:
            return match.group(1).upper()
    return None


def analyze(objects: list[SourceObject], package_name: str | None, source_mode: str, source_label: str,
            service_uri: str | None, protocol_override: str | None, initial_gaps: list[str],
            service_definition: str | None = None, entity_set: str | None = None) -> dict:
    inventory: list[dict] = []
    entities: list[dict] = []
    annotations: list[dict] = []
    associations: list[dict] = []
    services: list[dict] = []
    behaviors: list[dict] = []
    access_controls: list[dict] = []
    traceability: list[dict] = []
    bindings: list[dict] = []
    parse_gaps: list[str] = []

    for obj in objects:
        inventory.append({
            "name": obj.name, "type": obj.object_type, "path": obj.path,
            "version": obj.version, "sha256": obj.sha256, "truncated": obj.truncated,
        })
        # XML sources carry namespace URLs; a lexical // comment rule would cut them.
        text = obj.source if obj.object_type in {"SRVB", "DEVC"} else strip_comments(obj.source, obj.object_type)
        annotation_names = unique(re.findall(r"@([A-Za-z][A-Za-z0-9_.]+)", text))
        for name in annotation_names:
            annotations.append({"name": name, "object": obj.name, "path": obj.path})

        if obj.object_type == "DDLS":
            entity_match = re.search(
                r"\bdefine\s+(root\s+)?(?:(projection)\s+)?view\s+entity\s+([A-Za-z_][A-Za-z0-9_]*)",
                text, re.I,
            )
            if entity_match:
                entity = entity_match.group(3)
                elements = projection_elements(text)
                if elements["unparsed"]:
                    parse_gaps.append(
                        f"{len(elements['unparsed'])} element(s) of {entity} could not be read lexically; "
                        f"verify them in $metadata: {'; '.join(elements['unparsed'][:3])}"
                    )
                entities.append({
                    "name": entity,
                    "root": bool(entity_match.group(1)),
                    "projection": bool(entity_match.group(2)) or bool(re.search(r"\bas\s+projection\s+on\b", text, re.I)),
                    "fields": elements["fields"],
                    "keys": elements["keys"],
                    "exposedAssociations": elements["exposedAssociations"],
                    "unparsedElements": elements["unparsed"],
                    "sourceObject": obj.name,
                    "path": obj.path,
                })
                traceability.append({"backendObject": entity, "sourcePath": obj.path, "uiImpact": "entity-and-fields"})
            for target, alias in re.findall(
                r"\bassociation(?:\s+\[[^\]]+\])?\s+to(?:\s+parent)?\s+([A-Za-z_][A-Za-z0-9_]*)\s+as\s+(_[A-Za-z_][A-Za-z0-9_]*)",
                text, re.I,
            ):
                associations.append({"sourceObject": obj.name, "target": target, "alias": alias, "path": obj.path})

        elif obj.object_type == "DDLX":
            target = first_match(r"\bannotate\s+(?:view\s+)?([A-Za-z_][A-Za-z0-9_]*)\s+with\b", text)
            if target:
                traceability.append({"backendObject": target, "sourcePath": obj.path, "uiImpact": "ui-annotations"})

        elif obj.object_type == "BDEF":
            definitions = parse_behavior_definitions(text, obj.name, obj.path)
            if not definitions:
                parse_gaps.append(f"No behavior definition could be read from {obj.name}")
            behaviors.extend(definitions)
            for definition in definitions:
                traceability.append({"backendObject": definition["entity"], "sourcePath": obj.path, "uiImpact": "edit-actions-messages"})

        elif obj.object_type == "SRVD":
            definition = first_match(r"\bdefine\s+service\s+([A-Za-z_][A-Za-z0-9_]*)", text) or obj.name
            exposed = [
                {"sourceEntity": source, "entitySet": alias or source}
                for source, alias in re.findall(
                    r"\bexpose\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s+as\s+([A-Za-z_][A-Za-z0-9_]*))?\s*;",
                    text, re.I,
                )
            ]
            services.append({"name": definition, "exposedEntities": exposed, "sourceObject": obj.name, "path": obj.path})
            traceability.append({"backendObject": definition, "sourcePath": obj.path, "uiImpact": "service-boundary"})

        elif obj.object_type == "SRVB":
            bindings.append({"name": obj.name, "protocol": detect_binding_protocol(text), "path": obj.path})

        elif obj.object_type == "DCLS":
            role = first_match(r"\bdefine\s+role\s+([A-Za-z_][A-Za-z0-9_]*)", text) or obj.name
            targets = unique(re.findall(r"\bgrant\s+select\s+on\s+([A-Za-z_][A-Za-z0-9_]*)", text, re.I))
            access_controls.append({"role": role, "targets": targets, "path": obj.path})

    detected_protocols = unique([item["protocol"] for item in bindings if item["protocol"] != "unknown"])
    protocol = protocol_override or (detected_protocols[0] if len(detected_protocols) == 1 else "unknown")
    gaps = list(initial_gaps) + parse_gaps
    main_service = None
    if service_definition:
        main_service = next((item for item in services if item["name"].upper() == service_definition.upper()), None)
        if main_service is None:
            gaps.append(f"Explicit service definition {service_definition} was not observed in the package")
    elif len(services) == 1:
        main_service = services[0]
    elif services:
        gaps.append(
            "Multiple service definitions were observed; name the UI service with --service-definition: "
            + ", ".join(item["name"] for item in services)
        )
    exposed = main_service["exposedEntities"] if main_service else []
    root_names = {item["name"].upper() for item in entities if item["root"]}
    root_sets = [item["entitySet"] for item in exposed if item["sourceEntity"].upper() in root_names]
    main_entity_set = "unknown"
    if entity_set:
        main_entity_set = next((item["entitySet"] for item in exposed if item["entitySet"] == entity_set), "unknown")
        if main_entity_set == "unknown":
            gaps.append(f"Explicit entity set {entity_set} is not exposed by the selected service definition")
    elif len(exposed) == 1:
        main_entity_set = exposed[0]["entitySet"]
    elif len(root_sets) == 1:
        main_entity_set = root_sets[0]
    elif exposed:
        gaps.append("The leading entity set is ambiguous; name it with --entity-set: " + ", ".join(item["entitySet"] for item in exposed))
    ui_annotations = [item for item in annotations if item["name"].lower().startswith(("ui.", "consumption.valuehelp", "semantics."))]
    if protocol_override and detected_protocols and protocol_override not in detected_protocols:
        gaps.append(f"Explicit protocol {protocol_override} conflicts with observed service binding protocol(s): {', '.join(detected_protocols)}")
    if len(detected_protocols) > 1:
        gaps.append(f"Multiple service binding protocols were observed: {', '.join(detected_protocols)}")
    if not entities:
        gaps.append("No CDS view entity was observed")
    if not services:
        gaps.append("No service definition was observed")
    if protocol == "unknown":
        gaps.append("OData protocol was not proven from a service binding or explicit input")
    if not service_uri:
        gaps.append("Published service URI cannot be derived from package source")
    if not ui_annotations:
        gaps.append("No UI/value-help annotation was observed")
    transactional = any(
        item["create"] or item["update"] or item["delete"] or item["actions"]
        for item in behaviors
    )
    if transactional and not any(item["draftEnabled"] for item in behaviors) and protocol == "odata-v4":
        gaps.append("Transactional Fiori elements OData V4 readiness needs draft or target-version feature verification")
    if any(obj.truncated for obj in objects):
        gaps.append("At least one source object is truncated")
    gaps = unique(gaps)

    framework = "fiori-elements-odata-v4" if protocol == "odata-v4" and main_service else "undecided"
    readiness = "ready" if framework != "undecided" and service_uri and ui_annotations and not gaps else (
        "partial" if entities or services else "blocked"
    )
    digest_input = "\n".join(f"{item['type']}|{item['name']}|{item['path']}|{item['sha256']}" for item in inventory)
    snapshot_sha = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()
    all_actions = unique([action for behavior in behaviors for action in behavior["actions"]])
    draft_values = {behavior["draftEnabled"] for behavior in behaviors}
    draft_enabled: bool | str = next(iter(draft_values)) if len(draft_values) == 1 else "mixed-or-unknown"

    return {
        "$schema": "./abap-backend-contract.schema.json",
        "$schemaVersion": "1.0",
        "source": {
            "mode": source_mode,
            "label": source_label,
            "packageName": package_name or "unknown",
            "snapshotSha256": snapshot_sha,
            "activeSourcesOnly": all(obj.version == "active" for obj in objects),
            "complete": not any(obj.truncated for obj in objects) and not initial_gaps,
        },
        "inventory": {"objectCount": len(inventory), "objects": inventory},
        "model": {"entities": entities, "associations": associations},
        "behavior": {
            "definitions": behaviors, "draftEnabled": draft_enabled, "actions": all_actions,
            "draftActions": unique([action for behavior in behaviors for action in behavior["draftActions"]]),
        },
        "service": {
            "definition": main_service["name"] if main_service else "unknown",
            "uri": service_uri or "unknown",
            "protocol": protocol,
            "entitySet": main_entity_set,
            "exposedEntities": exposed,
            "bindings": bindings,
        },
        "uiSemantics": {
            "annotations": ui_annotations,
            "annotationCount": len(ui_annotations),
            "valueHelpObserved": any("valuehelp" in item["name"].lower() for item in ui_annotations),
        },
        "security": {
            "accessControls": access_controls,
            "authorizationAnnotationObserved": any(item["name"].lower() == "accesscontrol.authorizationcheck" for item in annotations),
            "backendAuthorizationObserved": bool(access_controls) or any(item["authorization"] == "declared" for item in behaviors),
        },
        "recommendation": {
            "framework": framework,
            "readiness": readiness,
            "reason": "RAP service and OData V4 metadata favor Fiori elements" if framework != "undecided" else "Protocol or service evidence is insufficient for a framework decision",
        },
        "traceability": traceability,
        "gaps": gaps,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect an ABAP package directory, ZIP, or read-only ADT snapshot for UI-relevant contracts"
    )
    parser.add_argument("source", type=Path, help="ADT/abapGit directory, ZIP, or normalized ADT snapshot JSON")
    parser.add_argument("--output", type=Path, required=True, help="Output abap-backend-contract.json")
    parser.add_argument("--package-name", help="Exact package name when it cannot be inferred")
    parser.add_argument("--service-uri", help="Published service URI observed in the target system")
    parser.add_argument("--protocol", choices=["odata-v2", "odata-v4"], help="Observed service binding protocol")
    parser.add_argument("--service-definition", help="UI service definition when the package contains several")
    parser.add_argument("--entity-set", help="Leading entity set when the service exposes several candidates")
    parser.add_argument("--json", action="store_true", help="Print the completed contract to stdout")
    return parser


def main() -> int:
    configure_stdio()
    args = build_parser().parse_args()
    source = args.source.resolve()
    try:
        if args.service_uri and not args.service_uri.startswith("/"):
            raise ValueError("--service-uri must begin with /")
        gaps: list[str] = []
        if source.is_dir():
            objects = read_directory(source)
            package_name = None
            source_mode = "local-export"
        elif source.is_file() and zipfile.is_zipfile(source):
            objects = read_zip(source)
            package_name = None
            source_mode = "local-export"
        elif source.is_file() and source.suffix.lower() == ".json":
            objects, package_name, gaps = read_adt_snapshot(source)
            source_mode = "live-adt-snapshot"
        else:
            raise ValueError("Source must be an existing directory, ZIP, or ADT snapshot JSON")
        if not objects:
            raise ValueError("No supported ABAP package sources were found")
        package_name = (args.package_name or package_name or package_from_devc(objects) or "unknown").upper()
        contract = analyze(
            objects, package_name, source_mode, source.name,
            args.service_uri, args.protocol, gaps,
            args.service_definition, args.entity_set,
        )
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        if args.json:
            print(json.dumps(contract, ensure_ascii=False, indent=2))
        else:
            print(f"ABAP backend contract written: {output}")
            print(f"Objects: {len(objects)}; readiness: {contract['recommendation']['readiness']}; gaps: {len(contract['gaps'])}")
        return 0
    except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
