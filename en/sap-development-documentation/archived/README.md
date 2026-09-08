# Archived releases

This first public release has no earlier snapshots. The current version lives in the [parent skill folder](../README.md).

Before a future update, archive both language packages' previous committed releases using the repository's [versioning instructions](../../CONTRIBUTING.md). Snapshots are named `vMAJOR.MINOR.PATCH.zip` and include an `ARCHIVE-MANIFEST.json` with source commit and per-file hashes. The archive helper excludes the archive directory itself.

Preserve published ZIPs byte-for-byte. Inspect them only by extracting outside skill discovery directories and verifying the manifest; do not register archived SKILL.md files as active skills.
