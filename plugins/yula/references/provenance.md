# Source and interface provenance

English · [Türkçe](provenance.tr.md)

Yula derives the object/evidence/member/public-content schema and retrieval semantics from the supplied SAP Brain package, and the release-partitioned configuration catalog, XML workbook importer and evidence lifecycle from the supplied SAP Configuration Architect skill. Only the reachable workbook/canonical-import call graph is retained in `runtime/yula/vendor/sca.py`; unused CLI commands, host mutation paths and bulk prompt templates are excluded.

The original advisor/developer distinction is preserved. Shared rules now live in one conditional reference; configuration's former mandatory reference fan-out and mandatory write-after-every-answer are replaced by task-specific retrieval and explicit useful-evidence recording. No VOLTRAN gateway, SAP development runtime, Node/npm dependency or live credentials are needed for offline operation.

Official released-catalog authority: [SAP Cloudification Repository](https://github.com/SAP/abap-atc-cr-cv-s4hc), exact [Public Edition JSON](https://raw.githubusercontent.com/SAP/abap-atc-cr-cv-s4hc/main/src/objectReleaseInfoLatest.json). SAP's source license and attribution are retained under `LICENSES/`.

Documentation source: [SAP Help Portal](https://help.sap.com/docs/). Stored topics retain exact document/topic IDs, edition/version and URL. Original unknown fetch dates remain unknown. Configuration workbook release and hashes are captured in the seed manifest/source entries; curated dossiers and project lessons are not SAP-authored statements.

Transport contract: [MCP stdio specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports). Yula implements newline-delimited JSON-RPC initialization, ping, tool discovery and calls; it advertises only implemented tools. No HTTP transport, resource subscription, prompts, elicitation or SAP execution capability is advertised.

Legacy operation mapping:

| Legacy operation | Yula interface |
|---|---|
| check_objects_released | yula_check |
| find_released_objects | yula_search: catalog |
| find_objects_by_capability | yula_search: objects; results distinguish curated mappings from lexical candidates |
| get_object_context / get_object_content | yula_get: object summary/members/declaration/sources |
| search_abap_docs / read_abap_doc_topic | yula_search: docs / yula_get: topic |
| recall_lessons | yula_search: lessons; candidate/project status retained |
| index/object/docs status | yula_status |
| source synchronization | scripts/yula.py check/apply/rollback |
| SCA query / activity | yula_search: configuration / yula_get: activity sections |
| SCA import-catalog / build-index | configuration-workbook / configuration-root maintenance adapters |
| research/incident/lesson/release recording | knowledge-records maintenance adapter with immutable revisions |

Legacy names are mapped rather than simultaneously registered as aliases, avoiding duplicate MCP schemas. Full tool metadata is discoverable through `tools/list`; the SQLite payload is never injected into prompt context.
