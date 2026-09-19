# Source and design notes

Source check date: 2026-08-27 (SAP sources), 2026-09-19 (package structure). This file is for maintenance; it is not read at runtime and is not refreshed from the web for every design. The links to be verified live at runtime are in [official-sources.md](official-sources.md).

## Foundations

- [SAP Fiori for Web](https://www.sap.com/design-system/fiori-design-web): floorplan, pattern, visual system and accessibility rules. The guideline is versioned; the skill does not accept a fixed version as the truth, it has the versioned page that fits the target opened.
- [SAPUI5 Demo Kit](https://ui5.sap.com/): API Reference, developer best practices, Fiori elements and testing guides. The fact that a sample works does not prove that the pattern is Fiori compliant.
- [ABAP RAP](https://help.sap.com/docs/abap-cloud/abap-rap): business service, behavior definition, draft, side effects and backend-driven UI features.
- [SAP AI Skills Library — sap-fiori-guidelines](https://github.com/SAP/ai-skills-library/tree/main/skills/sap-fiori-guidelines): SAP's experimental Fiori AI skill; a useful baseline, requires human verification.
- [OpenAI — Build skills](https://learn.chatgpt.com/docs/build-skills): a distinctive description, a guideline loaded when needed and optional references.

## Structural choices

- **Guideline format (1.1.0):** `SKILL.md` is written in the imperative mood, with XML sections (`<invariants>`, `<references>`, `<scope>`, `<evidence>`, `<contract>`, `<architecture>`, `<prototype>`, `<production>`, `<verification>`, `<self_check>`, `<delivery>`, `<resources>`), decision tables and two good/bad examples. The section names follow the order of the workflow.
- **Two kinds of reference:** the domain references (seven files, about 75 KB) are read at runtime only when needed; Fiori/UI5/RAP knowledge is too broad to fit into a single file, and loading it on every invocation is an unnecessary cost. `behavior-checks.md` and this file are for maintenance only, and `SKILL.md` says so explicitly.
- **Contract chain:** `abap-backend-contract.json` → `design-contract.json` → prototype/PNG/code. The contracts are bound with SHA-256; the validator checks the chain. The goal is to prevent the PNG and the code from being "designed" separately and drifting apart.
- **Fail-closed validation:** a warning also closes the gate. The cost of false positives is accepted deliberately; this is why the color and hard-coded text checks are kept narrow.
- **A gap instead of a guess:** the inspector is a lexical reader. It does not choose an element it cannot classify, or among more than one candidate service or entity set; it writes it into `gaps`. The `ready` result is given only when no gap remains.
- **Two separate versions:** the scaffold profile determines the tooling and the `minUI5Version` value; the target runtime is written only when it is observed. Writing both into the same field led to the template value being reported as a system finding.
- **Shared runtime:** the scripts, schemas, templates and tests are byte-identical in the two language packages; the script messages and contract keys are in English. The repository test preserves this equality.

## Limits

- The inspector is not an ABAP compiler, an ADT activation, a service preview or runtime authorization evidence; it does not cover the whole CDS/BDEF syntax. When a new syntax gap is found, add a test first, then extend the parser; when in doubt, produce `gaps`.
- There is a single reviewed profile (`assets/version-profiles.json`). The template lockfiles belong to that profile; a new profile requires its own lockfile. For older LTS runtimes, the production scaffold is refused until a profile is added.
- The static validator does not replace build, test, browser rendering, Support Assistant and visual inspection.
- It is not claimed that the behavior checks (FD01–FD32) pass in every environment; they are maintenance scenarios. The skill cannot guarantee that a model will follow the rule in every session.
- The version notes in `official-sources.md` belong to the research date; links with version numbers may become outdated.
- The skill does not write to the SAP system; activation, transport and deploy are out of scope.

## Distribution and single source

- This repository (`public-skills`) is the single source of the skill. A copy that goes to another host (for example into a plugin) is not edited by hand; it is produced with `python .github/scripts/skills.py export en/sap-fiori-design --dest <folder> [--name <skill-name>] [--overlay <extra.md>]`. `--name` changes the front matter name and the default invocation; `--overlay` appends the host-specific section to the end of `SKILL.md`. The exported copy carries the source version and commit in `EXPORT-MANIFEST.json`.
- Host-specific rules (authority root, tool gateway, write permission) live in the overlay file; they are not moved into the core instructions.
- The templates are really installed, linted, type-checked, built and browser-tested by a separate workflow in the repository CI; the 1.2.0 templates were verified this way and by hand in Chromium (the prototype's six states, the fragment dialog, the freestyle list → detail and not-found journeys, the Fiori elements smoke test).
- The shared `scripts/`, `assets/` and `tests/` are deliberately duplicated in both language packages: the repository rule requires every skill folder to be installable on its own. The repository test guards their equality.
