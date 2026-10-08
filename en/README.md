# English skills

[Türkçe](../tr/README.md) · [Repository home](../README.md) · [Contributing and versioning](CONTRIBUTING.md)

| Skill | What it does | Turkish equivalent |
| --- | --- | --- |
| [Prompter](prompter/README.md) | Drafts a contextual prompt, recommends an execution model, asks for approval, and executes in the same conversation. | [Yordamla](../tr/yordamla/README.md) |
| [SAP Fiori Design](sap-fiori-design/README.md) | Designs SAP Fiori for Web screens, reads an ABAP package (and optionally the service `$metadata`) into an evidence-backed contract, and produces a UI5 prototype, recorded PNG captures, and production code from it. | [SAP Fiori Tasarım](../tr/sap-fiori-tasarim/README.md) |

Each skill folder contains the latest instructions, an introduction, UI metadata, optional supporting resources, a changelog, and its own `archived/` folder. The current version is recorded in `SKILL.md` under `metadata.version`.

Install the individual skill folder you want, rather than this entire language directory. Follow the installation section in its introduction. Historical ZIP files are for retrieval and rollback preparation; they are not active skills.

English and Turkish counterparts share a version and behavior but have localized names, descriptions, and documentation. Instructions are usually localized; the SAP Fiori Design pair uses English model-facing text in both packages and still answers in the user's language. Read [Contributing and versioning](CONTRIBUTING.md) before adding a skill or publishing an update.

## Complete plugins

[Yula 1.4.1](../plugins/yula/README.md) bundles released-object advice, ABAP Cloud contracts, configuration architecture, four offline MCP read tools and its populated SQLite corpus for Codex and Claude Code. Install the complete plugin from the repository marketplace; its three skills depend on shared files. [Plugin contribution rules](CONTRIBUTING.md#complete-plugins).

[Belirtim Yazmanı 3.1.0](../plugins/belirtim-yazmani/README.md) documents SAP Cloud ERP developments as self-contained TOON FS-TS, consultant-owned questions and coordinated separate-development handoffs. Install the complete plugin with its shared Python/Node runtime and pinned codec.
