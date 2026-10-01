# Installation and host updates

English · [Türkçe](installation.tr.md)

## Prerequisites

Use Python 3.11+ with SQLite FTS5, exposed as `python` in the host PATH, and a current Claude Code or Codex CLI with plugin support. The repository is public; private GitHub access is not required. No credentials belong in plugin files. Run from `plugins/yula`: `python scripts/preflight.py --host both`, or choose only `claude` / `codex`.

## GitHub marketplace

Claude Code terminal commands:

```text
claude plugin marketplace add aytacmehmet/public-skills
claude plugin install yula@aytacmehmet-public
claude plugin list
```

Codex terminal commands:

```text
codex plugin marketplace add aytacmehmet/public-skills --sparse .agents --sparse .claude-plugin --sparse plugins/yula
codex plugin add yula@aytacmehmet-public
codex plugin list --marketplace aytacmehmet-public
```

The sparse paths retain both the root marketplace and the complete plugin. Both hosts use one runtime, three skills and four read tools; `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` provide their respective metadata. Claude Code starts the MCP server from `.mcp.json`; Codex does not expand `${CLAUDE_PLUGIN_ROOT}`, so the Codex manifest declares the same server inline with `cwd: "."`, which resolves to the installed plugin root. `agents/openai.yaml` is Codex interface metadata, not a Claude subagent.

## Local repository or delivery ZIP

The delivery ZIP holds one `yula-marketplace/` folder with the repository layout: `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json` and `plugins/yula/`. Extract it to a stable directory. Register the extracted **marketplace root** (`yula-marketplace`), not its `plugins/yula` subdirectory or ZIP file.

```text
claude plugin marketplace add "/absolute/path/to/marketplace"
claude plugin install yula@aytacmehmet-public
codex plugin marketplace add "/absolute/path/to/marketplace"
codex plugin add yula@aytacmehmet-public
```

The ZIP's marketplace contains only Yula; the repository marketplace may list other plugins. Keep the source directory while it is registered. To switch marketplace origins, use the host's marketplace management commands; do not register two origins under the same marketplace name at once. For a Claude development session, `claude --plugin-dir "/absolute/path/to/marketplace/plugins/yula"` loads Yula directly. Do not load the same plugin twice.

## Activation and storage

Start a new session after installation/update. Claude commands are `/yula:sap-released-object-advisor`, `/yula:sap-released-object-developer` and `/yula:sap-configuration-architect`. Codex exposes the same skills in its picker. Automatic selection remains enabled. Claude `/mcp` should show `plugin:yula:yula`; Codex `mcp list` shows the registered server. Registration alone is not a successful tool call.

The manifest selects `--data-root @user/yula`. Set `YULA_DATA_ROOT` in the host's launch environment before starting it to select a different external corpus (Codex forwards it through the manifest's `env_vars`); otherwise the OS user data directory is used. Both hosts share it by default. First lookup verifies and expands the included ZIP offline. Plugin updates preserve existing working data. CLI maintenance requires `--data-root` or the environment variable; choose the same target as the host.

## Updating

Use the host's marketplace update and plugin update flow, then restart the session and check installed version and a tool response. Read that installed CLI's `plugin --help` for its update syntax. Reinstalling a plugin does not refresh the working corpus; use explicit `check` / hash-bound `apply`. Storage revision 2 remains compatible with 1.2.0. Older working corpora can stage `migrate` on the selected data root before applying its plan.

## Format references

[Claude plugin format](https://code.claude.com/docs/en/plugins-reference), [Claude marketplace format](https://code.claude.com/docs/en/plugin-marketplaces), [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins). The installed CLI checks and repository CI establish local compatibility; they do not verify a model conversation or live SAP behavior.
