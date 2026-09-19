# Contributing and versioning

[English catalog](README.md) · [Türkçe](../tr/CONTRIBUTING.md)

## Add a skill

Create one folder under `en/` and its Turkish counterpart under `tr/`. Use short lowercase names with hyphens where needed. Names may differ by language, as `prompter` and `yordamla` do.

Each package needs `SKILL.md`, `README.md`, `CHANGELOG.md`, a copy of the repository `LICENSE`, `agents/openai.yaml`, and `archived/README.md`. Add `references/`, `scripts/`, or `assets/` only when the skill needs them. Keep all introductions, instructions, UI descriptions, and supporting explanations in the package's language; preserve the original legal text of LICENSE.

`SKILL.md` frontmatter identifies the skill and the paired release:

```yaml
name: prompter
description: Describe this skill and its precise trigger.
metadata:
  version: "1.0.0"
  language: "en"
  family: "contextual-prompting"
  counterpart: "tr/yordamla"
```

The counterpart must point back, use the other language, and share the family and version. A new skill uses its own family identifier. Register both packages in the language catalogs. Check the translation for behavioral equivalence; structural validation cannot prove that translation is correct.

For a first public release, start at `1.0.0`. Keep only the archive guide in `archived/`; do not invent a previous release.

## Update a published skill

Keep the latest files at the package root. Do not introduce a `latest/` directory or move the active skill into a version-number directory.

1. Start from an up-to-date checkout of `main`. Archive the current **committed** release of both language packages before preparing the next release:

   ```text
   python .github/scripts/skills.py archive en/prompter --ref HEAD
   python .github/scripts/skills.py archive tr/yordamla --ref HEAD
   ```

   The helper reads Git, not uncommitted edits. It writes `archived/v1.0.0.zip` for version `1.0.0`, refuses to replace an existing snapshot, and never includes older archives inside the ZIP. It does not edit the active skill or commit/push anything.

2. Edit the current files in place. Increase `metadata.version` in both languages using `MAJOR.MINOR.PATCH`: major for incompatible behavior, minor for added capabilities, patch for compatible fixes or documentation updates. Add matching localized changelog entries and review both introductions.
3. Preserve every previously published ZIP byte-for-byte. A snapshot contains the previous package and `ARCHIVE-MANIFEST.json`, which records its Git source and per-file SHA-256 hashes.
4. Run the checks below. Include the new archive ZIPs, both updated packages, and relevant catalog changes in the same commit. Review the diff before pushing.

Any change to a published package's active files, including its documentation or license copy, needs a version bump and the previous snapshot. Language catalog changes alone do not change a skill version. The two translations advance together even when a correction starts in only one language.

## Validate

From the repository root, with Python 3.12 or later and Git:

```text
python -m pip install -r .github/requirements.txt
python -B -m unittest discover -s .github/tests -v
python -B .github/scripts/skills.py validate --base HEAD
```

Before committing, `--base HEAD` checks your edits against the previous committed release. After committing, use the previous commit or a known earlier release as the base. Omit `--base` for structural checks only. GitHub Actions compares a push with its previous head, and a pull request with its base commit.

Checks cover metadata, UI invocation, local links, language pairing, version alignment, archive hashes, retention of published archives, and preservation of the exact previous package. They do not establish runtime behavior, UI compatibility, or token savings; test relevant scenarios separately when behavior changes.

## Produce a copy for another host

The repository is the single source of the skills. When a plugin or another host needs a copy, do not copy and edit the active package by hand:

```text
python .github/scripts/skills.py export en/sap-fiori-design --dest <folder-outside-the-repo> --name <host-name> --overlay <host-rules.md>
```

The command copies everything except `archived/`, optionally renames the skill and its default invocation, appends the overlay file to the end of `SKILL.md`, and records the source version and commit in `EXPORT-MANIFEST.json`. Host-specific rules stay in the overlay; fixes are made here first and the copy is produced again. The destination must be outside the repository and empty.

## Inspect an old release

Keep historical ZIPs inside their skill's `archived/` folder. Extract one only into an isolated directory outside skill discovery paths. Verify its manifest before preparing a rollback or a separate installation. Never unpack archived `SKILL.md` files underneath an active installation.

Every directory directly under a language root is a skill package and must contain SKILL.md. Default invocations must mention the exact skill name; $prompter-old does not count as $prompter.
