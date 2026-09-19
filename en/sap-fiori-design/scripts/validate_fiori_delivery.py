#!/usr/bin/env python3
"""Fail-closed static quality gate for SAP Fiori contracts and UI5 deliveries."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


SKIP_DIR_NAMES = {"node_modules", "dist", "coverage", ".git", ".ui5"}
TEXT_SUFFIXES = {".js", ".mjs", ".ts", ".xml", ".html", ".css", ".json", ".yaml", ".yml"}
OUTPUTS = {"png", "interactive", "code"}
FRAMEWORKS = {"freestyle-sapui5-prototype", "freestyle-sapui5", "fiori-elements-odata-v2", "fiori-elements-odata-v4"}
INTERACTIVE_XML_CONTROLS = {"Button", "CheckBox", "ComboBox", "DatePicker", "Dialog", "Input", "Link", "List", "MultiComboBox", "MultiInput", "SearchField", "Select", "Switch", "Table", "TextArea", "TreeTable"}
VISIBLE_XML_ATTRIBUTES = {"description", "label", "noDataText", "placeholder", "text", "title", "tooltip"}


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="backslashreplace")


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    path: str | None = None
    line: int | None = None


class Report:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.findings: list[Finding] = []
        self.checked_files: set[Path] = set()

    def add(self, severity: str, code: str, message: str, path: Path | None = None, line: int | None = None) -> None:
        relative = None
        if path is not None:
            resolved = path.resolve()
            try:
                relative = str(resolved.relative_to(self.root))
            except ValueError:
                relative = str(resolved)
        self.findings.append(Finding(severity, code, message, relative, line))

    def mark(self, path: Path) -> None:
        self.checked_files.add(path.resolve())

    # Severities: error and warning close the gate (warning unless --allow-warnings); info never does.
    def count(self, severity: str) -> int:
        return sum(item.severity == severity for item in self.findings)


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def is_skipped(root: Path, path: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    return any(part in SKIP_DIR_NAMES for part in relative.parts[:-1])


def iter_project_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and not is_skipped(root, path) and path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"Non-standard JSON number: {value}")


def load_json(path: Path, report: Report, code: str) -> dict | list | None:
    report.mark(path)
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_pairs, parse_constant=reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        line = error.lineno if isinstance(error, json.JSONDecodeError) else None
        report.add("error", code, f"Invalid strict JSON: {error}", path, line)
        return None


def schema_type_matches(value: object, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "boolean": isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "null": value is None,
    }.get(expected, True)


def validate_schema_value(value: object, schema: dict, pointer: str, report: Report, path: Path) -> None:
    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not schema_type_matches(value, expected_type):
        report.add("error", "SCHEMA_TYPE", f"{pointer} must be {expected_type}", path)
        return
    if "const" in schema and value != schema["const"]:
        report.add("error", "SCHEMA_CONST", f"{pointer} must equal {schema['const']!r}", path)
    if isinstance(schema.get("enum"), list) and value not in schema["enum"]:
        report.add("error", "SCHEMA_ENUM", f"{pointer} has unsupported value {value!r}", path)
    if isinstance(value, str):
        if isinstance(schema.get("minLength"), int) and len(value) < schema["minLength"]:
            report.add("error", "SCHEMA_MIN_LENGTH", f"{pointer} is too short", path)
        if isinstance(schema.get("pattern"), str) and not re.search(schema["pattern"], value):
            report.add("error", "SCHEMA_PATTERN", f"{pointer} does not match the required pattern", path)
    if isinstance(value, list):
        if isinstance(schema.get("minItems"), int) and len(value) < schema["minItems"]:
            report.add("error", "SCHEMA_MIN_ITEMS", f"{pointer} has too few items", path)
        if schema.get("uniqueItems") is True:
            encoded = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
            if len(encoded) != len(set(encoded)):
                report.add("error", "SCHEMA_UNIQUE", f"{pointer} contains duplicate items", path)
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                validate_schema_value(item, item_schema, f"{pointer}/{index}", report, path)
    if isinstance(value, dict):
        required = schema.get("required")
        if isinstance(required, list):
            for key in required:
                if key not in value:
                    report.add("error", "SCHEMA_REQUIRED", f"{pointer}/{key} is required", path)
        properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    report.add("error", "SCHEMA_ADDITIONAL", f"{pointer}/{key} is not allowed", path)
        for key, child_schema in properties.items():
            if key in value and isinstance(child_schema, dict):
                validate_schema_value(value[key], child_schema, f"{pointer}/{key}", report, path)


def validate_against_schema(data: object, schema_path: Path, data_path: Path, report: Report, code: str) -> None:
    schema = load_json(schema_path, report, code)
    if not isinstance(schema, dict):
        report.add("error", code, "Schema root must be an object", schema_path)
        return
    validate_schema_value(data, schema, "$", report, data_path)


PLACEHOLDER = re.compile(r"^(?:Replace\b|replace-with|ReplaceWith|pending-|verify-|YYYY-MM-DD$)")
REQUIRED_STATES = ("initial", "populated", "empty", "error", "no-auth")
RECOMMENDED_STATES = ("loading", "no-results")
PNG_NAME = r"^(?P<app>[a-z0-9]+(?:-[a-z0-9]+)*?)-(?P<state>{states})-(?P<breakpoint>S|M|L|XL)-(?P<theme>[a-z0-9_]+)-(?P<density>cozy|compact)\.png$"


def walk_strings(value: object, pointer: str = "$") -> Iterable[tuple[str, str, str]]:
    """Yield (pointer, key, string) for every string in a JSON document."""
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, str):
                yield f"{pointer}/{key}", key, child
            else:
                yield from walk_strings(child, f"{pointer}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            if isinstance(child, str):
                yield f"{pointer}/{index}", "", child
            else:
                yield from walk_strings(child, f"{pointer}/{index}")


def validate_completeness(data: dict, outputs: list, report: Report, path: Path) -> None:
    """A delivery gate is only as good as what it refuses: template text and empty evidence are not a design."""
    placeholders = [pointer for pointer, _, text in walk_strings(data) if PLACEHOLDER.match(text.strip())]
    for pointer in placeholders[:12]:
        report.add("warning", "CONTRACT_PLACEHOLDER", f"{pointer} still holds template or pending text", path)
    if len(placeholders) > 12:
        report.add("warning", "CONTRACT_PLACEHOLDER", f"{len(placeholders) - 12} more template or pending values remain", path)

    states = data.get("states") if isinstance(data.get("states"), list) else []
    state_ids = [item.get("id") for item in states if isinstance(item, dict)]
    for recommended in RECOMMENDED_STATES:
        if recommended not in state_ids:
            report.add("warning", "CONTRACT_STATE_RECOMMENDED", f"State is not designed: {recommended}", path)
    verification = data.get("verification") if isinstance(data.get("verification"), dict) else {}
    verified_states = verification.get("states") if isinstance(verification.get("states"), list) else []
    if sorted(map(str, verified_states)) != sorted(map(str, state_ids)):
        report.add("warning", "SEMANTIC_STATES", "verification.states differs from the designed states", path)
    evidence = verification.get("accessibilityEvidence")
    if not isinstance(evidence, list) or not evidence or any(
        not isinstance(row, dict) or not all(row.get(key) for key in ("check", "method", "result")) for row in evidence
    ):
        report.add("warning", "CONTRACT_A11Y_EVIDENCE", "verification.accessibilityEvidence needs check, method and result for what was really tested", path)

    if "code" in outputs:
        data_contract = data.get("dataContract") if isinstance(data.get("dataContract"), dict) else {}
        if not verification.get("commands"):
            report.add("warning", "CONTRACT_COMMANDS", "verification.commands is empty for a code delivery", path)
        if not data_contract.get("initialSelect"):
            report.add("warning", "CONTRACT_DATA_BUDGET", "dataContract.initialSelect is empty: name the fields of the first render", path)
        backend = data.get("backendEvidence") if isinstance(data.get("backendEvidence"), dict) else {}
        if backend.get("applicable") is True and data_contract.get("releasedApisVerified") not in (True, "not-applicable"):
            report.add("warning", "CONTRACT_RELEASED_UNVERIFIED", "dataContract.releasedApisVerified must be true or not-applicable once it was checked in the target system", path)


def i18n_keys(tree: Path) -> set[str] | None:
    bundles = [item for item in tree.rglob("i18n.properties") if not is_skipped(tree, item)]
    if not bundles:
        return None
    keys: set[str] = set()
    for line in bundles[0].read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            keys.add(line.split("=", 1)[0].strip())
    return keys


def validate_contract_against_tree(contract: dict, tree: Path, report: Report, metadata_driven: bool) -> None:
    """Every text key and action the contract names has to exist in the delivered UI."""
    if metadata_driven:
        return  # Fiori elements takes labels and actions from annotations, not from the app's bundle or views.
    keys = i18n_keys(tree)
    scope = {name: contract.get(name) for name in ("informationArchitecture", "fieldsAndActions")}
    wanted = unique_sorted(text for _, key, text in walk_strings(scope) if key.endswith("Key"))
    if keys is not None:
        for key in wanted:
            if key not in keys:
                report.add("warning", "SEMANTIC_I18N_KEY", f"Contract text key is missing from the i18n bundle: {key}", tree)
    xml_ids: set[str] = set()
    for view in tree.rglob("*.xml"):
        if not is_skipped(tree, view):
            xml_ids.update(re.findall(r"\bid\s*=\s*\"([^\"]+)\"", view.read_text(encoding="utf-8", errors="replace")))
    actions = contract.get("fieldsAndActions", {}).get("actions", [])
    for action in actions if isinstance(actions, list) else []:
        if isinstance(action, dict) and action.get("id") and action["id"] not in xml_ids:
            report.add("warning", "SEMANTIC_ACTION_ID", f"Contract action has no control with the same stable ID: {action['id']}", tree)


def unique_sorted(values: Iterable[str]) -> list[str]:
    return sorted({value for value in values if value})


def validate_launch_and_search(contract: dict, app_root: Path, report: Report) -> None:
    target = contract.get("context", {}).get("targetSystem", {})
    manifest_path = app_root / "webapp" / "manifest.json"
    if target.get("launchContext") == "flp" and manifest_path.is_file():
        try:
            inbounds = json.loads(manifest_path.read_text(encoding="utf-8")).get("sap.app", {}).get("crossNavigation", {}).get("inbounds", {})
        except json.JSONDecodeError:
            inbounds = {}
        intent = target.get("launchIntent") if isinstance(target.get("launchIntent"), dict) else {}
        matches = [
            row for row in inbounds.values()
            if isinstance(row, dict) and row.get("semanticObject") == intent.get("semanticObject") and row.get("action") == intent.get("action")
        ] if isinstance(inbounds, dict) else []
        if not intent or not matches:
            report.add("warning", "SEMANTIC_FLP_INBOUND", "launchContext is flp but the manifest has no inbound for context.targetSystem.launchIntent", manifest_path)
    capabilities = contract.get("dataContract", {}).get("serverCapabilities", {})
    if capabilities.get("search") is not True:
        for source in (app_root / "webapp").rglob("*"):
            if source.suffix.lower() in {".ts", ".js"} and not is_skipped(app_root, source) and "$search" in source.read_text(encoding="utf-8", errors="replace"):
                report.add("warning", "SEMANTIC_SEARCH_UNVERIFIED", "The app sends $search but dataContract.serverCapabilities.search is not true; verify @Search.searchable or filter instead", source)
                break


def require_object(data: dict, key: str, report: Report, path: Path) -> dict:
    value = data.get(key)
    if not isinstance(value, dict):
        report.add("error", "CONTRACT_REQUIRED", f"{key} must be an object", path)
        return {}
    return value


def require_nonempty_string(container: dict, key: str, report: Report, path: Path, prefix: str) -> None:
    if not isinstance(container.get(key), str) or not container[key].strip():
        report.add("error", "CONTRACT_TYPE", f"{prefix}.{key} must be a non-empty string", path)


def validate_contract(path: Path, schema_path: Path, report: Report) -> dict | None:
    data = load_json(path, report, "CONTRACT_JSON")
    if not isinstance(data, dict):
        if data is not None:
            report.add("error", "CONTRACT_ROOT", "Contract root must be an object", path)
        return None
    if schema_path.is_file():
        validate_against_schema(data, schema_path, path, report, "CONTRACT_SCHEMA_JSON")
    else:
        report.add("error", "CONTRACT_SCHEMA_MISSING", "design-contract.schema.json is missing", schema_path)
    if data.get("$schemaVersion") != "2.0":
        report.add("error", "CONTRACT_SCHEMA_VERSION", "$schemaVersion must be 2.0", path)
    if data.get("$schema") != "./design-contract.schema.json":
        report.add("error", "CONTRACT_SCHEMA_LINK", "$schema must reference the bundled local schema", path)

    required_objects = ["project", "context", "architecture", "informationArchitecture", "fieldsAndActions", "responsive", "visualSystem", "accessibility", "backendEvidence", "dataContract", "verification"]
    objects = {key: require_object(data, key, report, path) for key in required_objects}
    project, context, architecture = objects["project"], objects["context"], objects["architecture"]
    for key in ("id", "name", "language"):
        require_nonempty_string(project, key, report, path, "project")
    app_id = project.get("id")
    if isinstance(app_id, str) and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+", app_id):
        report.add("error", "CONTRACT_APP_ID", "project.id is not a valid dot-separated UI5 namespace", path)
    outputs = project.get("outputs")
    if not isinstance(outputs, list) or not outputs or any(item not in OUTPUTS for item in outputs) or len(outputs) != len(set(outputs)):
        report.add("error", "CONTRACT_OUTPUTS", "project.outputs must contain unique supported output values", path)

    framework = architecture.get("framework")
    if framework not in FRAMEWORKS:
        report.add("error", "CONTRACT_FRAMEWORK", f"Unsupported architecture.framework: {framework!r}", path)
    for key in ("floorplan", "layout", "frontendLanguage", "serviceProtocol", "decisionRationale"):
        require_nonempty_string(architecture, key, report, path, "architecture")
    expected_language = {"freestyle-sapui5-prototype": "javascript", "freestyle-sapui5": "typescript", "fiori-elements-odata-v2": "metadata", "fiori-elements-odata-v4": "metadata"}.get(framework)
    if expected_language and architecture.get("frontendLanguage") != expected_language:
        report.add("error", "CONTRACT_LANGUAGE_FRAMEWORK", f"{framework} requires frontendLanguage={expected_language}", path)
    protocol = architecture.get("serviceProtocol")
    if protocol not in {"odata-v2", "odata-v4"}:
        report.add("error", "CONTRACT_PROTOCOL", "serviceProtocol must be odata-v2 or odata-v4", path)
    if framework == "fiori-elements-odata-v4" and protocol != "odata-v4":
        report.add("error", "CONTRACT_PROTOCOL_FRAMEWORK", "Fiori elements OData V4 requires serviceProtocol=odata-v4", path)
    if framework == "fiori-elements-odata-v2" and protocol != "odata-v2":
        report.add("error", "CONTRACT_PROTOCOL_FRAMEWORK", "Fiori elements OData V2 requires serviceProtocol=odata-v2", path)

    target = context.get("targetSystem")
    if not isinstance(target, dict):
        report.add("error", "CONTRACT_TARGET", "context.targetSystem must be an object", path)
    else:
        # A prototype may honestly not know its target yet; production code may not.
        severity = "warning" if isinstance(outputs, list) and "code" in outputs else "info"
        for key in ("product", "edition", "release", "ui5Runtime", "fioriGuidelineVersion", "launchContext"):
            if str(target.get(key, "")).strip().lower() in {"", "unknown"}:
                report.add(severity, "CONTRACT_TARGET_UNKNOWN", f"context.targetSystem.{key} is not verified", path)
        if target.get("launchContext") == "flp" and not isinstance(target.get("launchIntent"), dict):
            report.add(severity, "CONTRACT_TARGET_UNKNOWN", "context.targetSystem.launchIntent is not verified", path)

    states = data.get("states")
    ids = {item.get("id") for item in states if isinstance(item, dict)} if isinstance(states, list) else set()
    for required in REQUIRED_STATES:
        if required not in ids:
            report.add("error", "CONTRACT_STATE", f"Required state is missing: {required}", path)
    breakpoints = objects["responsive"].get("breakpoints")
    names = {item.get("name") for item in breakpoints if isinstance(item, dict)} if isinstance(breakpoints, list) else set()
    for required in ("S", "M", "L", "XL"):
        if required not in names:
            report.add("error", "CONTRACT_BREAKPOINT", f"Required breakpoint is missing: {required}", path)
    for key in ("persistentLabels", "keyboardComplete", "visibleFocus", "highContrast"):
        if objects["accessibility"].get(key) is not True:
            report.add("error", "CONTRACT_ACCESSIBILITY", f"accessibility.{key} must be true", path)
    if objects["dataContract"].get("authorization") != "backend-enforced":
        report.add("error", "CONTRACT_AUTH", "dataContract.authorization must be backend-enforced", path)

    for key, required_fields in (("traceability", ("requirementId", "screenOrControl", "test")), ("sources", ("url", "checkedOn"))):
        rows = data.get(key)
        if not isinstance(rows, list) or not rows:
            report.add("error", f"CONTRACT_{key.upper()}", f"{key} must be a non-empty array", path)
            continue
        for index, row in enumerate(rows, 1):
            if not isinstance(row, dict) or any(not row.get(field) for field in required_fields):
                report.add("warning", f"CONTRACT_{key.upper()}", f"{key} row {index} is incomplete", path)
    validate_completeness(data, outputs if isinstance(outputs, list) else [], report, path)
    return data


def resolve_inside(root: Path, relative_value: object) -> Path | None:
    if not isinstance(relative_value, str) or not relative_value.strip() or relative_value == "unknown":
        return None
    candidate = (root / relative_value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def validate_backend_evidence(root: Path, contract: dict, report: Report) -> dict | None:
    evidence = contract.get("backendEvidence")
    if not isinstance(evidence, dict):
        report.add("error", "BACKEND_EVIDENCE", "backendEvidence must be an object")
        return None
    status = evidence.get("status")
    if status == "not-provided":
        if evidence.get("applicable") is True:
            report.add("warning", "BACKEND_NOT_PROVIDED", "ABAP package intake is applicable but no backend contract was provided")
        return None
    contract_path = resolve_inside(root, evidence.get("contractFile"))
    if contract_path is None:
        report.add("error", "BACKEND_PATH", "backendEvidence.contractFile must stay inside the delivery root")
        return None
    if not contract_path.is_file():
        report.add("error", "BACKEND_MISSING", "Referenced ABAP backend contract is missing", contract_path)
        return None
    expected_hash = evidence.get("sha256")
    observed_hash = hashlib.sha256(contract_path.read_bytes()).hexdigest()
    if expected_hash != observed_hash:
        report.add("error", "BACKEND_HASH", "ABAP backend contract SHA-256 differs from backendEvidence.sha256", contract_path)
    backend = load_json(contract_path, report, "BACKEND_JSON")
    if not isinstance(backend, dict):
        return None
    schema_path = root / "abap-backend-contract.schema.json"
    if schema_path.is_file():
        validate_against_schema(backend, schema_path, contract_path, report, "BACKEND_SCHEMA_JSON")
    else:
        report.add("error", "BACKEND_SCHEMA_MISSING", "abap-backend-contract.schema.json is missing", schema_path)

    source = backend.get("source") if isinstance(backend.get("source"), dict) else {}
    inventory = backend.get("inventory") if isinstance(backend.get("inventory"), dict) else {}
    objects = inventory.get("objects") if isinstance(inventory.get("objects"), list) else []
    if inventory.get("objectCount") != len(objects):
        report.add("error", "BACKEND_INVENTORY_COUNT", "inventory.objectCount differs from the objects array", contract_path)
    digest_rows: list[str] = []
    for item in objects:
        if isinstance(item, dict):
            digest_rows.append("|".join(str(item.get(key, "")) for key in ("type", "name", "path", "sha256")))
    snapshot_hash = hashlib.sha256("\n".join(digest_rows).encode("utf-8")).hexdigest()
    if source.get("snapshotSha256") != snapshot_hash:
        report.add("error", "BACKEND_SNAPSHOT_HASH", "source.snapshotSha256 does not match the object inventory", contract_path)
    for key in ("sourceMode", "packageName", "complete", "activeSourcesOnly"):
        source_key = {"sourceMode": "mode", "packageName": "packageName"}.get(key, key)
        if evidence.get(key) != source.get(source_key):
            report.add("error", "BACKEND_EVIDENCE_MISMATCH", f"backendEvidence.{key} differs from the backend contract", contract_path)

    gaps = backend.get("gaps") if isinstance(backend.get("gaps"), list) else []
    if evidence.get("gaps") != gaps:
        report.add("error", "BACKEND_GAPS_MISMATCH", "backendEvidence.gaps differs from the backend contract", contract_path)
    if status == "source-verified" and (gaps or source.get("complete") is not True or source.get("activeSourcesOnly") is not True):
        report.add("error", "BACKEND_FALSE_VERIFIED", "Source-verified backend evidence must be complete, active-only, and gap-free", contract_path)
    if status == "partial":
        report.add("warning", "BACKEND_PARTIAL", f"ABAP backend evidence remains partial with {len(gaps)} gap(s)", contract_path)
    if source.get("inventoryVerified") is not True:
        report.add("info", "BACKEND_INVENTORY_UNVERIFIED", "The package source declares no system inventory; completeness of the export is the provider's statement", contract_path)

    backend_service = backend.get("service") if isinstance(backend.get("service"), dict) else {}
    design_service = contract.get("dataContract", {}).get("mainService", {})
    architecture = contract.get("architecture", {})
    comparisons = (
        ("protocol", architecture.get("serviceProtocol"), backend_service.get("protocol")),
        ("uri", design_service.get("uri"), backend_service.get("uri")),
        ("entitySet", design_service.get("entitySet"), backend_service.get("entitySet")),
    )
    for label, design_value, backend_value in comparisons:
        if backend_value not in (None, "", "unknown") and design_value != backend_value:
            report.add("error", "BACKEND_DESIGN_DIVERGENCE", f"Design {label} differs from observed backend value", contract_path)
    mapped = {
        row.get("backendObject") for row in contract.get("traceability", [])
        if isinstance(row, dict) and row.get("backendObject")
    }
    expected = {
        row.get("backendObject") for row in backend.get("traceability", [])
        if isinstance(row, dict) and row.get("backendObject")
    }
    missing = sorted(expected - mapped)
    if missing:
        report.add("warning", "BACKEND_TRACEABILITY", f"Backend objects are not mapped in design traceability: {', '.join(missing[:10])}", contract_path)
    return backend


def version_tuple(value: object) -> tuple[int, ...]:
    if not isinstance(value, str):
        return ()
    try:
        return tuple(int(part) for part in value.split("."))
    except ValueError:
        return ()


def is_fiori_elements_manifest(sap_ui5: dict) -> bool:
    return "sap.fe.templates" in json.dumps(sap_ui5.get("routing", {}))


def validate_manifest(path: Path, report: Report, contract: dict | None, production: bool) -> dict | None:
    data = load_json(path, report, "MANIFEST_JSON")
    if not isinstance(data, dict):
        return None
    sap_app, sap_ui5 = data.get("sap.app"), data.get("sap.ui5")
    if not isinstance(sap_app, dict) or not isinstance(sap_ui5, dict):
        report.add("error", "MANIFEST_REQUIRED", "sap.app and sap.ui5 must be objects", path)
        return data
    if not isinstance(sap_app.get("i18n"), dict):
        report.add("error", "MANIFEST_I18N", "sap.app/i18n must define supportedLocales and fallbackLocale", path)
    else:
        for key in ("supportedLocales", "fallbackLocale"):
            if not sap_app["i18n"].get(key):
                report.add("error", "MANIFEST_I18N", f"sap.app/i18n/{key} is missing", path)
    dependencies = sap_ui5.get("dependencies")
    if not isinstance(dependencies, dict) or not dependencies.get("minUI5Version"):
        report.add("error", "MANIFEST_MIN_UI5", "sap.ui5/dependencies/minUI5Version is required", path)
    elif version_tuple(dependencies["minUI5Version"]) >= (1, 136) and version_tuple(data.get("_version")) < (2, 0):
        report.add("error", "MANIFEST_V2", "New projects targeting UI5 >=1.136 must use Manifest V2", path)
    if isinstance(dependencies, dict) and not isinstance(dependencies.get("libs"), dict):
        report.add("error", "MANIFEST_LIBS", "sap.ui5/dependencies/libs must be an object", path)
    if isinstance(sap_ui5.get("resources"), dict) and sap_ui5["resources"].get("js"):
        report.add("error", "MANIFEST_LEGACY_JS", "sap.ui5/resources/js is deprecated", path)
    if re.search(r'"async"\s*:\s*false', path.read_text(encoding="utf-8")):
        report.add("error", "MANIFEST_SYNC", "async:false is not allowed", path)
    manifest_v2 = version_tuple(data.get("_version")) >= (2, 0)
    if not is_fiori_elements_manifest(sap_ui5):
        root_view = sap_ui5.get("rootView")
        if not isinstance(root_view, dict):
            report.add("error", "MANIFEST_ROOT_VIEW", "Freestyle app requires rootView", path)
        elif not manifest_v2 and root_view.get("async") is not True:
            report.add("error", "MANIFEST_ASYNC_VIEW", "Manifest V1 freestyle rootView.async must be true", path)
    if not isinstance(sap_ui5.get("models"), dict) or "i18n" not in sap_ui5["models"]:
        report.add("error", "MANIFEST_I18N_MODEL", "Named i18n model is required", path)
    if not isinstance(sap_ui5.get("contentDensities"), dict):
        report.add("error", "MANIFEST_DENSITY", "contentDensities must be declared", path)

    if isinstance(contract, dict):
        project, architecture = contract.get("project", {}), contract.get("architecture", {})
        target = contract.get("context", {}).get("targetSystem", {})
        if sap_app.get("id") != project.get("id"):
            report.add("error", "SEMANTIC_APP_ID", "Manifest sap.app/id differs from contract project.id", path)
        if production and isinstance(dependencies, dict):
            minimum = dependencies.get("minUI5Version")
            declared = architecture.get("minUI5Version")
            if declared and minimum != declared:
                report.add("error", "SEMANTIC_MIN_UI5", "Manifest minUI5Version differs from contract architecture.minUI5Version", path)
            # minUI5Version is a lower bound, not the system runtime: it only has to be reachable by the target.
            runtime_version, minimum_version = version_tuple(target.get("ui5Runtime")), version_tuple(minimum)
            if runtime_version and minimum_version and runtime_version[:len(minimum_version)] < minimum_version[:len(runtime_version)]:
                report.add("error", "SEMANTIC_UI5_VERSION", "Manifest minUI5Version is newer than the contract target runtime", path)
        expected_fe = str(architecture.get("framework", "")).startswith("fiori-elements-")
        if production and is_fiori_elements_manifest(sap_ui5) != expected_fe and architecture.get("framework") != "freestyle-sapui5-prototype":
            report.add("error", "SEMANTIC_FRAMEWORK", "Manifest implementation does not match contract framework", path)
        if production:
            service = contract.get("dataContract", {}).get("mainService", {})
            serialized = json.dumps(data)
            if service.get("uri") and service["uri"] not in serialized:
                report.add("error", "SEMANTIC_SERVICE_URI", "Contract service URI is absent from manifest", path)
            if service.get("entitySet") and expected_fe and service["entitySet"] not in serialized:
                report.add("error", "SEMANTIC_ENTITY_SET", "Contract entity set is absent from Fiori elements routing", path)
            data_sources = sap_app.get("dataSources") if isinstance(sap_app.get("dataSources"), dict) else {}
            main_source = data_sources.get("mainService") if isinstance(data_sources.get("mainService"), dict) else {}
            settings = main_source.get("settings") if isinstance(main_source.get("settings"), dict) else {}
            observed_protocol = {"2.0": "odata-v2", "4.0": "odata-v4"}.get(settings.get("odataVersion"))
            if observed_protocol and observed_protocol != architecture.get("serviceProtocol"):
                report.add("error", "SEMANTIC_ODATA_VERSION", "Manifest OData version differs from the design contract", path)
    return data


def local_name(tag: str) -> str:
    return tag.split("}")[-1].split(":")[-1]


def validate_xml(path: Path, text: str, report: Report) -> None:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        report.add("error", "XML_PARSE", f"Invalid XML: {error}", path, error.position[0])
        return
    for element in root.iter():
        tag = local_name(element.tag)
        if tag in INTERACTIVE_XML_CONTROLS and not element.attrib.get("id"):
            report.add("warning", "XML_STABLE_ID", f"Interactive control has no stable ID: {tag}", path)
        for attribute, value in element.attrib.items():
            name, stripped = local_name(attribute), value.strip()
            if name == "style" and stripped:
                report.add("error", "XML_INLINE_STYLE", "Inline style is not allowed", path)
            literal = any(char.isalpha() for char in stripped) and not stripped.startswith(("{", "sap-icon://"))
            if name in VISIBLE_XML_ATTRIBUTES and literal:
                report.add("warning", "XML_HARDCODED_TEXT", f"Visible text should use i18n: {tag}.{name}", path)
            if name in {"press", "change", "search", "selectionChange"} and stripped and not stripped.startswith(".") and not stripped.startswith("{"):
                report.add("error", "XML_HANDLER_SCOPE", f"Event handler must use explicit controller-relative syntax: {name}=.{stripped}", path)


PATTERNS = [
    ("error", "LEGACY_CORE", re.compile(r"sap\.ui\.getCore\s*\("), "Use scoped public APIs instead of sap.ui.getCore()."),
    ("error", "LEGACY_JQUERY", re.compile(r"jQuery\.sap\."), "jQuery.sap.* is deprecated."),
    ("error", "LEGACY_CONTROLLER", re.compile(r"sap\.ui\.controller\s*\("), "Legacy global controller factory found."),
    ("error", "GLOBAL_UI5_CLASS", re.compile(r"(?:new\s+|instanceof\s+)sap\.[A-Za-z][A-Za-z0-9_.]*|\bsap\.(?:m|f|ui\.core)\.[A-Z][A-Za-z0-9_.]*\s*\("), "Import UI5 classes as modules; only documented loader APIs may be global."),
    ("error", "DANGEROUS_EVAL", re.compile(r"\beval\s*\(|new\s+Function\s*\("), "Dynamic code execution violates CSP guidance."),
    ("error", "DIRECT_DOM_QUERY", re.compile(r"document\.(?:getElementById|querySelector|querySelectorAll)\s*\("), "Use UI5 control APIs and bindings instead of direct DOM lookup."),
    ("error", "UNSAFE_INNERHTML", re.compile(r"\.innerHTML\s*="), "Direct innerHTML assignment violates CSP guidance."),
]
HEX_COLOR = r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![0-9A-Za-z_-])"
COLOR_FUNCTION = r"\b(?:rgb|rgba|hsl|hsla)\s*\("
# A CSS value or a quoted literal is a color; an ID selector, a URL fragment or a route hash is not.
COLOR_PATTERNS = {
    ".css": re.compile(rf":[^;{{}}]*?(?:{HEX_COLOR}|{COLOR_FUNCTION})"),
    "code": re.compile(rf"[\"'`]\s*(?:{HEX_COLOR}|{COLOR_FUNCTION})"),
}


def validate_text(path: Path, text: str, report: Report, production: bool) -> None:
    if path.suffix.lower() in {".js", ".mjs", ".ts", ".html", ".css"}:
        for severity, code, pattern, message in PATTERNS:
            for match in pattern.finditer(text):
                report.add(severity, code, message, path, line_number(text, match.start()))
        color_pattern = COLOR_PATTERNS.get(path.suffix.lower(), COLOR_PATTERNS["code"])
        for match in color_pattern.finditer(text):
            report.add("warning", "HARDCODED_COLOR", "Prefer UI5 theme parameters over hard-coded colors.", path, line_number(text, match.end()))
    if path.suffix.lower() == ".html" and "sap-ui-core.js" in text:
        if not re.search(r"data-sap-ui-async\s*=\s*[\"']true[\"']", text, re.I):
            report.add("error", "BOOTSTRAP_ASYNC", "UI5 bootstrap must be async", path)
        is_test_runner = "test" in path.parts and "qunit" in path.name.lower()
        if not is_test_runner and "module:sap/ui/core/ComponentSupport" not in text:
            report.add("error", "BOOTSTRAP_COMPONENT", "Standalone bootstrap must use ComponentSupport", path)
        if not re.search(r"data-height\s*=\s*[\"']100%[\"']", text, re.I):
            report.add("error", "BOOTSTRAP_HEIGHT", "Component host must declare data-height=100%", path)
        if re.search(r"<body[^>]+sapUiSize(?:Compact|Cozy)", text, re.I):
            report.add("error", "DENSITY_HARDCODED", "Do not hard-code content density on body", path)
        if not production and "ui5.sap.com/resources/" in text:
            report.add("error", "PROTOTYPE_UNPINNED_UI5", "Prototype CDN runtime must include an explicit UI5 version", path)


def validate_package(app_root: Path, report: Report, framework: str) -> None:
    package_path = app_root / "package.json"
    lock_path, ui5_path = app_root / "package-lock.json", app_root / "ui5.yaml"
    for path, code in ((package_path, "PROJECT_PACKAGE"), (lock_path, "PROJECT_LOCK"), (ui5_path, "PROJECT_UI5_YAML")):
        if not path.is_file():
            report.add("error", code, f"Production project is missing {path.name}", path)
    package = load_json(package_path, report, "PACKAGE_JSON") if package_path.is_file() else None
    if isinstance(package, dict):
        scripts = package.get("scripts") if isinstance(package.get("scripts"), dict) else {}
        required = {"build", "lint", "test:integration"}
        required.add("typecheck" if framework == "freestyle-sapui5" else "validate:manifest")
        if framework == "freestyle-sapui5":
            required.add("test:unit")
        for name in sorted(required):
            if not scripts.get(name):
                report.add("error", "PROJECT_SCRIPT", f"Required npm script is missing: {name}", package_path)
        for dependency in ("@ui5/cli", "@ui5/linter"):
            value = package.get("devDependencies", {}).get(dependency) if isinstance(package.get("devDependencies"), dict) else None
            if not isinstance(value, str) or value.startswith(("^", "~", ">", "*")):
                report.add("error", "PROJECT_PIN", f"{dependency} must be pinned exactly", package_path)
    if ui5_path.is_file():
        report.mark(ui5_path)
        text = ui5_path.read_text(encoding="utf-8")
        if "specVersion: \"4.0\"" not in text or "version: \"" not in text:
            report.add("error", "PROJECT_UI5_PROFILE", "ui5.yaml must pin specVersion 4.0 and framework version", ui5_path)

    integration = list((app_root / "tests" / "integration").glob("*.spec.ts"))
    if not integration:
        report.add("error", "PROJECT_INTEGRATION_TEST", "No executable integration *.spec.ts test was found", app_root / "tests")
    if framework == "freestyle-sapui5":
        if not (app_root / "tsconfig.json").is_file() or not list((app_root / "webapp").rglob("*.ts")):
            report.add("error", "PROJECT_TYPESCRIPT", "Freestyle production code requires tsconfig.json and TypeScript sources", app_root)
        if not list((app_root / "tests" / "unit").glob("*.spec.ts")):
            report.add("error", "PROJECT_UNIT_TEST", "No executable unit *.spec.ts test was found", app_root / "tests")


def validate_artifact(root: Path, report: Report, contract: dict | None, production: bool) -> None:
    manifests = [path for path in root.rglob("manifest.json") if path.is_file() and not is_skipped(root, path)]
    if not manifests:
        report.add("error", "PROJECT_MANIFEST", "No manifest.json was found", root)
    for manifest in manifests:
        validate_manifest(manifest, report, contract, production)
    for path in iter_project_files(root):
        if path.resolve() in report.checked_files:
            continue
        report.mark(path)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            report.add("error", "UTF8", f"File is not valid UTF-8: {error}", path)
            continue
        if path.suffix.lower() == ".xml":
            validate_xml(path, text, report)
        validate_text(path, text, report, production)


def validate_png_artifacts(root: Path, report: Report, contract: dict | None = None) -> None:
    visuals = root / "visuals"
    png_files = sorted(visuals.glob("*.png")) if visuals.is_dir() else []
    if not png_files:
        report.add("error", "PNG_MISSING", "Contract requests PNG output but visuals/ contains no PNG capture", visuals)
        return
    for path in png_files:
        report.mark(path)
        data = path.read_bytes()
        if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
            report.add("error", "PNG_INVALID", "File is not a valid PNG with an IHDR header", path)
            continue
        width, height = struct.unpack(">II", data[16:24])
        if width < 1 or height < 1:
            report.add("error", "PNG_DIMENSIONS", "PNG dimensions must be positive", path)
        # "list-populated" and "no-auth" are both two words: only the contract says which part is the state.
        states = sorted((str(item.get("id")) for item in (contract or {}).get("states", []) if isinstance(item, dict) and item.get("id")), key=len, reverse=True)
        designed = "|".join(re.escape(state) for state in states) or "[a-z]+(?:-[a-z]+)?"
        if not re.match(PNG_NAME.format(states=designed), path.name):
            generic = re.match(PNG_NAME.format(states="[a-z]+"), path.name)
            report.add("warning", "PNG_NAME", (
                f"Capture names a state the contract does not design: {generic.group('state')}" if generic
                else "Name captures <app>-<screen>-<state>-<S|M|L|XL>-<theme>-<cozy|compact>.png"
            ), path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate an SAP Fiori delivery; warnings fail by default")
    parser.add_argument("root", type=Path, help="Delivery root")
    parser.add_argument("--contract", type=Path, help="Path to design-contract.json")
    parser.add_argument("--allow-warnings", action="store_true", help="Development-only escape hatch; errors still fail")
    parser.add_argument("--review", action="store_true", help="Review an existing UI5 project that has no design contract; only errors fail")
    parser.add_argument("--json", action="store_true", help="Print JSON report")
    return parser


def main() -> int:
    configure_stdio()
    args = build_parser().parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"Delivery root does not exist or is not a directory: {root}", file=sys.stderr)
        return 2
    report = Report(root)
    contract_path = args.contract.resolve() if args.contract else root / "design-contract.json"
    schema_path = root / "design-contract.schema.json"
    contract = validate_contract(contract_path, schema_path, report) if contract_path.is_file() and not args.review else None
    if args.review:
        validate_artifact(root, report, None, production=True)
    elif contract is None and not contract_path.is_file():
        report.add("error", "CONTRACT_MISSING", f"Design contract not found: {contract_path}")
    if isinstance(contract, dict):
        validate_backend_evidence(root, contract, report)

    outputs = contract.get("project", {}).get("outputs", []) if isinstance(contract, dict) else []
    if "png" in outputs:
        validate_png_artifacts(root, report, contract)
    if "interactive" in outputs:
        prototype_root = root / "prototype"
        if prototype_root.is_dir():
            validate_artifact(prototype_root, report, contract, production=False)
            validate_contract_against_tree(contract, prototype_root, report, metadata_driven=False)
        else:
            report.add("error", "PROTOTYPE_MISSING", "Contract requests interactive output but prototype/ is missing", prototype_root)
    if "code" in outputs:
        app_root = root / "app"
        if app_root.is_dir():
            validate_artifact(app_root, report, contract, production=True)
            framework = contract.get("architecture", {}).get("framework", "") if isinstance(contract, dict) else ""
            validate_package(app_root, report, framework)
            validate_contract_against_tree(contract, app_root, report, metadata_driven=str(framework).startswith("fiori-elements-"))
            validate_launch_and_search(contract, app_root, report)
        else:
            report.add("error", "APP_MISSING", "Contract requests code output but app/ is missing", app_root)
    if not outputs and not args.review:
        validate_artifact(root, report, contract, production=False)

    errors, warnings = report.count("error"), report.count("warning")
    passed = errors == 0 and (args.allow_warnings or args.review or warnings == 0)
    result = {
        "root": str(root), "passed": passed,
        "policy": "review" if args.review else ("errors-only" if args.allow_warnings else "fail-on-warning"),
        "summary": {"errors": errors, "warnings": warnings, "info": report.count("info"), "filesChecked": len(report.checked_files)},
        "findings": [asdict(item) for item in report.findings],
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Policy: {result['policy']}")
        print(f"Files checked: {len(report.checked_files)}")
        print(f"Errors: {errors}; Warnings: {warnings}; Info: {report.count('info')}")
        for finding in report.findings:
            location = finding.path or "."
            if finding.line:
                location += f":{finding.line}"
            print(f"[{finding.severity.upper()}] {finding.code} {location} - {finding.message}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
