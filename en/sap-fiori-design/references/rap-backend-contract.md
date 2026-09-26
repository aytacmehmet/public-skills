# RAP, OData and ABAP Cloud UI contract

Read when the screen connects to a RAP/OData/ABAP backend or an "ABAP-optimized" design is requested.

Sections: 1 principle · 2 target and Clean Core · 3 RAP/Fiori elements decisions · 4 annotations · 5 data and performance · 6 transaction, draft, side effects · 7 validation, messages, authorization · 8 service/versioning · 9 acceptance checklist

## 1. Principle and scope

"ABAP-optimized" means more than little frontend code: match the UI task to the business-object boundary · make standard UI behavior backend-driven via metadata/annotations · push filtering, sorting, paging, aggregation and business validation to the server · minimal payload, few requests · draft, action, side-effect, message and authorization semantics designed end to end · only released APIs and extension points. RAP's CDS model, behavior and service exposure are the natural Fiori contract ([ABAP RAP](https://help.sap.com/docs/abap-cloud/abap-rap)).

## 2. Target system and Clean Core

Distinguish S/4HANA Cloud Public Edition, Private Edition, on-premise and BTP ABAP Environment.

Public Edition developer extensibility: ABAP Cloud language version · only SAP objects/APIs released in the target release · only released/predefined extension points · RAP for new transactional services · never guess table, CDS, class, function module or BAPI names · no released API found → gap/blocker, never a silent fallback to an unreleased object.

Release contracts: C0 extend · C1 stable use inside the system · C2 remote API · C3 configuration content. Verify in ADT Released Objects and the target product/release documentation; released elsewhere is not enough ([Released APIs](https://help.sap.com/docs/ABAP_Cloud/abap-development-tools-user-guide/released-apis), [Public Released APIs](https://help.sap.com/docs/abap-cloud/abap-cloud/public-released-apis), [Developer Extensibility](https://help.sap.com/docs/SAP_S4HANA_CLOUD/6aa39f1ac05441e5a23f484f31e477e7/657285a09f7148d894c27bb8e17827cf.html), [Clean Core Extensibility](https://help.sap.com/docs/abap-cloud/developer-guide-from-classic-abap-to-abap-cloud/clean-core-extensibility-and-abap-based-extensions)).

## 3. RAP / Fiori elements decisions

Standard transactional UI ([Defining Business Service for Fiori UI](https://help.sap.com/docs/abap-cloud/abap-rap/defining-business-service-for-fiori-ui?version=s4hana_cloud), [Service Binding](https://help.sap.com/docs/abap-cloud/abap-rap/service-binding)): 1 CDS data model and projection · 2 behavior definition/projection as the transactional contract · 3 service definition exposing only the needed projection entities/actions · 4 OData V4 UI service binding · 5 early annotation/behavior check in the Fiori elements preview.

OData V4 is the future-proof default; design V2 deliberately only when the target requires it, never V2 imitated with the V4 model. Fiori elements V4 ([prerequisites](https://ui5.sap.com/docs/topics/f2344b5e78164b2b9c27ef8b068f295c.html)): one main service for the framework controls · `$count`, `$skip`, `$top` and the needed filter/sort supported · draft requirement for edit verified in the target framework docs · custom pages/building blocks inside the same service and transaction boundary.

## 4. UI annotation contract

Prefer annotations ([Back End-Driven UI Features](https://help.sap.com/docs/abap-cloud/abap-rap/back-end-driven-ui-features)): `@UI.lineItem` table fields and row actions · `@UI.identification` object identity and object-level actions · `@UI.headerInfo` title, type name, image/icon · `@UI.fieldGroup` form groups · `@UI.facet` Object Page sections/subsections · `@UI.selectionField` initial filters · value help, text, currency/unit and semantic-object relations · criticality/status.

Annotations follow the information architecture and `design-contract.json`, not technical convenience; label/visibility/criticality logic is never duplicated in the frontend. UI-specific semantics in the projection, reusable domain semantics in the interface view, unless the project standard differs.

## 5. Data and performance contract

Per page budget: fields mandatory for first render · navigations loaded only on drill-down · aggregates/KPIs computed server-side · filters that matter for index/partition/selectivity · target row count and page size ([OData V4 Performance](https://ui5.sap.com/docs/topics/5a0d286c5606424b8e0d663c87445733.html), [Automatic Expand/Select](https://ui5.sap.com/docs/topics/10ca58b701414f7f93cd97156f898f80.html)).

Rules: expose nothing the UI does not need · support `$select` and a narrow `$expand` in the metadata/navigation design · no N+1 requests, no per-row action/lookup · server-side paging/filter/sort mandatory for large sets · never pull everything to the client · CDS/HANA push-down expressions, no ABAP-loop calculation by default · small, searchable value helps, no eager domain loading · currency/unit and text associations without extra manual roundtrips · controller field needs made explicit instead of colliding with `autoExpandSelect`.

## 6. Transaction, draft and side effects

The UI edit flow mirrors the behavior model: managed/unmanaged by existing logic and persistence ownership · Create/Edit/Save/Cancel matched to the draft/non-draft contract · actions named after user intent, never a generic "Process" · enablement/feature control tied to backend state and authorization · RAP side effects wherever a field change alters another field, permission or message · determination/validation timing matched to UI expectation · concurrency/ETag and locks designed explicitly · long-running actions use async/job patterns with progress/refresh, never an open HTTP request.

## 7. Validation, messages and authorization

Validation: client-side for fast UX, the same rule enforced in the backend · cross-field and business validation in RAP behavior · messages targeted at entity/field with location, cause and fix · no leaked technical exception text · errors block finalizing, warnings do not block the decision flow unnecessarily.

Authorization: data access and actions enforced in the backend · UI visibility/enabled state is auxiliary only · unauthorized fields/actions reflected via metadata/feature control without removing the backend check · no unnecessary sensitive fields in projection/service · no sensitive data in logs, traces, messages.

## 8. Service and versioning safety

UI service and remote Web API have different purposes · service definition limited to the client's projection · breaking changes get versioning and backward compatibility · published entity/property/action names never renamed casually · annotations and metadata tested in the target UI5/Fiori elements version · a local publish/preview does not prove external reachability · no destination, authentication or network trust in code ([Service Binding](https://help.sap.com/docs/ABAP_Cloud/f055b8bf582d4f34b91da667bc1fcce6/service-binding?version=s4hana_cloud)).

## 9. Acceptance checklist

- [ ] Target system/release and ABAP language version verified
- [ ] Release status of every SAP object/API verified in the target system
- [ ] Floorplan consistent with the RAP business-object boundary
- [ ] OData V4/V2 decision justified
- [ ] Projection exposes only required fields/actions/navigations
- [ ] Annotations match the design contract
- [ ] `$count/$skip/$top`, filter, sort and paging support verified
- [ ] Payload minimal; no N+1, no client-side full-set processing
- [ ] Draft/non-draft, save/cancel, ETag/lock and side effects designed
- [ ] Validation/message targets understandable to the user
- [ ] Authorization enforced in the backend
- [ ] Unit/integration/service preview and UI tests run
- [ ] Nothing reported as "released" without verification
