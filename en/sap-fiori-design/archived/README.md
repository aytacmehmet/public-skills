# Archived releases

Previous public releases are stored here. For a first release, this folder contains only this guide. The current release lives in the [parent skill folder](../README.md).

When preparing an update, save the preceding committed version here as `vMAJOR.MINOR.PATCH.zip`. Each ZIP contains the complete previous package at its root and an `ARCHIVE-MANIFEST.json` file with per-file SHA-256 hashes. Snapshots exclude the `archived/` folder itself, so archives never contain earlier archives.

Published snapshots must not be replaced or deleted. Keep them zipped here: extracting old `SKILL.md` files inside a discovery directory may register duplicate skills. To inspect or prepare a rollback, extract a chosen ZIP outside skill discovery directories and verify its manifest before deciding what to install.

Follow the repository's [versioning instructions](../../CONTRIBUTING.md) when preparing a new release.
