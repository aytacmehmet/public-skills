# SAP Fiori Design

[English catalog](../README.md) · [Türkçe: SAP Fiori Tasarım](../../tr/sap-fiori-tasarim/README.md)

Designs an SAP Fiori for Web screen starting from the business task, then turns the same design into a running prototype built with real SAPUI5 controls, PNG captures, and production code. Given an ABAP package, it reads the CDS/RAP/service sources and ties the UI to that contract. It never treats what it has not seen as verified: every assumption, gap, and version stays in the contract as `verified`, `assumed`, or `unknown`.

## Languages and install

This package's instructions and references are in English. The [Turkish equivalent](../../tr/sap-fiori-tasarim/README.md) provides the same behavior with Turkish instructions. Scripts, tests, schemas, and UI5 templates are byte-identical in both packages; script messages, finding codes, and contract keys are deliberately English. The language of the generated application is chosen with `--language tr|en`; the shared default is `tr`, so pass `--language en` for an English application.

With Skill Installer available:

```text
$skill-installer Install the skill from https://github.com/aytacmehmet/public-skills/tree/main/en/sap-fiori-design
```

Alternatively, copy this individual folder into a skill discovery directory supported by your environment. Consult the [official skill documentation](https://learn.chatgpt.com/docs/build-skills) for the appropriate location. Preserve an existing installation before replacing it and confirm that the skill appears in your skill list. Do not install the English and Turkish packages side by side; they trigger on the same work under two names.

The scripts use only the Python 3.12+ standard library. The production templates require Node.js `^20.11.0 || >=22` and npm 10+; dependencies are pinned exactly to the profile in `assets/version-profiles.json`.

## Use

```text
$sap-fiori-design Design a List Report + Object Page for sales order approval; produce PNG captures and an interactive prototype. The target system is S/4HANA Cloud Public Edition.
```

```text
$sap-fiori-design Inspect the ABAP package in ./abapgit-export, derive the backend contract, and generate the matching Fiori elements app. Service URI: /sap/opu/odata4/...; target SAPUI5 runtime 1.152.1.
```

```text
$sap-fiori-design Review the existing webapp/ project against the Fiori guidelines, accessibility, and deprecated API use; report findings with file and line.
```

## How it works

```text
requirements ─┐
              ├─> abap-backend-contract.json ─> design-contract.json ─┬─> prototype/   (running UI5 with mock data)
ABAP package ─┘      (inspect_abap_package)     (scaffold_fiori_…)    ├─> visuals/*.png (captured from the prototype)
                                                                      └─> app/          (TypeScript or Fiori elements V4)
                                            validate_fiori_delivery: schema, hash chain, contract ↔ manifest, risky patterns
```

- **Backend contract:** extracts entities, fields, keys, associations, draft, actions, validations, authorization, and the service boundary from a local ADT/abapGit folder, a ZIP, or a read-only ADT snapshot. It does not guess at an element it cannot read or at several service or entity set candidates; it records them in `gaps`.
- **Design contract:** the single source for PNG, prototype, and code; it carries pages, fields, actions, states, responsive behavior, accessibility, and requirement → control → backend object → test traceability.
- **Version separation:** `--ui5-version` selects only the scaffold profile (tooling and `minUI5Version`). The runtime observed in the target system is passed with `--target-ui5-runtime`; without it the value stays `unknown` and the delivery gate stays closed.
- **Validator:** fails on warnings as well. `--allow-warnings` is only for work in progress.

## Verification and limits

```text
python -B tests/test_skill_tools.py
```

The tests cover scaffold inputs, ABAP package reading (abapGit/ADT service binding formats, multi-entity behavior definitions, element lists with inline annotations), ZIP path safety, hash integrity, schema enforcement, and the version check.

The inspector is a lexical reader; it is not the ABAP compiler, ADT activation, a service preview, or runtime authorization evidence. A `ready` result does not replace the real `$metadata`, the target release, or released-object verification. The static validator does not replace build, tests, browser rendering, and visual inspection. The skill does not write to an SAP system and performs no activation, transport, or deployment; it never asks for a password or key in the conversation. The version notes in `references/official-sources.md` belong to their research date; verify the target version against the live source.

## Files and versions

- [SKILL.md](SKILL.md): imperative instructions in XML sections — invariants, reference routing, scope slots, evidence, contract, architecture, prototype, production, verification, self-check, and delivery — plus version metadata.
- [UI metadata](agents/openai.yaml): display name, description, and default prompt.
- Domain references, read at runtime only when needed: [design foundations](references/design-foundations.md), [floorplans and patterns](references/floorplans-and-patterns.md), [UI5 engineering](references/ui5-engineering.md), [ABAP package intake](references/abap-package-intake.md), [RAP backend contract](references/rap-backend-contract.md), [delivery and quality](references/delivery-and-quality.md), [official sources](references/official-sources.md).
- [Behavior checks](references/behavior-checks.md): FD01–FD26 are maintenance scenarios, not a claim that every scenario passes in every environment. Not read at runtime.
- [Source and design notes](references/source-notes.md): foundations, structural choices, and limits. Not read at runtime.
- `scripts/`, `assets/`, `tests/`: scripts, schemas, UI5 templates, and script tests that are byte-identical in both languages.
- [Changelog](CHANGELOG.md) and [archived releases](archived/README.md).
- [GPL-3.0 license](LICENSE).

The current version is 1.1.0 and lives directly here, not in `latest/` or a version-numbered subfolder. Previously published releases are kept in `archived/` as unmodified ZIP copies following the repository's [versioning instructions](../CONTRIBUTING.md). Do not extract those ZIPs inside a skill discovery directory.
