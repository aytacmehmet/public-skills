# SAP Fiori floorplan and UI pattern decisions

Read this reference when designing the information architecture, floorplan, table/form/filter/dialog, action placement, messages and states.

## Contents

1. Decision order
2. Floorplan selection matrix
3. Dynamic Page and Flexible Column Layout
4. List Report and Object Page
5. Form, table and Filter Bar
6. Dialog and navigation
7. Action placement
8. State and messaging
9. Empty, error and loading
10. Stop/warning conditions

## 1. Decision order

1. Derive the role, the task, the data volume, the transaction frequency, the object lifecycle, the devices and the runtime.
2. Look for a standard floorplan.
3. In a standard annotation/OData scenario, choose Fiori elements.
4. Choose freestyle only if there is an unsupported interaction or a genuinely unique layout.
5. Choose the control not by aesthetics but by data semantics, volume, task and device support.
6. Create the state and responsive matrix before the code.

Main source: [When to Use Which Floorplan](https://www.sap.com/design-system/fiori-design-web/v1-145/page-types/floorplans/when-to-use-which-floorplan)

## 2. Floorplan selection matrix

| Need | Default choice | Avoid |
|---|---|---|
| Role-based KPIs, tasks and summaries from different applications | Overview Page | Detailed search/processing on a single data set |
| Search, filter, sort and act on a large data set | List Report | Intensive chart-table root cause analysis |
| KPI, visual filter, slice-and-dice and chart/table analysis | Analytical List Page | Only finding records |
| Processing predefined work items in sequence | Worklist | General record discovery |
| Displaying/creating/editing a single object | Object Page | Mass editing or record search |
| Unfamiliar, long process with 3–8 steps | Wizard | A flow shorter than two steps or longer than eight |
| Going to a single object with a known identifier | Initial Page | A search whose result will be a list |
| List-detail or list-detail-detail | Flexible Column Layout + the appropriate floorplans | Dashboard/workbench/independent pages |

Sources:

- [List Report](https://www.sap.com/design-system/fiori-design-web/v1-145/page-types/floorplans/list-report-floorplan-sap-fiori-element)
- [Analytical List Page](https://experience.sap.com/fiori-design-web/analytical-list-page/) — legacy `experience.sap.com` page; verify the current `sap.com/design-system` equivalent for the target version
- [Object Page](https://experience.sap.com/fiori-design-web/object-page/) — legacy `experience.sap.com` page; verify the current `sap.com/design-system` equivalent for the target version
- [Worklist](https://www.sap.com/design-system/fiori-design-web/v1-120/page-types/floorplans/work-list/usage)
- [Initial Page](https://www.sap.com/design-system/fiori-design-web/v1-96/page-types/floorplans/initial-page-floorplan/usage)
- [Wizard](https://www.sap.com/design-system/fiori-design-web/v1-108/ui-elements/wizard/usage)

## 3. Dynamic Page and Flexible Column Layout

### Dynamic Page

Dynamic Page is the basic page layout consisting of a title/header, content and an optional finalizing footer. If a standard floorplan fits, do not rebuild it by hand as a Dynamic Page.

- When the header collapses, keep the main title and the important actions.
- If there is no header content, do not add expand/collapse/pin.
- Use the footer only for actions that finish the workflow.
- Use the Dynamic Page Header in an Object Page; do not use the old Object Header.
- In a new freestyle page, put the Filter Bar in the Dynamic Page header content.
- Do not embed an entire floorplan in the content area of a Dynamic Page.

Source: [Dynamic Page Layout](https://www.sap.com/design-system/fiori-design-web/v1-136/page-types/page-layouts/dynamic-page-layout/usage)

### Flexible Column Layout

FCL is used only for list-detail or list-detail-detail, with at most three columns.

- Do not start directly with three columns.
- Do not show an empty detail column.
- Give each column its own header, scroll and, if needed, footer behavior.
- Do not produce a second app header/footer that wraps all the columns.
- On an S screen, show the last drill-down column full screen; keep the back flow.
- On an M screen, use a limited two columns; on L/XL, use the appropriate ratios.
- Do not right-align a dialog over a single column; center it over the whole screen.
- Do not use FCL for a dashboard, a workbench, a side panel or to split the same object.

Source: [Flexible Column Layout](https://www.sap.com/design-system/fiori-design-web/v1-96/page-types/page-layouts/flexible-column-layout/)

## 4. List Report and Object Page

### List Report

Use it for finding records and acting on a data set.

- Place the Filter Bar in the header content.
- Put Basic Search in the Filter Bar, not in the table toolbar.
- Use live filtering where possible; use `Go` only when an expensive query/heavy traffic/preparing several filters requires it.
- Give a mandatory filter a safe default value, or explicitly design the empty start.
- Do not make the page variant and the table variant two disconnected personalization models.
- Gather the sort, group and column settings in the P13n approach; enable only the personalization features that are needed.
- Do not use the footer for an arbitrary page action.
- If KPI and chart-table analysis is central, move to the Analytical List Page.

### Object Page

Use it for the display/create/edit lifecycle of a single business object.

- Keep the section → subsection → form/table/chart hierarchy.
- With several sections, use anchor navigation; for long and distinct topics, consider tab navigation.
- With a single section, hide the unnecessary navigation.
- Do not repeat the titles in the content.
- Use a breadcrumb only in a real object parent-child hierarchy.
- Consider top-aligned form labels the default choice.
- Responsive column starting point: S=1, M=2, L=3, XL=6; reduce according to content length.
- If a very long table breaks the context, design a separate List Report or a tab.

Source: [Object Page Content Area](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/frameworks/sap-fiori-elements/object-page/object-page-content-area-sap-fiori-elements)

## 5. Form, table and Filter Bar

### Form

- Group the field/value data according to the task order.
- For repeating records, use a table, not a form.
- Make the label short, clear and persistent; do not make the placeholder the label.
- Use display-only in display mode; use read-only for an important value that cannot be changed in edit. Do not imitate it with disabled.
- Show the required indicator in the edit context.
- Run all validations on Save/Create; do not leave the feedback only to the end.
- In the error text, explain the field, the cause and the solution.

Sources:

- [Form Layout](https://experience.sap.com/fiori-design-web/explore_group/form-layout-container/) — legacy `experience.sap.com` page; verify the current `sap.com/design-system` equivalent for the target version
- [Form Field Validation](https://experience.sap.com/fiori-design-web/form-field-validation/) — legacy `experience.sap.com` page; verify the current `sap.com/design-system` equivalent for the target version

### Table/list selection

| Data/task | Control |
|---|---|
| Independent rows, all devices | Responsive Table |
| Simple item with little detail | List |
| 1000+ rows, cell comparison, intensive desktop use | Grid Table + mobile adaptive alternative |
| Real multi-level grouping, subtotal/grand total | Analytical Table |
| Real hierarchical data, limited levels | Tree Table + mobile alternative |

Rules:

- Do not use a table for a field/value form, a small selection list or a dashboard visualization.
- On a phone, keep the key/identity field; apply pop-in/hide to low-importance content.
- Do not count horizontal scrolling as a mobile strategy.
- Separate the no-data and no-results states; state the next action.
- Use server-side paging/filter/sort for large data.

Sources:

- [Table Overview](https://www.sap.com/design-system/fiori-design-web/v1-145/foundations/best-practices/ui-elements/tables/table-overview)
- [Responsive Table](https://www.sap.com/design-system/fiori-design-web/v1-96/ui-elements/responsive-table/usage)

### Filter Bar

- It is standard in the List Report and the Overview Page; in the ALP there is the Visual Filter alternative.
- Do not put it in an Object Page section table, a Wizard or a simple List.
- Design desktop expanded/collapsed; tablet collapsed by default; phone filter dialog behavior.
- Make the frequently used, mandatory and most volume-reducing filters visible by default.
- For a simple domain, use a select/combo/date control; do not open an unnecessary value help.
- On re-filtering, prevent old selections from being kept by accident.

Source: [Filter Bar](https://www.sap.com/design-system/fiori-design-web/ui-elements/filter-bar/)

## 6. Dialog and navigation

### Dialog

- Use it for a temporary, modal operation of limited complexity.
- Use a MessageBox for a simple message; a toast for a normal success; an Object Page for a large create/edit.
- Do not build nested dialogs.
- Do not put a floorplan inside a dialog.
- On a phone, choose full-screen behavior.
- Generally use 1–2 actions; the primary may be emphasized, Cancel must not be emphasized.
- In a long form, provide a Message Popover for validation errors that are not visible.

Source: [Dialog](https://experience.sap.com/fiori-design-web/dialog/) — legacy `experience.sap.com` page; verify the current `sap.com/design-system` equivalent for the target version

### Navigation

- Make important page state restorable through a deep link/bookmark.
- Do not make the display/edit switch an unnecessary route state.
- Do not use a breadcrumb in place of back or cross-app navigation.
- Do not use Dynamic Side Content in place of critical content, navigation or list-detail.
- Use the Icon Tab Bar only for genuinely distinct content views.

Sources:

- [Navigation](https://www.sap.com/design-system/fiori-design-web/v1-136/foundations/best-practices/global-patterns/navigation/navigation)
- [Breadcrumb](https://www.sap.com/design-system/fiori-design-web/ui-elements/breadcrumb/)
- [Icon Tab Bar](https://www.sap.com/design-system/fiori-design-web/ui-elements/icontabbar/)
- [Dynamic Side Content](https://www.sap.com/design-system/fiori-design-web/v1-108/ui-elements/dynamic-side-content/usage)

## 7. Action placement

- Keep the navigation action on the left; the business/page action on the right.
- Use only one page-level primary action across header + footer in total.
- Use the footer for a finalizing action such as Save/Create/Submit.
- Use the table/chart toolbar only for a local action on that content.
- Give a destructive action clear text, an appropriate semantic treatment and, if needed, a confirmation.
- Do not secure an unauthorized action merely by hiding it; enforce the backend authorization.

Source: [Action Placement](https://www.sap.com/design-system/fiori-design-web/v1-145/foundations/best-practices/global-patterns/action-placement)

## 8. State and messaging

### UI element state

| State | Use |
|---|---|
| Enabled | Available, or why it is unavailable cannot be understood in advance |
| Disabled | Temporarily unavailable and it is clear how to enable it |
| Hidden | Genuinely not available because of the role/state/mode |
| Read-only | Important in edit mode but cannot be changed |
| Display-only | In display mode, or never edited |
| Error | Blocks finalizing |
| Warning | Non-blocking risk |
| Success | A persistent success state really matters |
| Information | Neutral information that genuinely needs attention |

Do not mark a control with more than one value state at the same time. Do not convey authorization by making the selection checkbox disabled.

Source: [UI Element States](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/best-practices/ui-elements/ui-element-states)

### Message component

| Need | Component |
|---|---|
| Non-field issue that requires a decision/confirmation | MessageBox |
| Several form/table field messages | MessagePopover |
| Several non-field messages as the result of an action | MessageView |
| Short, non-interrupting success | MessageToast |
| Persistent general/object-level information | MessageStrip |
| Page/component empty or message state | IllustratedMessage/Message Page |
| Field validation | Value State + explanatory text |

Do not use a toast for an error/warning. After navigation, show the toast on the target page. Give a warning for a cancel/back/navigation that would cause data loss.

Source: [Messaging](https://www.sap.com/design-system/fiori-design-web/v1-120/foundations/best-practices/global-patterns/messaging/messaging)

## 9. Empty, error and loading

Design the following states separately:

- First use / no data yet
- No search/filter results
- Emptied after a user action
- System/service error
- Missing authorization or configuration

In every state, give a title, a cause and a next step. Do not show no-results as if it were a system error.

Source: [Designing for Empty States](https://www.sap.com/design-system/fiori-design-web/v1-96/foundations/best-practices/global-patterns/designing-for-empty-states)

Loading rules:

- Do not produce a spinner flash for an operation shorter than approximately one second.
- Make only the affected control/region busy; do not block the shell unnecessarily.
- Use the Busy Dialog for a long operation in which all interaction will really be locked.
- Use a skeleton/placeholder on the initial app/app-to-app load, representing the real floorplan structure.
- Do not use the Progress Indicator in place of an indeterminate spinner; use it only for measurable progress.
- When an error occurs, close the busy state and move to the error/retry state.

Source: [Busy Handling](https://www.sap.com/design-system/fiori-design-web/v1-136/foundations/best-practices/ui-elements/busy-handling)

## 10. Stop/warning conditions

If any of the following is present, fix it or report an explicit blocker:

- Old Object Header
- Filter Bar inside an Object Page subsection
- A table used for the purpose of a form
- Nested dialog or a floorplan inside a dialog
- More than one page-level primary action
- Semantic color used as decoration/the only channel of meaning
- No mobile alternative for a Grid/Analytical/Tree Table
- Hard-coded color/dimension/layout
- The loading/empty/error/no-auth state missing
- A control/API that the target runtime does not support
- The mockup and the code diverging in terms of fields/actions/states
