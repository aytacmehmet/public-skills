# RAP, OData and ABAP Cloud UI contract

Read this reference when the Fiori screen is to be connected to a RAP/OData/ABAP backend or when a design "optimized for ABAP" is requested.

## Table of contents

1. Principle and scope
2. Target system and Clean Core
3. RAP/Fiori elements decisions
4. UI annotation contract
5. Data and performance contract
6. Transaction, draft and side effect
7. Validation, message and authorization
8. Service/versioning safety
9. Acceptance checklist

## 1. Principle and scope

A "Fiori design optimized for ABAP" does not just mean little frontend code. Ensure the following together:

- Match the UI task to the business object boundary.
- Make standard UI behavior backend-driven through metadata/annotations.
- Move filtering, sorting, paging, aggregates and business validation to the server as appropriate.
- Produce a minimal payload and few requests.
- Design draft, action, side effect, message and authorization semantics end to end.
- Do not go beyond released APIs and extension points.

RAP offers a natural contract for the Fiori UI through its CDS-based model, behavior and service exposure.

Source: [ABAP RESTful Application Programming Model](https://help.sap.com/docs/abap-cloud/abap-rap)

## 2. Target system and Clean Core

First distinguish the target:

- SAP S/4HANA Cloud Public Edition
- SAP S/4HANA Cloud Private Edition
- SAP S/4HANA on-premise
- SAP BTP ABAP Environment

For Public Edition developer extensibility:

- Use the ABAP Cloud language version.
- Use only SAP objects/APIs that are released in the target release.
- Use only released/predefined extension points.
- Prefer RAP for a new transactional service.
- Do not guess the name of an internal table, CDS, class, function module or BAPI.
- If no released API can be found, report this as a gap/blocker; do not automatically fall back to an unreleased object.

Release contract summary:

| Contract | Purpose |
|---|---|
| C0 | Extend |
| C1 | Stable use within the system |
| C2 | Remote API |
| C3 | Configuration content |

Verify availability in ADT Released Objects and in the documentation of the target product/release. Being released in another release is not sufficient.

Sources:

- [Released APIs](https://help.sap.com/docs/ABAP_Cloud/abap-development-tools-user-guide/released-apis)
- [Public Released APIs](https://help.sap.com/docs/abap-cloud/abap-cloud/public-released-apis)
- [Developer Extensibility](https://help.sap.com/docs/SAP_S4HANA_CLOUD/6aa39f1ac05441e5a23f484f31e477e7/657285a09f7148d894c27bb8e17827cf.html)
- [Clean Core Extensibility](https://help.sap.com/docs/abap-cloud/developer-guide-from-classic-abap-to-abap-cloud/clean-core-extensibility-and-abap-based-extensions)

## 3. RAP/Fiori elements decisions

For a standard transactional UI:

1. Create the CDS data model and projection.
2. Define the transactional contract with the behavior definition/projection.
3. Expose to the UI only the required projection entities/actions in the service definition.
4. Create an OData V4 UI service binding.
5. Verify annotations and behavior early with the Fiori elements preview.

Sources:

- [Defining Business Service for Fiori UI](https://help.sap.com/docs/abap-cloud/abap-rap/defining-business-service-for-fiori-ui?version=s4hana_cloud)
- [Service Binding](https://help.sap.com/docs/abap-cloud/abap-rap/service-binding)

Treat OData V4 as the future-proof default. If the target system/scope requires V2, design V2 deliberately; do not imitate a V2 service with the V4 model.

For Fiori elements V4, according to the current official documentation:

- Assume one main service for the framework controls.
- Verify that the service supports `$count`, `$skip`, `$top` and the required filter/sort behavior.
- In an edit scenario, verify the draft requirement in the documentation of the target framework.
- Check that a custom page/building block conforms to the same service and transaction boundary.

Source: [Fiori Elements V4 Prerequisites](https://ui5.sap.com/docs/topics/f2344b5e78164b2b9c27ef8b068f295c.html)

## 4. UI annotation contract

Define standard UI behavior through annotations wherever possible:

- `@UI.lineItem`: list/table field and row action
- `@UI.identification`: object identification and object-level action
- `@UI.headerInfo`: title, type name and image/icon semantics
- `@UI.fieldGroup`: form field group
- `@UI.facet`: Object Page section/subsection structure
- `@UI.selectionField`: initial filters
- Value help, text association, currency/unit and semantic object relationships
- Criticality/status semantics

Do not fill in annotations merely for technical convenience. Match them to the information architecture and to `design-contract.json`. Do not repeat the same label/visibility/criticality logic in the frontend.

Consider keeping UI-specific semantics in the projection layer and reusable domain semantics in the interface view. Follow the existing project standard.

Source: [Back End-Driven UI Features](https://help.sap.com/docs/abap-cloud/abap-rap/back-end-driven-ui-features)

## 5. Data and performance contract

Work out a data budget for every page:

- Which fields are mandatory for the first render?
- Which navigations can be loaded only on drill-down?
- Which aggregates/KPIs must be calculated on the server?
- Which filters matter in terms of index/partition and selectivity?
- How many rows are targeted and what is the page size?

Rules:

- Do not expose in the projection any field/association that the UI does not need.
- Support the metadata/navigation design for `$select` and a narrow `$expand`.
- Do not produce N+1 requests; do not design a per-row action/lookup.
- Make server-side paging/filter/sort mandatory for a large entity set.
- Do not pull all data to the client and filter/aggregate there.
- Use expressions/associations suited to CDS/HANA pushdown; do not make calculation in an ABAP loop the default.
- Design value helps to be small and to support search/filter; do not eagerly load the entire domain.
- Model currency/unit and text associations in a way that does not require a separate manual roundtrip.
- Do not let the controller's need for hidden fields conflict with the Fiori elements `autoExpandSelect` behavior; make the controller field an explicit contract.

Sources:

- [OData V4 Performance](https://ui5.sap.com/docs/topics/5a0d286c5606424b8e0d663c87445733.html)
- [Automatic Expand/Select](https://ui5.sap.com/docs/topics/10ca58b701414f7f93cd97156f898f80.html)

## 6. Transaction, draft and side effect

Make the UI edit flow identical to the behavior model:

- Make the managed/unmanaged choice according to the existing business logic and persistence ownership.
- Match the Create/Edit/Save/Cancel state to the draft/non-draft contract.
- Name the backend action after the user's intent; do not use a generic "Process".
- Tie action enablement/feature control to backend state and authorization.
- If a change to one field changes another field, a permission or a message, define a RAP side effect.
- Match the timing of determinations and validations to the UI expectation.
- Design concurrency/ETag and lock behavior explicitly.
- For a long-running action, define an async/job pattern and a progress/refresh strategy; do not keep the HTTP request open unnecessarily long.

Source: [Back End-Driven UI Features](https://help.sap.com/docs/abap-cloud/abap-rap/back-end-driven-ui-features)

## 7. Validation, message and authorization

Validation:

- Use client-side validation for fast UX; enforce the same rule in the backend as mandatory.
- Perform cross-field and business validation in the RAP behavior.
- Associate the message with an entity/field target; give the user the location, the cause and the solution.
- Do not leak technical exception text directly to the UI.
- Let an error prevent finalization; do not let a warning block the decision flow unnecessarily.

Authorization:

- Enforce data access and action authorization in the backend.
- Treat UI visibility/enabled state only as an auxiliary display.
- Reflect an unauthorized field/action through metadata/feature control, but do not remove the backend check.
- Do not unnecessarily expose a sensitive field in the projection/service.
- Do not publish sensitive data in logs, traces and messages.

## 8. Service/versioning safety

- Separate the purpose of a UI service from that of a remote Web API.
- Limit the service definition to the projection that the client needs.
- For a breaking change, plan versioning and backward compatibility.
- Do not arbitrarily change an entity/property/action name once it has been published.
- Test annotations and service metadata in the target UI5/Fiori elements version.
- Do not mistake a local publish/preview result for external system reachability.
- Do not embed destination, authentication and network trust in the code.

Source: [Service Binding](https://help.sap.com/docs/ABAP_Cloud/f055b8bf582d4f34b91da667bc1fcce6/service-binding?version=s4hana_cloud)

## 9. Acceptance checklist

- [ ] Target system/release and ABAP language version verified
- [ ] Release status of the SAP objects/APIs in use verified in the target system
- [ ] Floorplan is consistent with the RAP business object boundary
- [ ] OData V4/V2 decision is justified
- [ ] Projection exposes only the required fields/actions/navigations
- [ ] Annotations match the design contract
- [ ] Support for `$count/$skip/$top`, filter, sort and paging verified
- [ ] Payload is minimal; no N+1 and no client-side full-set processing
- [ ] Draft/non-draft, save/cancel, ETag/lock and side effects designed
- [ ] Validation/message targets are understandable to the user
- [ ] Authorization is enforced in the backend
- [ ] Unit/integration/service preview and UI tests were run
- [ ] No object whose released status was not verified has been reported as "released"
