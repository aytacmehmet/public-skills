# Source and design notes

Maintenance only; not read at runtime and not refreshed from the web per task. Source check dates: 2026-08-27 (SAP sources), 2026-09-23 (package structure). Links to verify live at runtime are in [official-sources.md](official-sources.md).

## Foundations

- [SAP Fiori for Web](https://www.sap.com/design-system/fiori-design-web): floorplans, patterns, visual system, accessibility. Versioned; the skill never treats one version as truth and makes the model open the target-version page.
- [SAPUI5 Demo Kit](https://ui5.sap.com/): API Reference, developer best practices, Fiori elements and testing guides. A working sample does not prove Fiori compliance.
- [ABAP RAP](https://help.sap.com/docs/abap-cloud/abap-rap): business services, behavior definitions, draft, side effects, backend-driven UI.
- [SAP AI Skills Library — sap-fiori-guidelines](https://github.com/SAP/ai-skills-library/tree/main/skills/sap-fiori-guidelines): SAP's experimental Fiori AI skill; useful baseline, needs human verification.
- [OpenAI — Build skills](https://learn.chatgpt.com/docs/build-skills): a distinctive description, instructions loaded on demand, optional references.

## Structural choices

- **Model-facing files are English and shared (1.4.0):** `SKILL.md` (body) and every file under `references/` are identical in the English and Turkish packages; only the `SKILL.md` front matter (`name`, `language`, `counterpart`) differs. The model answers in the user's language. `README.md`, `CHANGELOG.md`, `agents/openai.yaml` and `archived/README.md` stay in the package language because people read them. The repository pair test guards the equality.
- **Token budget:** `SKILL.md` carries only the workflow, gates and commands (about 13 KB); domain knowledge lives in seven references read on demand. References use terse imperative bullets, one primary link per topic and no repeated link blocks; the full link index is `official-sources.md`.
- **Instruction format (1.1.0):** imperative mood, XML sections in workflow order (`<invariants>` … `<resources>`), decision tables, two bad/good examples.
- **Two kinds of reference:** seven domain references read only when needed; `behavior-checks.md` and this file are maintenance-only and `SKILL.md` says so.
- **Contract chain:** `abap-backend-contract.json` → `design-contract.json` → prototype/PNG/code, bound by SHA-256 and checked by the validator so that PNG and code cannot drift apart.
- **Review mode (1.3.0):** `--review` reports new-project conventions (Manifest V2, locale, density) as `warning` and real defects as `error`; contract, package and PNG checks are off. At the delivery gate the same conventions stay `error`.
- **Fail-closed validation:** a warning also closes the gate; the false-positive cost is accepted, which is why color and hard-coded-text checks stay narrow.
- **Gap instead of guess:** the inspector is lexical; unclassifiable elements and ambiguous service/entity-set candidates become `gaps`; `ready` only with no gap left.
- **Two versions:** the scaffold profile sets tooling and `minUI5Version`; the target runtime is written only when observed. One field for both once caused template values to be reported as system findings.
- **Shared runtime:** scripts, schemas, templates and tests are byte-identical in both packages; script messages and contract keys are English.

## Limits

- The inspector is not a compiler, ADT activation, service preview or authorization evidence and does not cover the whole CDS/BDEF syntax. New syntax gap: add a test first, then extend the parser; when in doubt, produce `gaps`.
- One reviewed profile (`assets/version-profiles.json`); template lockfiles belong to it; a new profile needs its own lockfile. Older LTS runtimes are refused until a profile exists.
- The static validator does not replace build, tests, browser rendering, Support Assistant or visual inspection.
- Behavior checks FD01–FD32 are maintenance scenarios, not a guarantee that a model follows every rule in every session.
- Version notes in `official-sources.md` belong to the research date; versioned links may age.
- The skill never writes to an SAP system; activation, transport and deploy are out of scope.

## Distribution and single source

- This repository is the single source. Copies for another host are produced, never hand-edited: `python .github/scripts/skills.py export en/sap-fiori-design --dest <folder> [--name <skill-name>] [--overlay <extra.md>]`. `--name` changes the front-matter name and default invocation; `--overlay` appends a host-specific section (English, model-facing) to `SKILL.md`; `EXPORT-MANIFEST.json` records source version and commit.
- Host rules (authority root, tool gateway, write permission) live in the overlay, never in the core instructions.
- Templates are installed, linted, type-checked, built and browser-tested by a separate CI workflow; the 1.2.0 templates were also verified by hand in Chromium (prototype states, fragment dialog, freestyle list → detail and not-found journeys, Fiori elements smoke test); the 1.3.0 freestyle and Fiori elements skeletons passed install, lint, typecheck/manifest validation and build.
- `scripts/`, `assets/` and `tests/` are deliberately duplicated in both packages: every skill folder must install on its own. The repository test guards the equality.
