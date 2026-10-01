# Changelog

English · [Türkçe](CHANGELOG.tr.md)

## 1.4.1 — 2026-10-01

- First public-skills plugin distribution, imported from the merged Yula 1.4.0 source release; source version continuity is retained.
- Publish the complete plugin in both native marketplaces as `yula@aytacmehmet-public` and update English/Turkish installation instructions and the external ZIP builder.
- Preserve runtime retrieval behavior, compressed corpus, retained source licenses and historical qualification reports. Align runtime, host and skill release metadata at 1.4.1.
- Add package hash, marketplace, release-history and runtime checks to the public repository's existing validation workflow.
- Sort delivery payloads by case-sensitive relative POSIX names so Windows and Linux produce the same manifest ordering; regression-tested with an actual delivery build.

Earlier source releases are identified in [upstream provenance](PUBLICATION.json), the [source/interface record](references/provenance.md) and retained versioned test reports. No earlier public-skills plugin release or archive is asserted. Retrieve subsequent previous releases from committed Git history; delivery ZIPs are external artifacts.
