# Deriving the UI contract from an ABAP package

Read when a UI5/Fiori screen is requested from an ABAP package, ADT project, abapGit export or package name.

## Purpose and boundary

Produce the machine-readable `abap-backend-contract.json` before interpreting package sources as a screen requirement. It ties the inventory, the RAP/CDS/OData capabilities and the source file of every inference to the UI design. Reading source does not prove the backend's business purpose: never invent a requirement, role, process, published service URI, target release or runtime authorization that the package does not contain. The parser is lexical; it is not compiler, activation, service-preview or authorization evidence.

## Inputs

### Local package (ADT/abapGit folder or ZIP)

```powershell
python -B "<skill root>/scripts/inspect_abap_package.py" <package-folder-or-zip> `
  --output <output>/abap-backend-contract.json `
  --package-name Z_MY_PACKAGE `
  --service-uri /sap/opu/odata4/sap/z_ui_service/srvd/sap/z_ui_service/0001/ `
  --protocol odata-v4
```

`--service-uri` only when observed in the target system; never derived from source. Add `--metadata <file>` with the service `$metadata` observed or exported from the target system: the contract then records `service.metadata` (file hash, protocol, every entity set with its declared `$search` support from V4 `Capabilities.SearchRestrictions/Searchable` or V2 `sap:searchable`, `null` when undeclared), and a protocol mismatch or a leading entity set absent from the metadata becomes a gap. DTD/entity declarations are rejected.

Several service definitions: the inspector never picks the first. It selects the definition that every readable service binding names (evidence); otherwise `service.definition` stays `unknown` with a gap. With a single definition, a binding that names another definition keeps the selection and adds a gap. Override with `--service-definition <name>`; if the service exposes several entities and no single root entity stands out, name the leading set with `--entity-set <name>`. Both flags are case-insensitive; choose both from source or `$metadata` evidence.

Binding protocol is read from `ODATA V4`-style text or from separate type + version fields (`<TYPE>ODATA</TYPE><VERSION>V4</VERSION>`, `type="ODATA" version="V2"`); otherwise `unknown`.

### Live ADT package (read-only tools only)

Example tool names belong to the `sap-cloud-erp` MCP server; use the equivalent read operations on another host.

1. Load the read-only tool profile (`load_toolset(profile="source-read")`).
2. Read the package list with all pages (`list_packages`; continue while `truncated=true` or `nextOffset` is present).
3. Read the `DDLS`, `DDLX`, `BDEF`, `SRVD`, `SRVB`, `DCLS` and relevant `CLAS` sources from the **active** version (`read_source`, `read_cds_source`, `read_repository_object`).
4. For paged sources pass the previous `sha256` as the expected hash on each continuation (`expectedSha256`); a source is complete only after its last page. Paging is the tool's job; the inspector does not page.
5. Save the normalized snapshot without credentials/host/client and feed it to the inspector.

```json
{
  "packageName": "Z_MY_PACKAGE",
  "objectCount": 3,
  "objects": [
    {"name": "Z_I_ORDER", "type": "DDLS/DF", "uri": "/sap/bc/adt/ddic/ddl/sources/z_i_order",
     "version": "active", "truncated": false, "source": "define root view entity Z_I_Order ..."}
  ]
}
```

Snapshot fields: `name` (or `objectName`), `type` (or `objectType`) and `source` are mandatory; `uri`, `version` (absent = `active`, verify yourself), `truncated` and `sha256` are optional. A given `sha256` is compared with `source` and a mismatch aborts with exit 2; `truncated: true` adds a gap per object and sets `complete: false`; `inventoryVerified` becomes `true` when `objectCount` equals the number of objects.

```powershell
python -B "<skill root>/scripts/inspect_abap_package.py" <adt-snapshot.json> `
  --output <output>/abap-backend-contract.json --service-uri <observed-uri> --protocol odata-v4
