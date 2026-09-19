#!/usr/bin/env python3
"""Create or extend a non-destructive, contract-led SAP Fiori delivery workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS = SKILL_ROOT / "assets"
PROFILE_PATH = ASSETS / "version-profiles.json"
APP_ID_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+$")
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
TEMPLATES = {"freestyle-sapui5": "ui5-production-freestyle", "fiori-elements-odata-v4": "ui5-production-fiori-elements"}


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="backslashreplace")


def reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_backend_contract(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_pairs)
    if not isinstance(data, dict) or data.get("$schemaVersion") != "1.0":
        raise ValueError("--backend-contract must be an ABAP backend contract with $schemaVersion 1.0")
    for key in ("source", "service", "recommendation", "gaps", "traceability"):
        if key not in data:
            raise ValueError(f"--backend-contract is missing {key}")
    return data


def load_profiles() -> tuple[dict, str, str]:
    data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    profiles, default = data["profiles"], data.get("defaultProfile")
    if default not in profiles:
        raise ValueError("version-profiles.json: defaultProfile must name one of the profiles")
    return profiles, default, data.get("templateLockfileProfile", default)


def version_tuple(value: str | None) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in (value or "").split("."))
    except ValueError:
        return ()


def parse_outputs(value: str) -> list[str]:
    aliases = {
        "png": ["png", "interactive"],
        "png+interactive": ["png", "interactive"],
        "all": ["png", "interactive", "code"],
    }
    return aliases.get(value, [value])


def plan_tree(source: Path, destination: Path) -> list[tuple[Path, Path]]:
    return [(item, destination / item.relative_to(source)) for item in sorted(source.rglob("*")) if item.is_file()]


def ensure_no_conflicts(planned: list[tuple[Path, Path]], force: bool) -> None:
    if force:
        return
    conflicts = [destination for _, destination in planned if destination.exists()]
    if conflicts:
        preview = "\n".join(f"- {path}" for path in conflicts[:10])
        extra = len(conflicts) - 10
        suffix = f"\n- ... and {extra} more" if extra > 0 else ""
        raise FileExistsError(
            "Refusing to create a partial workspace because target files already exist:\n"
            f"{preview}{suffix}\nUse --force only when you intend to overwrite every planned scaffold target path."
        )


def render_file(source: Path, destination: Path, tokens: dict[str, str]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        content = source.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        shutil.copy2(source, destination)
        return
    for token, value in tokens.items():
        content = content.replace(f"__{token}__", value)
    destination.write_text(content, encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a design contract plus separate prototype and production artifacts. "
        "An existing design-contract.json is kept: a later run only adds the requested outputs to it."
    )
    parser.add_argument("target", type=Path, help="Output directory")
    parser.add_argument("--app-id", required=True, help="Dot-separated UI5 application namespace")
    parser.add_argument("--name", required=True, help="Human-readable application name")
    parser.add_argument("--language", default="tr", choices=["tr", "en"], help="Language of the generated app and its mock data")
    parser.add_argument("--output", choices=["png", "interactive", "png+interactive", "code", "all"], default="png+interactive")
    parser.add_argument("--framework", choices=sorted(TEMPLATES), help="Required when code is requested")
    parser.add_argument("--ui5-version", help="Reviewed scaffold profile (tooling and minUI5Version); required for code. Not target-system evidence")
    parser.add_argument("--target-ui5-runtime", help="SAPUI5 runtime version observed in the target system, for example 1.136.7; omit while unknown")
    parser.add_argument("--backend-contract", type=Path, help="Evidence-backed abap-backend-contract.json")
    parser.add_argument("--service-protocol", choices=["odata-v2", "odata-v4"], help="Observed service protocol; new code scaffold supports OData V4")
    parser.add_argument("--service-uri", help="OData V4 service URI; required for code")
    parser.add_argument("--entity-set", help="OData V4 entity set; required for code")
    parser.add_argument("--semantic-object", help="SAP Fiori launchpad semantic object of the app tile; omit while unknown")
    parser.add_argument("--action", default="display", help="SAP Fiori launchpad action of the inbound (default: display)")
    parser.add_argument("--force", action="store_true", help="Overwrite the planned prototype/ and app/ files; the design contract is still kept")
    parser.add_argument("--reset-contract", action="store_true", help="Start design-contract.json again from the template; the old file is saved as .bak")
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary")
    return parser


def validate_args(args: argparse.Namespace, outputs: list[str], profiles: dict, lockfile_profile: str, backend: dict | None) -> list[str]:
    errors: list[str] = []
    if not APP_ID_PATTERN.fullmatch(args.app_id):
        errors.append("--app-id must be a dot-separated UI5 namespace, for example com.acme.orders")
    if args.target_ui5_runtime and not re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", args.target_ui5_runtime):
        errors.append("--target-ui5-runtime must look like 1.136 or 1.136.7")
    for name in ("semantic_object", "action"):
        value = getattr(args, name)
        if value and not IDENTIFIER.fullmatch(value):
            errors.append(f"--{name.replace('_', '-')} must be an identifier such as SalesOrder or display")
    if "code" in outputs:
        for name in ("framework", "ui5_version", "service_protocol", "service_uri", "entity_set"):
            if not getattr(args, name):
                errors.append(f"--{name.replace('_', '-')} is required when --output includes code")
        if args.service_protocol and args.service_protocol != "odata-v4":
            errors.append("New production scaffold supports OData V4 only; preserve an existing OData V2 project instead of generating it from the V4 template")
        if args.ui5_version and args.ui5_version not in profiles:
            supported = ", ".join(sorted(profiles))
            errors.append(f"Unsupported UI5 profile {args.ui5_version!r}; reviewed profiles: {supported}")
        elif args.ui5_version and args.framework and lockfile_for(args.ui5_version, profiles, lockfile_profile, TEMPLATES[args.framework]) is None:
            errors.append(
                f"Profile {args.ui5_version} has no reviewed lockfile for {TEMPLATES[args.framework]}; "
                "add assets/<lockfileDir>/<template>/package-lock.json and name lockfileDir in version-profiles.json"
            )
        if args.service_uri and not args.service_uri.startswith("/"):
            errors.append("--service-uri must begin with /")
        if args.entity_set and not IDENTIFIER.fullmatch(args.entity_set):
            errors.append("--entity-set must be a valid OData identifier")
        runtime, minimum = version_tuple(args.target_ui5_runtime), version_tuple(args.ui5_version)
        if runtime and minimum and args.ui5_version in profiles and runtime[:len(minimum)] < minimum[:len(runtime)]:
            errors.append(
                f"Scaffold profile {args.ui5_version} would set minUI5Version above the observed target runtime "
                f"{args.target_ui5_runtime}; add a reviewed profile for that runtime instead"
            )
    if backend:
        service = backend.get("service", {})
        # The inspector's framework is a recommendation, not an observation: a justified freestyle decision may differ.
        comparisons = (
            ("service protocol", args.service_protocol, service.get("protocol")),
            ("service URI", args.service_uri, service.get("uri")),
            ("entity set", args.entity_set, service.get("entitySet")),
        )
        for label, selected, observed in comparisons:
            if selected and observed not in (None, "", "unknown", "undecided") and selected != observed:
                errors.append(f"Explicit {label} {selected!r} conflicts with backend contract value {observed!r}")
    return errors


def lockfile_for(version: str, profiles: dict, lockfile_profile: str, template: str) -> Path | None:
    """The template lockfile belongs to one profile; every other profile brings its own."""
    directory = profiles[version].get("lockfileDir")
    if directory:
        candidate = ASSETS / directory / template / "package-lock.json"
        return candidate if candidate.is_file() else None
    return ASSETS / template / "package-lock.json" if version == lockfile_profile else None


def add_evidence(contract: dict, fact: str, status: str, source: str) -> None:
    rows = contract["context"].setdefault("evidence", [])
    if not any(isinstance(row, dict) and row.get("fact") == fact for row in rows):
        rows.append({"fact": fact, "status": status, "source": source})


def add_flp_inbound(manifest_path: Path, semantic_object: str, action: str) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    inbound = {
        "semanticObject": semantic_object, "action": action, "title": "{{appTitle}}",
        "signature": {"parameters": {}, "additionalParameters": "allowed"},
    }
    manifest["sap.app"].setdefault("crossNavigation", {}).setdefault("inbounds", {})[f"{semantic_object}-{action}"] = inbound
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    configure_stdio()
    args = build_parser().parse_args()
    outputs = parse_outputs(args.output)
    profiles, default_profile, lockfile_profile = load_profiles()
    backend: dict | None = None
    backend_path: Path | None = None
    if args.backend_contract:
        backend_path = args.backend_contract.resolve()
        try:
            backend = load_backend_contract(backend_path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            print(f"ERROR: Cannot read backend contract: {error}", file=sys.stderr)
            return 2
        service = backend.get("service", {})
        recommendation = backend.get("recommendation", {})
        args.service_protocol = args.service_protocol or (service.get("protocol") if service.get("protocol") != "unknown" else None)
        args.service_uri = args.service_uri or (service.get("uri") if service.get("uri") != "unknown" else None)
        args.entity_set = args.entity_set or (service.get("entitySet") if service.get("entitySet") != "unknown" else None)
        suggested_framework = recommendation.get("framework")
        args.framework = args.framework or (suggested_framework if suggested_framework in TEMPLATES else None)
    if not args.service_protocol and "code" in outputs:
        args.service_protocol = "odata-v4" if not backend else None
    errors = validate_args(args, outputs, profiles, lockfile_profile, backend)

    target = args.target.resolve()
    contract_target = target / "design-contract.json"
    existing: dict | None = None
    if contract_target.is_file() and not args.reset_contract:
        try:
            existing = json.loads(contract_target.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_pairs)
            if existing["project"]["id"] != args.app_id:
                errors.append(
                    f"The workspace already belongs to {existing['project']['id']!r}; "
                    "use the same --app-id, another target, or --reset-contract"
                )
        except (json.JSONDecodeError, ValueError, KeyError, TypeError) as error:
            errors.append(f"Existing design-contract.json cannot be extended ({error}); repair it or pass --reset-contract")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    # An existing contract is the designer's work: later runs add outputs to it and never start it again.
    trees = {"interactive": (ASSETS / "ui5-prototype", target / "prototype")}
    if "code" in outputs:
        trees["code"] = (ASSETS / TEMPLATES[args.framework], target / "app")
    planned: list[tuple[Path, Path]] = []
    kept_trees: list[str] = []
    added_trees: list[str] = []
    for output, (source, destination) in trees.items():
        if output not in outputs:
            continue
        if existing is not None and destination.exists() and not args.force:
            kept_trees.append(destination.name)
            continue
        planned.extend(plan_tree(source, destination))
        added_trees.append(destination.name)
    try:
        ensure_no_conflicts(planned + ([] if existing is not None else [(ASSETS / "design-contract.template.json", contract_target)]), args.force)
    except FileExistsError as error:
        print(error, file=sys.stderr)
        return 1

    profile = profiles.get(args.ui5_version or default_profile, profiles[default_profile])
    tokens = {
        "APP_ID": args.app_id,
        "APP_PATH": args.app_id.replace(".", "/"),
        "APP_NAME": args.name,
        "LANGUAGE": args.language,
        "UI5_VERSION": profile["ui5Version"],
        "MANIFEST_VERSION": profile["manifestVersion"],
        "UI5_CLI_VERSION": profile["ui5CliVersion"],
        "UI5_LINTER_VERSION": profile["ui5LinterVersion"],
        "UI5_TYPES_VERSION": profile["ui5TypesVersion"],
        "TYPESCRIPT_VERSION": profile["typescriptVersion"],
        "TRANSPILE_VERSION": profile["transpileVersion"],
        "PLAYWRIGHT_VERSION": profile["playwrightVersion"],
        "QUNIT_TYPES_VERSION": profile["qunitTypesVersion"],
        "SERVICE_URI": args.service_uri or "/replace-with-odata-v4-service/",
        "ENTITY_SET": args.entity_set or "ReplaceWithEntitySet",
    }
    if contract_target.is_file() and args.reset_contract:
        shutil.copy2(contract_target, contract_target.with_suffix(".json.bak"))
    if existing is None:
        render_file(ASSETS / "design-contract.template.json", contract_target, tokens)
    # Schemas belong to the skill, not to the designer: keep them in step with the validator.
    render_file(ASSETS / "design-contract.schema.json", target / "design-contract.schema.json", tokens)
    if backend_path:
        target.mkdir(parents=True, exist_ok=True)
        if backend_path != (target / "abap-backend-contract.json").resolve():
            shutil.copy2(backend_path, target / "abap-backend-contract.json")
        render_file(ASSETS / "abap-backend-contract.schema.json", target / "abap-backend-contract.schema.json", tokens)
    for source, destination in planned:
        render_file(source, destination, tokens)
    if "app" in added_trees:
        lockfile = lockfile_for(args.ui5_version, profiles, lockfile_profile, TEMPLATES[args.framework])
        if lockfile and lockfile != ASSETS / TEMPLATES[args.framework] / "package-lock.json":
            render_file(lockfile, target / "app" / "package-lock.json", tokens)
        if args.semantic_object:
            add_flp_inbound(target / "app" / "webapp" / "manifest.json", args.semantic_object, args.action)

    contract = existing if existing is not None else json.loads(contract_target.read_text(encoding="utf-8"))
    fresh = existing is None
    adding_code = "code" in outputs and (fresh or "code" not in existing["project"]["outputs"] or "app" in added_trees)
    if fresh:
        contract["project"].update({"id": args.app_id, "name": args.name, "language": args.language, "outputs": outputs})
        contract["architecture"]["serviceProtocol"] = args.service_protocol or "odata-v4"
        contract["architecture"].update({"framework": "freestyle-sapui5-prototype", "frontendLanguage": "javascript", "floorplan": "dynamic-page-list-with-detail-dialog"})
    else:
        contract["project"]["outputs"] = [item for item in ("png", "interactive", "code") if item in {*contract["project"]["outputs"], *outputs}]

    # The scaffold profile decides tooling and minUI5Version; only an observed value may describe the target system.
    target_system = contract["context"]["targetSystem"]
    if args.target_ui5_runtime:
        target_system["ui5Runtime"] = args.target_ui5_runtime
        contract["context"]["evidence"] = [
            row for row in contract["context"].get("evidence", [])
            if not (isinstance(row, dict) and row.get("fact") == "Target runtime is not yet verified")
        ]
        add_evidence(contract, f"Target SAPUI5 runtime {args.target_ui5_runtime} was supplied to the scaffold; record where it was observed", "assumed", "--target-ui5-runtime")
    add_evidence(contract, f"Scaffold profile {profile['ui5Version']} sets tooling, prototype runtime and minUI5Version; it is not target-system evidence", "verified", "bundled version profile")
    if args.semantic_object:
        target_system["launchIntent"] = {"semanticObject": args.semantic_object, "action": args.action}
        add_evidence(contract, f"Launchpad intent {args.semantic_object}-{args.action} was supplied to the scaffold; verify it against the target catalog", "assumed", "--semantic-object")

    if backend and backend_path:
        backend_source = backend.get("source", {})
        backend_gaps = backend.get("gaps", []) if isinstance(backend.get("gaps"), list) else []
        complete = backend_source.get("complete") is True
        active_only = backend_source.get("activeSourcesOnly") is True
        contract["backendEvidence"] = {
            "applicable": True,
            "status": "source-verified" if complete and active_only and not backend_gaps else "partial",
            "contractFile": "./abap-backend-contract.json",
            "sha256": hashlib.sha256((target / "abap-backend-contract.json").read_bytes()).hexdigest(),
            "sourceMode": backend_source.get("mode", "unknown"),
            "packageName": backend_source.get("packageName", "unknown"),
            "complete": complete,
            "activeSourcesOnly": active_only,
            "gaps": backend_gaps,
        }
        mapped = {row.get("backendObject") for row in contract["traceability"] if isinstance(row, dict)}
        backend_rows = [
            {
                "requirementId": f"BE-{index:03d}",
                "requirement": "Map observed ABAP backend semantics to the UI contract",
                "screenOrControl": "pending-design-mapping",
                "backendObject": row.get("backendObject", "unknown"),
                "backendSource": row.get("sourcePath", "unknown"),
                "serviceOrAnnotation": row.get("uiImpact", "backend-contract"),
                "test": "pending-contract-test",
            }
            for index, row in enumerate(backend.get("traceability", []), 1)
            if isinstance(row, dict) and (fresh or row.get("backendObject") not in mapped)
        ]
        if backend_rows:
            contract["traceability"] = backend_rows if fresh else contract["traceability"] + backend_rows
        if not any(isinstance(row, dict) and row.get("url") == "./abap-backend-contract.json" for row in contract["sources"]):
            contract["sources"].append({"url": "./abap-backend-contract.json", "version": "unknown", "checkedOn": date.today().isoformat()})
        for row in contract["sources"]:
            if isinstance(row, dict) and row.get("url") == "./abap-backend-contract.json":
                row.update({"version": backend_source.get("snapshotSha256", "unknown"), "checkedOn": date.today().isoformat()})

    if adding_code:
        freestyle = args.framework == "freestyle-sapui5"
        contract["architecture"].update({
            "framework": args.framework,
            "minUI5Version": profile["ui5Version"],
            "frontendLanguage": "typescript" if freestyle else "metadata",
            "serviceProtocol": args.service_protocol,
        })
        main_service = contract["dataContract"]["mainService"]
        main_service.update({"uri": args.service_uri, "protocol": args.service_protocol, "entitySet": args.entity_set})
        searchable: bool | str = "unknown"
        if backend:
            main_service["name"] = backend.get("service", {}).get("definition", "mainService")
            main_service["draftEnabled"] = backend.get("behavior", {}).get("draftEnabled", "unknown")
            contract["dataContract"]["actions"] = backend.get("behavior", {}).get("actions", [])
            exposed = {item.get("entitySet"): item.get("sourceEntity") for item in backend.get("service", {}).get("exposedEntities", [])}
            searchable = exposed.get(args.entity_set) in backend.get("uiSemantics", {}).get("searchableEntities", [])
        elif fresh:
            main_service["name"] = "mainService"
        contract["dataContract"]["serverCapabilities"].setdefault("search", searchable)
        if backend:
            contract["dataContract"]["serverCapabilities"]["search"] = searchable
        quality_command = "npm run typecheck" if freestyle else "npm run validate:manifest"
        test_commands = ["npm run test:unit", "npm run test:integration"] if freestyle else ["npm run test:integration"]
        contract["verification"]["commands"] = ["npm ci", quality_command, "npm run lint", "npm run build", *test_commands]
        if fresh:
            # Only a new contract gets the skeleton's own pages; an existing design is the designer's to keep.
            contract["architecture"]["floorplan"] = "dynamic-page-list-with-detail-page" if freestyle else "list-report-object-page"
            contract["informationArchitecture"]["pages"] = [
                contract["informationArchitecture"]["pages"][0],
                {"id": "detail", "titleKey": "itemDetailTitle", "purpose": "Display the selected business object", "sections": []},
            ]
            contract["informationArchitecture"]["navigation"] = [{"from": "main", "to": "detail", "trigger": "row-press", "deepLinkable": True}]
            contract["fieldsAndActions"]["actions"] = []
            contract["fieldsAndActions"]["fields"][0]["labelKey"] = "itemColumn"
    contract_target.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if "png" in outputs:
        (target / "visuals").mkdir(parents=True, exist_ok=True)

    summary = {
        "target": str(target), "contract": str(contract_target),
        "contractMode": "created" if fresh else "kept-and-extended",
        "prototype": str(target / "prototype") if (target / "prototype").is_dir() else None,
        "app": str(target / "app") if (target / "app").is_dir() else None,
        "addedTrees": added_trees, "keptTrees": kept_trees,
        "framework": contract["architecture"]["framework"],
        "targetUi5Version": contract["context"]["targetSystem"]["ui5Runtime"],
        "scaffoldUi5Version": profile["ui5Version"],
        "backendContract": str(target / "abap-backend-contract.json") if backend else None,
        "fileCount": len(planned), "outputs": contract["project"]["outputs"],
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"{'Created' if fresh else 'Extended'} SAP Fiori delivery workspace: {target}")
        print(f"Outputs: {', '.join(summary['outputs'])}")
        if not fresh:
            print("Design contract kept; only scaffold-owned fields were updated.")
        for name in kept_trees:
            print(f"Kept existing {name}/ (pass --force to overwrite it)")
        if summary["prototype"]:
            print(f"Prototype: {summary['prototype']}")
        if summary["app"]:
            print(f"Production app: {summary['app']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
