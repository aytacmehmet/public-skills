# ${title} — Design

## Design status and authority

Draft; source baseline and approver are not established. Separate approved design, implemented behavior, and proposed changes.

## Business requirements and boundaries

Record actors, use cases, acceptance criteria, upstream/downstream systems, data/rule authority, and exclusions.

## Architecture and responsibilities

Describe components and responsibilities, reuse shared architecture by link, and justify material tradeoffs with ADRs. Use context/container-level Mermaid diagrams when useful; use a lightweight arc42/C4-inspired structure rather than generating every possible section.

## Data model and contracts

Record keys, semantics, units, cardinality, lifecycle, sources, ownership, validation, and concurrency. Describe CDS/RAP/service contracts, actions, errors, compatibility, idempotency, authorization, and integration behavior where applicable.

## SAP extensibility and release boundary

State the actual product/release and tenant/client evidence. Record released API/CDS/BAdI/BO references and how release status was established. Cover Clean Core, transport/deployment dependencies, and configuration prerequisites. Unverified names or release assumptions remain open.

## Quality and operation

Address relevant authorization, privacy, accessibility, performance, observability, failure handling, recovery, and operational ownership. Link verification and release evidence.