```

No SAP connection → ask for a local export or report the missing connection as a blocker; never ask for a password, RSA or private key. Reading grants no write, activation, publish, transport or deploy right.

## Reading priority

Large package → thin end-to-end slice first: 1 `SRVB` + `SRVD` (protocol, published service, entity-set boundary) · 2 projection `DDLS` + `DDLX` (exposed fields, associations, annotations) · 3 projection/root `BDEF` (draft, CUD, actions, validations, side effects) · 4 interface/root `DDLS` (keys, compositions/associations, currency/unit/text/value help) · 5 `DCLS` and behavior authorization · 6 only the behavior implementation methods that affect UI behavior. Over 200 objects: record the paging and reading plan in the contract; never skip an object by name silently — record per type why it is out of scope.

## Reading the inspector output

- `model.entities[].fields/keys`: elements read from the element list; `exposedAssociations` are navigation candidates, not fields.
- `model.entities[].unparsedElements`: elements the lexical reader could not classify (e.g. an alias-less `case`). One gap per entity (first three listed) blocks `ready`; verify against `$metadata` and map manually.
- `model.entities[].kind`: `view-entity`, `custom-entity`, `abstract-entity`, `classic-view`. Abstract entities are action parameters, not screen objects; a custom entity's query lives in an ABAP class — verify filter/sort/paging with `$metadata` and a test.
- `model.associations[]`: `association … to` and `composition … of`, distinguished by `kind`; derive navigation, sections/tables and the `$expand` budget from them. Facets are not summarized: read the DDLX source for `@UI.facet`.
- `behavior.definitions[]`: one record per `define behavior for`; parenthesized `create/update/delete` (`update ( features : instance );`) is recognized; `createByAssociation` keeps sub-object creation separate.
- `behavior.actions` are business actions; `draftActions` (Edit, Activate, Discard, Resume, Prepare) belong to the framework and are never buttons. The five names classify only `use action` lines of a projection; anything declared with `draft action` / `draft determine action` lands in `draftActions` regardless of name.
- `dynamicFeatureControl`: operations/actions whose enablement is decided at runtime — plan their disabled/hidden state and its test.
- `etag` and `totalEtag` are separate; write the concurrency scenario for both.
- `uiSemantics.fields`: field → annotation map from DDLS and DDLX, summarized in `lineItemFields`, `selectionFields`, `identificationFields`, `fieldGroupFields`, `hiddenFields`, `valueHelpFields`, `textFields`, `amountFields`, `quantityFields` (`Entity.Field`). Derive columns, filters and value helps from them; read the source for annotation values (position, importance, qualifier).
- `uiSemantics.searchableEntities`: entities with `@Search.searchable: true`; never send `$search` elsewhere.
- `service.bindings[].serviceDefinition`: the definition a binding names; with several definitions the inspector selects only when all readable bindings agree. Unreadable (`unknown`) bindings leave the choice to you.
- `source.inventoryVerified` and `notes`: only a snapshot that declares `objectCount` can be compared with the inventory; a local export stays `false` (reported as `info`). For a local export `source.complete` and `source.activeSourcesOnly` are written as `true` unconditionally — a declaration, not an observation; the validator ties `source-verified` to these two values and an empty `gaps` list, so for a local export only `gaps` guards the gate.
- Limits: 2 MB per source in every input kind (a gap in a snapshot); 5,000 files for folders and ZIPs; 50 MB total and a compression ratio of 200 for ZIPs; beyond that the package is rejected.

## Converting into UI decisions

| Backend evidence | UI decision |
|---|---|
| Projection entity and expose alias | Entity set, route, page identity |
| `@UI.lineItem`, selection field, facet, field group | List Report / Object Page information architecture |
| Draft behavior | Edit/save/cancel and unsaved-change flow |
| RAP action + feature control | Action placement, enablement, test |
| Validation / message target | Field and message popover, error scenario |
| Association / composition | Navigation, section/table, `$expand` budget |
| Value help / text / currency / unit | Control type, display format, request plan |
| DCL / authorization master | Backend enforcement, no-auth state |
| ETag / lock / side effect | Concurrency, refresh, stale-data scenario |

Bind every row in `design-contract.json.traceability` to the backend object/file and a test ID. An action or field absent from source is never generated in the frontend.

## Readiness gate

Before production code: package/snapshot complete and from active sources? · service definition and binding protocol proven? · real service URI and `$metadata` seen in the target? · exposed entity set and projection/BDEF in the same transaction boundary? · draft, authorization, value help, messages and side effects clear? · UI annotations consistent with the design contract? · target release and released status of used SAP objects verified separately?

Keep what is missing as `gaps` and `blocked`/`assumed`. Even `ready` does not replace real `$metadata`, preview, activation, authorization or released-object evidence.
