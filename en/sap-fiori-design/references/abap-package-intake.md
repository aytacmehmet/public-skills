# Deriving the UI contract from an ABAP package

Read this reference when the user asks for a UI5/Fiori screen to be developed from an ABAP package, an ADT project, an abapGit export or a package name.

## Purpose and boundary

Before interpreting the package sources as a screen requirement, produce a machine-readable `abap-backend-contract.json`. This contract connects the package inventory, the RAP/CDS/OData capabilities and the source file of every inference to the UI design.

Reading the source does not, on its own, prove the business purpose of the backend. Do not invent a requirement, role, process, published service URI, target tenant release or runtime authorization that is not found in the package. The parser extracts lexical evidence; it is not ABAP compiler, ADT activation, service preview or runtime authorization evidence.

## Supported inputs

### Local package

For an ADT or abapGit export folder or ZIP:

```powershell
python -B "<skill root>/scripts/inspect_abap_package.py" <package-folder-or-zip> `
  --output <output>/abap-backend-contract.json `
  --package-name Z_MY_PACKAGE `
  --service-uri /sap/opu/odata4/sap/z_ui_service/srvd/sap/z_ui_service/0001/ `
  --protocol odata-v4
```

Provide `--service-uri` only if it has been observed in the target system. Do not guess the URI from the source file.

If the package contains more than one service definition, the inspector does not pick the first one; it leaves the `service.definition` value as `unknown` and writes this into `gaps`. Provide the UI service with `--service-definition <name>`. If the selected service exposes more than one entity and a single root entity cannot be distinguished, provide the main entity set with `--entity-set <name>`. Select both based on source or `$metadata` evidence.

The service binding protocol is read either from a single expression such as `ODATA V4` or from the separate type + version fields in abapGit/ADT exports (`<TYPE>ODATA</TYPE><VERSION>V4</VERSION>`, `type="ODATA" version="V2"`); if neither is present, it stays `unknown`.

### Live ADT package

Only if a preconfigured read-only ADT connection and tools are available (the example steps are based on the `sap-cloud-erp` MCP server; on another host, use the equivalent of the same read operations):

1. Use `load_toolset(profile="source-read")` or a read-only profile that contains the required tools.
2. Read all pages with `list_packages`; if `truncated=true` or `nextOffset` is present, continue.
3. Read the `DDLS`, `DDLX`, `BDEF`, `SRVD`, `SRVB`, `DCLS` and related `CLAS` sources that affect the UI contract from the **active** version with `read_source`, `read_cds_source` or `read_repository_object`.
4. For a paged source, pass the previous `sha256` value as `expectedSha256` on every continuation call. Do not consider the source complete without reading up to the last page.
5. Save the results in the normalized snapshot format below, without credentials/host/client, and hand them to the inspector.

```json
{
  "packageName": "Z_MY_PACKAGE",
  "objectCount": 3,
  "objects": [
    {
      "name": "Z_I_ORDER",
      "type": "DDLS/DF",
      "uri": "/sap/bc/adt/ddic/ddl/sources/z_i_order",
      "version": "active",
      "truncated": false,
      "source": "define root view entity Z_I_Order ..."
    }
  ]
}
```

Then:

```powershell
python -B "<skill root>/scripts/inspect_abap_package.py" <adt-snapshot.json> `
  --output <output>/abap-backend-contract.json `
  --service-uri <observed-uri> --protocol odata-v4
```

If there is no SAP connection, the skill does not ask the user for a password/RSA/private key. It asks for a local export or reports as a blocker that the connection must be configured by the project owner. A package read request does not grant write, activation, publish, transport or deploy authorization.

## Reading priority

If the package is large, first read a thin end-to-end slice:

1. `SRVB` + `SRVD`: protocol, published service and entity set boundary
2. Projection `DDLS` + `DDLX`: fields, associations and annotations exposed to the UI
3. Projection/root `BDEF`: draft, create/update/delete, action, validation and side effect
4. Interface/root `DDLS`: keys, composition/association, currency/unit/text/value help
5. `DCLS` and behavior authorization: backend authorization evidence
6. Only the behavior implementation classes/methods that affect UI behavior

If the package inventory exceeds 200 items, state the paging and comprehensive reading plan in the contract. Do not silently skip an object that does not look relevant by its name; record per type why it is out of scope.

## Reading the inspector output

- `model.entities[].fields/keys`: fields read from the element list. `exposedAssociations` are not fields; they are navigation candidates.
- `model.entities[].unparsedElements`: elements that the lexical reader could not classify (for example a `case` expression without an alias). Each one produces a `gap` and blocks the `ready` result; verify the field against `$metadata` and bind it to the contract manually.
- `behavior.definitions[]`: a separate record for each `define behavior for`. It also recognizes the parenthesized notation of `create/update/delete` (`update ( features : instance );`); `createByAssociation` keeps sub-object creation separate.
- `behavior.actions` are business actions only; `draftActions` (Edit, Activate, Discard, Resume, Prepare) belong to the framework and are not designed as buttons.
- `dynamicFeatureControl`: operations and actions whose enablement is determined at runtime. Plan the disabled/hidden state and its test for these.
- `etag` and `totalEtag` are separate fields; write the concurrency scenario according to both.

## Converting into a UI decision

From `abap-backend-contract.json`, establish at least the following mapping:

| Backend evidence | UI decision |
|---|---|
| Projection entity and expose alias | Entity set, route and page identity |
| `@UI.lineItem`, selection field, facet, field group | List Report/Object Page information architecture |
| Draft behavior | Edit/save/cancel and unsaved-change flow |
| RAP action + feature control | Action placement, enablement and test |
| Validation/message target | Field/message popover and error scenario |
| Association/composition | Navigation, section/table and `$expand` budget |
| Value help/text/currency/unit | Control type, display format and request plan |
| DCL/authorization master | Backend enforcement and no-auth state |
| ETag/lock/side effect | Concurrency, refresh and stale-data scenario |

Bind every row in `design-contract.json.traceability` with the backend object/file and the test ID. If an action or field is not in the source, do not generate it in the frontend as if it existed.

## Readiness gate

Before moving on to production code:

- Is the package/snapshot complete and from active sources?
- Have the service definition and the binding protocol been proven?
- Have the real service URI and `$metadata` been seen in the target system?
- Are the exposed entity set and the projection/BDEF within the same transaction boundary?
- Is the draft, authorization, value help, message and side effect status clear?
- Are the UI annotations consistent with the design contract?
- Have the target release and the release status of the SAP objects used been verified separately?

Keep whatever is missing as `gaps` and `blocked/assumed`. Even the inspector's `ready` result does not replace real `$metadata`, preview, activation, authorization or released-object evidence.
