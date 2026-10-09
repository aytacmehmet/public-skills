# Spec Writer skill

English · [Türkçe](README.tr.md)

## Scope
One shared model-facing entrypoint for Claude Code and Codex. It reads only applicable references
and calls the plugin-owned runtime. It has no skill-local dependency or executable ownership.
Use the [plugin guide](../../README.md) for installation, migration, review gates and tests.
Respond in the user's language; Turkish is the default. The rule body is English.

## Work profiles
Version 3.2.0 adds Lite / Yalın, Plus / Gelişmiş, Pro / Yetkin, Max / Doruk and Ultra / Üstün as private work intensity choices. One recommendation card precedes the user's choice. Preparation, attempt budgets, host capacity and provider-local model suggestions vary; three full-scope readers, two clean final rounds and human approval stay common. Document profiles `hafif/standart/tam` remain separate. Use [work-profiles](references/work-profiles.md) only when this route applies; the runtime never automatically selects a model or launches provider subprocesses. Package discovery and synthetic tests are not native execution or measured savings.

Version 3.2.1 corrects native Codex manifest selection and portable Windows hook launch after Codex 0.160.0 probes. The active host manifest is `.codex-plugin/plugin.json`; portable metadata lives at `metadata/agent-plugin.json`. The five-profile protocol, all 22 rules and their existing quality gates remain unchanged. Use the complete updated plugin package; native trust/event execution and provider cost still require their own evidence.

3.2.2 stores each complete reader source once by file hash and retains pointer bindings. That historical version used protocol 3.2; current work requires protocol 3.3 and fresh execution confirmation; historical packets are explicit read-only compatibility.

## 3.3 selective routes and acceptance
Use [intake/capacity](references/work-profiles.md), [native dispatch](references/dispatch.md) or [models/cost](references/models.md) only when needed. Protocol 3.3 binds roles and oracle admission; packet sources remain complete. read-reference supports repeated IDs in one call. The plugin-root scripts/check.py selects changed checks and runs the stable final suite once; final three-reader/two-clean-round handoff gates remain.
