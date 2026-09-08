# Documentation Policy

[[Home|Home]] · [[Development-Index|Developments]] · [[Shared-Index|Shared components]] · [[architecture/Overview|Architecture]]

## Placement and identity

Use developments/ID-slug for each development, shared/ID-slug for reusable components, and architecture/ for shared architecture. IDs are stable across renames and never recycled. Record assets under assets/ID/. Templates live in templates/. Required tool instruction files and source-owned package documents stay at their legitimate locations; classify other Markdown before migration.

## Read and update

Read the relevant Current State first. Open details only as needed. Keep long-lived design in Design, active work in Current State, chronological evidence in History, and unresolved questions in Open Items. Append a checkpoint for meaningful changes and maintain navigation. Indexes and page/consumer lists are generated from owning records; do not edit their managed blocks manually.

## Authority and evidence

Record source locations, versions, authority, and the claims they support. Original specifications and code keep their authority. Separate facts, decisions, assumptions, and inferences. Distinguish historical occurrence from documentation time. Correct history by adding a linked correction; preserve accepted decisions and supersede them explicitly.

Local checks, tenant reads, activation, automated tests, business UAT, and go-live approval are separate evidence categories. Record scope, system/client, release, time, outcome, and evidence reference. A source hash proves matching bytes only. Missing evidence remains unverified.

## Links and visual evidence

Use Vault-root-relative wikilinks with forward slashes. Links to attachments include their extensions. In table cells, escape an alias separator as backslash plus pipe. Maintain both useful navigation and dependency ownership; Obsidian computes backlinks from actual links. Keep business flow descriptions next to Mermaid diagrams. Record real screenshot provenance and whether a screen is a mockup, local preview, or tenant capture.

## Lightweight context

Current State should usually fit in roughly one screen of prose (about 300–600 words); split detail when justified. Record the next executable action, accepted constraints, active blockers, last actual verification, and relevant links. Refresh source fingerprints only after reviewing changed evidence. Preserve detailed history when creating a shorter continuation summary. No fixed token saving is guaranteed.
