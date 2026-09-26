# SAP Fiori floorplan and UI pattern decisions

Read when designing information architecture, floorplans, tables/forms/filters/dialogs, action placement, messages and states.

Sections: 1 decision order · 2 floorplan matrix · 3 Dynamic Page and FCL · 4 List Report and Object Page · 5 form, table, Filter Bar · 6 dialog and navigation · 7 action placement · 8 states and messaging · 9 empty, error, loading · 10 stop conditions

## 1. Decision order

1. Derive role, task, data volume, transaction frequency, object lifecycle, devices and runtime.
2. Look for a standard floorplan ([When to Use Which Floorplan](https://www.sap.com/design-system/fiori-design-web/v1-145/page-types/floorplans/when-to-use-which-floorplan)).
3. Standard annotation/OData scenario → Fiori elements.
4. Freestyle only for an unsupported interaction or a genuinely unique layout.
5. Choose controls by data semantics, volume, task and device support, not aesthetics.
6. Write the state and responsive matrix before code.

## 2. Floorplan selection matrix

| Need | Default | Avoid |
|---|---|---|
| Role-based KPIs, tasks, cross-app summaries | Overview Page | Detailed search/processing of one data set |
| Search, filter, sort and act on a large data set | List Report | Chart-table root-cause analysis |
| KPI, visual filter, slice-and-dice, chart/table analysis | Analytical List Page | Merely finding records |
| Predefined work items processed in sequence | Worklist | General record discovery |
| Display/create/edit one object | Object Page | Mass editing or record search |
| Unfamiliar, long process, 3–8 steps | Wizard | Flows under 2 or over 8 steps |
| Jump to one object by known identifier | Initial Page | A search whose result is a list |
| List-detail or list-detail-detail | Flexible Column Layout + fitting floorplans | Dashboards, workbenches, independent pages |

Pages: [List Report](https://www.sap.com/design-system/fiori-design-web/v1-145/page-types/floorplans/list-report-floorplan-sap-fiori-element) · [Analytical List Page](https://experience.sap.com/fiori-design-web/analytical-list-page/) and [Object Page](https://experience.sap.com/fiori-design-web/object-page/) (legacy `experience.sap.com`; verify the current `sap.com/design-system` page for the target version) · [Worklist](https://www.sap.com/design-system/fiori-design-web/v1-120/page-types/floorplans/work-list/usage) · [Initial Page](https://www.sap.com/design-system/fiori-design-web/v1-96/page-types/floorplans/initial-page-floorplan/usage) · [Wizard](https://www.sap.com/design-system/fiori-design-web/v1-108/ui-elements/wizard/usage).

## 3. Dynamic Page and Flexible Column Layout

**Dynamic Page** ([usage](https://www.sap.com/design-system/fiori-design-web/v1-136/page-types/page-layouts/dynamic-page-layout/usage)) = title/header + content + optional finalizing footer. Never rebuild a fitting standard floorplan by hand as a Dynamic Page. Keep the main title and key actions when the header collapses · no expand/collapse/pin without header content · footer only for workflow-finishing actions · Object Page uses the Dynamic Page Header, never the old Object Header · new freestyle pages put the Filter Bar in the header content · never embed a whole floorplan in the content area.

**Flexible Column Layout** ([usage](https://www.sap.com/design-system/fiori-design-web/v1-96/page-types/page-layouts/flexible-column-layout/)): list-detail(-detail) only, at most three columns. Never start with three columns · no empty detail column · each column owns its header, scroll and footer · no second app header/footer wrapping all columns · on S show the last drill-down column full screen and keep the back flow · M limited to two columns, L/XL fitting ratios · dialogs centered over the whole screen, not over one column · never for dashboards, workbenches, side panels or splitting one object.

## 4. List Report and Object Page

**List Report** — find records and act on a data set: Filter Bar in the header content · Basic Search in the Filter Bar, not the table toolbar · Fiori elements default is manual update with `Go`; consider live update only with few filter fields, a cheap query and low traffic, and verify against the target-version Filter Bar page · mandatory filters get a safe default or an explicitly designed empty start · page variant and table variant are one personalization model · sort/group/column settings via P13n, only the needed features enabled · no arbitrary page actions in the footer · KPI and chart-table analysis at the center → Analytical List Page.

**Object Page** ([content area](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/frameworks/sap-fiori-elements/object-page/object-page-content-area-sap-fiori-elements)) — display/create/edit lifecycle of one object: section → subsection → form/table/chart hierarchy · anchor navigation for several sections, tab navigation for long distinct topics, no navigation for a single section · no title repetition in content · breadcrumb only for a real parent-child hierarchy · top-aligned form labels by default · responsive columns S=1, M=2, L=3, XL=6, reduced by content length · a very long table that breaks context becomes a separate List Report or tab.

## 5. Form, table and Filter Bar

**Form** ([Form Layout](https://experience.sap.com/fiori-design-web/explore_group/form-layout-container/), [Form Field Validation](https://experience.sap.com/fiori-design-web/form-field-validation/), both legacy pages — verify the current equivalent): group by task order · repeating records are a table, not a form · short, clear, persistent labels; placeholder never the label · display-only in display mode; read-only for an unchangeable important value in edit, never imitated with disabled · required indicator in edit context · run all validations on Save/Create, not only at the end · error text names field, cause and fix.

**Table/list** ([Table Overview](https://www.sap.com/design-system/fiori-design-web/v1-145/foundations/best-practices/ui-elements/tables/table-overview), [Responsive Table](https://www.sap.com/design-system/fiori-design-web/v1-96/ui-elements/responsive-table/usage)):

| Data/task | Control |
|---|---|
| Independent rows, all devices | Responsive Table |
| Simple items with little detail | List |
| 1000+ rows, cell comparison, intensive desktop | Grid Table + mobile adaptive alternative |
| Real multi-level grouping, subtotals/grand totals | Analytical Table |
| Real hierarchy, limited levels | Tree Table + mobile alternative |

No table for a field/value form, a small selection list or a dashboard visual · on a phone keep the key/identity field, pop-in/hide low-importance columns · horizontal scrolling is not a mobile strategy · separate no-data from no-results and state the next action · server-side paging/filter/sort for large data.

**Filter Bar** ([page](https://www.sap.com/design-system/fiori-design-web/ui-elements/filter-bar/)): standard in List Report and Overview Page, Visual Filter as the ALP alternative · never inside an Object Page section table, a Wizard or a simple List · desktop expanded/collapsed, tablet collapsed by default, phone filter dialog · frequently used, mandatory and most selective filters visible by default · simple domains use select/combo/date controls, no unnecessary value help · re-filtering never silently keeps stale selections.

## 6. Dialog and navigation

**Dialog** ([page](https://experience.sap.com/fiori-design-web/dialog/), legacy — verify the current equivalent): temporary, modal, limited complexity · MessageBox for simple messages, toast for normal success, Object Page for large create/edit · no nested dialogs, no floorplan inside a dialog · full screen on a phone · usually 1–2 actions; primary may be emphasized, Cancel never · Message Popover for validation errors hidden in a long form.

**Navigation** ([Navigation](https://www.sap.com/design-system/fiori-design-web/v1-136/foundations/best-practices/global-patterns/navigation/navigation), [Breadcrumb](https://www.sap.com/design-system/fiori-design-web/ui-elements/breadcrumb/), [Icon Tab Bar](https://www.sap.com/design-system/fiori-design-web/ui-elements/icontabbar/), [Dynamic Side Content](https://www.sap.com/design-system/fiori-design-web/v1-108/ui-elements/dynamic-side-content/usage)): important page state is deep-linkable/bookmarkable · display/edit is not a route state · breadcrumb never replaces back or cross-app navigation · Dynamic Side Content never holds critical content, navigation or list-detail · Icon Tab Bar only for genuinely distinct content views.

## 7. Action placement

[Action Placement](https://www.sap.com/design-system/fiori-design-web/v1-145/foundations/best-practices/global-patterns/action-placement): navigation actions left, business/page actions right · one page-level primary action across header + footer · footer for finalizing actions (Save/Create/Submit) · table/chart toolbar only for local actions on that content · destructive actions get clear text, semantic treatment and, if needed, confirmation · hiding is not securing — backend authorization is mandatory.

## 8. States and messaging

**Element states** ([UI Element States](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/best-practices/ui-elements/ui-element-states)):

| State | Use |
|---|---|
| Enabled | Available, or unavailability cannot be known in advance |
| Disabled | Temporarily unavailable and the way to enable it is clear |
| Hidden | Genuinely absent for this role/state/mode |
| Read-only | Important in edit mode but unchangeable |
| Display-only | Display mode or never edited |
| Error | Blocks finalizing |
| Warning | Non-blocking risk |
| Success | A persistent success that really matters |
| Information | Neutral information that needs attention |

One value state per control at a time. Never express authorization by disabling the selection checkbox.

**Message components** ([Messaging](https://www.sap.com/design-system/fiori-design-web/v1-120/foundations/best-practices/global-patterns/messaging/messaging)):

| Need | Component |
|---|---|
| Non-field issue needing a decision/confirmation | MessageBox |
| Several form/table field messages | MessagePopover |
| Several non-field messages after an action | MessageView |
| Short, non-interrupting success | MessageToast |
| Persistent general/object-level information | MessageStrip |
| Page/component empty or message state | IllustratedMessage / Message Page |
| Field validation | Value State + explanatory text |

No toast for errors/warnings · after navigation the toast appears on the target page · warn before a cancel/back/navigation that loses data.

## 9. Empty, error and loading

Design separately ([Designing for Empty States](https://www.sap.com/design-system/fiori-design-web/v1-96/foundations/best-practices/global-patterns/designing-for-empty-states)): first use / no data yet · no search/filter results · emptied by a user action · system/service error · missing authorization or configuration. Each state has a title, a cause and a next step; no-results is never shown as a system error.

Loading ([Busy Handling](https://www.sap.com/design-system/fiori-design-web/v1-136/foundations/best-practices/ui-elements/busy-handling)): no spinner flash under ≈ 1 s · busy only the affected control/region, never the shell without need · Busy Dialog only for a long operation that really locks all interaction · skeleton/placeholder on initial and app-to-app load, mirroring the real floorplan · Progress Indicator only for measurable progress · on error leave busy and enter the error/retry state.

## 10. Stop/warning conditions

Fix or report an explicit blocker for: old Object Header · Filter Bar inside an Object Page subsection · table used as a form · nested dialog or floorplan inside a dialog · more than one page-level primary action · semantic color as decoration or the only meaning channel · Grid/Analytical/Tree Table without a mobile alternative · hard-coded color/dimension/layout · missing loading/empty/error/no-auth state · a control/API the target runtime does not support · mockup and code diverging in fields/actions/states.
