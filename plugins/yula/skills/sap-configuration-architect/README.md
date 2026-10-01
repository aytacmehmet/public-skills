# Configuration architect

English · [Türkçe](README.tr.md)

Resolve release-specific SSCUI/CBC activities, dependencies, diagnosis and change impact. SAP tenant execution is outside this skill.

## Installation

Included in **Yula 1.4.1**. Install the [complete plugin](../../README.md); this skill depends on its shared MCP server, rules and SQLite corpus. Do not install a second standalone copy.

## Usage

Automatic invocation is enabled. In Claude Code, use `/yula:sap-configuration-architect` when explicit invocation is preferred. In Codex, select the Yula skill in the skill picker.

Answers follow the user's language. Technical identifiers stay unchanged. The model-facing rules are English and load detailed references only when needed.

## Evidence boundary

Local catalog and source evidence do not establish target-tenant availability, activation, authorization or runtime success. Missing evidence stays explicit.
