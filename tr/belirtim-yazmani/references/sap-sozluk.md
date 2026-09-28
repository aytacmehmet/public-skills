# SAP Cloud ERP term glossary

For correct classification and for writing the right information into the right column; it gives no advice. Which option is used is the consultant's decision.

## Extension approaches (1.1 `yaklasim`)

| Term | Meaning | Typical traces in the document |
|---|---|---|
| Key user extensibility | Adaptation without code: custom field, custom logic, form template | Custom field / custom logic in 4.3; software collection in 7.2 |
| Developer extensibility (on-stack, ABAP Cloud) | Development inside the system with ABAP Cloud | DDLS, BDEF, SRVD, SRVB, CLAS in 4.1; language version "ABAP for Cloud Development" |
| Side-by-side (SAP BTP) | An application decoupled from the system, connected through APIs and events | API / event contract in 3.10; inbound-outbound mapping in 3.4 |

## Clean core levels (1.1 `clean_core`)

| Level | Definition |
|---|---|
| A | Released APIs and extension points only |
| B | A + classic APIs (documented, usually upgrade-stable) |
| C | Access to SAP-internal objects; upgrade risk |
| D | Modification, writes to SAP tables, implicit enhancement |

For a level other than A, fill 1.1 `cc_gerekce` and write the risk into 7.3.

## Release contract (1.2 table, 4.1 "Dil versiyonu / release contract")

| Contract | Meaning |
|---|---|
| C0 | Extend: the object can be extended (e.g. CDS view extension) |
| C1 | Use system-internally: usable from ABAP Cloud code |
| C2 | Use as remote API: consumable from outside via OData / SOAP |
| C3 / C4 | Configuration content management / use inside AMDP |

## RAP and service terms (1.2, 3.5, 4.1)

| Term | Note |
|---|---|
| Managed / unmanaged | Whether persistence is done by the framework or by custom code |
| Save sequence | The phase in which persistence happens; the 3.5 "Commit / rollback" column refers to it, `COMMIT WORK` is not written |
| Draft | Unsaved data kept on the server; 1.2 `draft` |
| Determination / validation / action | Behavior definition elements; named in 3.5 steps and 3.3 actions |
| Service definition / binding | SRVD / SRVB; the binding type is 1.2 `binding_tipi` |
| Fiori elements floorplan | List report, worklist, object page, analytical list page, overview page; 3.3 `floorplan` |

## Public Cloud operations terms

| Term | Where it is written |
|---|---|
| Communication scenario → arrangement → system | 3.4 `comm_scenario`, 3.10; the arrangement is set up manually in every system → 3.1 and 7.2 |
| IAM app → business catalog → business role | 5.3 |
| Restriction type / field; Read, Write, Value help access | 5.2, 5.3 |
| Transport request (developer objects), software collection (key user objects) | 7.2 |
| Development (development + customizing tenant), test, production systems | 3.1 "Sistem / tenant", 7.2 "Sistem" |
| Application job (catalog entry, template) | 3.4 `tetikleyici`, 4.1 type Application job |
| Application log (object / subobject) | 7.1 "Hedef" |
| ABAP Test Cockpit (ATC); priority 1–2 findings | 6.3 |

## Values for the 4.1 "SAP tipi" column

As codes: TABL table · DDLS CDS view entity · DDLX metadata extension · DCLS access control · BDEF behavior definition · SRVD service definition · SRVB service binding · CLAS class · INTF interface · DTEL data element · DOMA domain · MSAG message class · SUSO authorization object · ENHO enhancement implementation · DEVC package

By name: BAdI · API · Business event · Fiori app · UI5 app · IAM app · Business catalog · Application job · Communication scenario · Outbound service · Inbound service · Software component · Custom field · Form template · Application log object · Number range · Business role template · Launchpad space / page

Objects that share a name (for example a CDS view entity with its BDEF and DCLS) go into separate rows. A note may be added in parentheses: `CLAS (behavior implementation)`.
