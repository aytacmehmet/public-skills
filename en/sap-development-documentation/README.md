# SAP Development Documentation

[English catalog](../README.md) · [Türkçe: SAP Geliştirme Dokümantasyonu](../../tr/sap-gelistirme-dokumantasyonu/README.md)

Maintain development design, progress, decisions, dependencies, SAP object inventories, and evidence in one project-local Obsidian Vault. A short Current State helps a new task resume without reading the entire history.

## Languages and installation

This package's instructions are English. Its [Turkish counterpart](../../tr/sap-gelistirme-dokumantasyonu/README.md) provides equivalent Turkish instructions. **Both versions generate English Vault documentation.** Generated document templates, their prose, schema keys, command names, and structured helper diagnostics intentionally remain English. Implementation and tests are shared byte-for-byte; each generated project instruction snippet invokes its own package name.

With Skill Installer available:

```text
$skill-installer Install the skill from https://github.com/aytacmehmet/public-skills/tree/main/en/sap-development-documentation
```

Alternatively, copy this individual skill folder into a location supported by your Codex host. See the [official skill documentation](https://learn.chatgpt.com/docs/build-skills). Preserve any existing installation before replacing it; verify that this skill appears in the selector. A new turn or client restart may be needed. Do not unpack old releases inside a skill discovery directory.

The helper requires Python 3.12+ and PyYAML 6.x; its dependency is listed in [requirements](scripts/requirements.txt). This baseline supports the directory-junction checks on Windows. No Obsidian community plugin or background service is needed.

## Use

Open a task on the actual project, then request the relevant operation:

```text
$sap-development-documentation Set up this project's English Obsidian development documentation, preserve existing source authority, and install the project documentation guidance.
```

```text
$sap-development-documentation Resume DEV-001 from Current State. Inspect changed sources and the required dependency contracts before updating its records.
```

```text
$sap-development-documentation Document the completed changes from the supplied source files and history. Separate occurrence time from recording time and keep missing evidence as open items.
```

Setup resolves the real project root, creates or adopts `obsidian/`, and can merge a short rule into the effective project instruction file. An existing unmanaged Vault is inspected and mapped before adoption. A temporary chat folder is not automatically treated as a SAP project. Relevant authorized development work includes updating its documentation; a separate documentation request is not required for every change.

## Organization and retrieval

- `developments/<ID>-<slug>/`: a separate folder for each development.
- `shared/<ID>-<slug>/`: reusable components and their contracts.
- `architecture/`: common architecture and cross-cutting decisions.
- Four core pages per entity: Overview, Current State, History, and Open Items.
- Optional pages: Design, Process, Objects, UI, Verification, Sources, Handover, and individual ADRs.
- `assets/<ID>/`: genuine screenshots and evidence; `templates/`: English output templates.

Wikilinks provide page navigation, relationships, and Obsidian backlinks. The dependency list records consumer-to-provider direction; generated consumer lists provide reverse navigation. Shared facts stay with one owner. Original approved specifications and code keep their authority.

Resume retrieval reads the selected Current State, direct dependencies, and source-drift indicators; it does not load every journal. Meaningful changes append an immutable event identity and refresh the current checkpoint. Repeating an identical event is a no-op; corrections use a new event. This reduces unnecessary reading by design, without claiming measured token savings.

## Verification and limits

```text
python -X utf8 -B scripts/test_vault.py
```

The isolated suite covers initialization, navigation, dependencies, source drift, event replay, history retention, path containment, and concurrent edits. See [operations](references/operations.md) for commands and validation scope. Project guidance and the helper's checks direct file placement; a skill cannot prevent every arbitrary filesystem write or guarantee that every future session follows its guidance.

Structural validation does not establish prose quality, complete business coverage, diagram rendering, screenshot provenance, or SAP tenant readiness. Track local checks, tenant reads, activation, runtime tests, business UAT, and go-live approval separately. Test relevant diagrams and UI evidence in the actual target environment.

## Package

[Instructions](SKILL.md) · [Vault contract](references/vault-contract.md) · [Operations](references/operations.md) · [Sources](references/sources.md) · [Changelog](CHANGELOG.md) · [Archives](archived/README.md) · [GPL-3.0 license](LICENSE)

This is the first public release, version 1.0.0. Current files live at this package root. Future updates archive the previous committed version according to the repository's [versioning instructions](../CONTRIBUTING.md).
