# SAP Fiori visual and interaction foundations

Read this reference when making a visual design, theme, token, typography, icon, responsive behavior or accessibility decision.

## Contents

1. Version and evidence rule
2. Design principles
3. Theme and design tokens
4. Color and semantics
5. Typography
6. Iconography and illustration
7. Responsive and adaptive design
8. Content density
9. Accessibility
10. UX text and localization
11. Visual quality guardrails

## 1. Version and evidence rule

This summary was prepared on 12 August 2026 by observing SAP Fiori for Web guideline v1.148 and SAPUI5 Demo Kit 1.151.0. These two versions do not have to be the same. For every job, verify the target runtime, then use the versioned Fiori guideline and UI5 API documentation that match that runtime.

- [Guideline versioning](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/versioning)
- [SAP Fiori for Web](https://www.sap.com/design-system/fiori-design-web)
- [SAPUI5 Demo Kit](https://ui5.sap.com/)

SAP's official `sap-fiori-guidelines` AI skill is based on v1.145 (May 2026) and is marked as experimental. Treat it as a useful index; do not substitute it for the live documentation of the target version.

- [SAP AI Skill for Fiori Guidelines](https://www.sap.com/design-system/fiori-design-web/v1-145/resources/ai-skills/sap-fiori-guidelines)
- [SAP AI Skills Library source](https://github.com/SAP/ai-skills-library/tree/main/skills/sap-fiori-guidelines)

## 2. Design principles

Evaluate every screen against these five principles:

- **Role-based:** Support the decision and the daily task of the specific role; instead of showing all the data, bring forward the data needed for the decision.
- **Adaptive:** Adapt to the device, input method and working conditions; do not merely shrink the desktop.
- **Coherent:** Preserve the control, action, message and navigation behavior used across SAP.
- **Simple:** Remove unnecessary fields, actions, decoration and steps; use progressive disclosure.
- **Delightful:** Produce fast, predictable and trust-building feedback; do not put visual showiness ahead of task success.

Source: [SAP Design Principles](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/sap-design-system/vision-and-mission/design-principles)

Use the SAP Fiori for Web UI Kit as the canonical mockup reference. Instead of freely redrawing a control, pick its UI Kit/SAPUI5 counterpart.

Source: [SAP Fiori for Web UI Kit](https://www.sap.com/design-system/fiori-design-web/v1-148/resources/libraries/sap-fiori-for-web-ui-kit)

## 3. Theme and design tokens

The default modern visual language is Horizon. If the target system is pinned to a different theme, keep that theme.

- Morning Horizon: light theme
- Evening Horizon: dark theme
- High Contrast Black / High Contrast White: high contrast
- Quartz Light / Quartz Dark: if the target system requires it

Morning/Evening Horizon target WCAG 2.2 AA; the Horizon high-contrast themes target WCAG 2.2 AAA. Do not reproduce theme support with application CSS.

Source: [Theming](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/theming)

Token rules:

1. Do not write hard-coded colors, fonts, shadows, radii or control dimensions.
2. Use the appropriate main/base token for quick branding; use a stable semantic component token for control implementation.
3. Do not bind a reference palette value directly to control CSS.
4. Record the same semantic token name in the Figma/prototype decision and in the code decision.
5. Solve customer branding through the UI Theme Designer/token chain, not through one-off CSS patches.
6. Verify the hover, focus, active, selected, disabled and high-contrast states together.

Source: [Design Tokens](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/design-tokens)

If custom CSS is really needed:

- First look for a standard control property, aggregation, layout data, utility class and theme parameter.
- Keep the CSS small, scoped and free of theme dependencies.
- Do not use private DOM/class selectors; they can break with a patch release.
- Do not use inline styles or native HTML/SVG inside XML.

## 4. Color and semantics

In the Morning Horizon visual reference, the accent blue is `#0070F2`, the application background is `#F5F6F7`, the main text is `#131E29` and the secondary text is `#556B82`. Do not write these values directly into code; get them from the theme parameter.

Source: [Morning Horizon Colors](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/colors/morning-horizon)

Semantic mapping:

| Semantic | Meaning | Appropriate use |
|---|---|---|
| Neutral | Normal/needs no interpretation | Regular state |
| Positive | Good/successful persistent state | Completed, suitable |
| Critical | Attention, non-blocking risk | Approaching deadline, review required |
| Negative/Error | Error or bad state | Blocking issue, rejected |
| Information | Genuine information | Neutral information that needs attention |

Do not use semantic color for decoration. Color must not carry meaning on its own; support it with text, status and/or an icon. Use an industry/indication color only if the domain has an established color convention, and do not mix it with the semantic palette inside the same control.

Source: [Using Semantic and Industry-Specific Colors](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/best-practices/ui-elements/how-to-use-semantic-colors)

Contrast targets:

- Normal text and text-like icons: at least 4.5:1
- Large text, bold text-like icons and meaningful graphics: at least 3:1
- Focus indicator and state difference: perceivable independently of color

## 5. Typography

- Use the `72` family; if it cannot be loaded, keep the fallback order `72full`, Arial, Helvetica, sans-serif.
- Use the control's ready-made typographic style; do not imitate a title with font size alone.
- Keep the semantic heading hierarchy at the page → section → subsection level.
- Do not make small text the main content; do not use a light weight on small labels.
- Use a line height of approximately 1.5 for long/wrapping content.
- Format numbers, dates, times, currency and units according to the user's locale.

Source: [Typography – Horizon](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/typography/typography-horizon)

## 6. Iconography and illustration

First look for an existing SAP Horizon icon. For an icon:

- Use it for a functional cue, an established metaphor or a narrow toolbar area.
- Do not use it in place of an essential text label.
- Do not add it to create ornament and clutter.
- Do not force it to carry a complex or culture-specific concept on its own.

Size guide:

- Standard: 16 px
- Absolute recommended lower limit: 12 px
- Upper limit inside a standard component: 48 px
- SVG is the default; icon font is supported

Accessibility:

- Give an icon-only interaction an accessible name and a tooltip.
- Hide a decorative icon from assistive technology.
- Support a meaningful icon with text/a label.
- Check LTR/RTL direction changes and cultural metaphors.

Source: [Iconography – Horizon](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/iconography/iconography-horizon)

Do not use a generative image model to draw an SAP control or a UI screen containing text. If a decorative illustration is needed, produce a separate asset, verify the illustration style and the accessible alternative text; render UI elements with real SAPUI5.

## 7. Responsive and adaptive design

Responsive: Reflowing the same functionality and information as the space changes. Adaptive: Providing a different presentation/interaction when the device capability, the context or the task purpose changes.

Breakpoints:

| Class | Width |
|---|---:|
| S | ≤ 599 px |
| M | 600–1023 px |
| L | 1024–1439 px |
| XL | ≥ 1440 px |

Sources:

- [Responsiveness and Adaptiveness](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/sap-design-system/vision-and-mission/responsiveness-adaptiveness)
- [Responsive Spacing](https://www.sap.com/design-system/fiori-design-web/v1-148/page-types/page-layouts/spacing)

Rules:

- Set the information priority mobile-first.
- Use the 12-column responsive grid with an appropriate layout.
- Do not build the layout with fixed width/height.
- Accept that Grid/Analytical/Tree Table is not fully responsive on a phone; design a Responsive Table, a card/list or a separate adaptive view.
- On a phone, keep the identity and decision fields; reduce low-importance content with pop-in/hide.
- Test for overflow with long translations, RTL and browser zoom.

## 8. Content density

- Choose cozy for touch, compact for intensive mouse/keyboard use.
- On a hybrid device, keep the user/environment choice.
- The cozy target area is approximately 2.75 rem / 44 px.
- Do not mix cozy and compact within the same page and navigation hierarchy.
- Do not shrink the font to show more data; fix the information priority and the layout choice.

Source: [Cozy and Compact](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/cozy-compact)

## 9. Accessibility

Framework accessibility is the starting point; the application context must still be verified.

In every delivery:

- Use clear and persistent labels; do not make the placeholder the label.
- Place the initial focus somewhere logical; verify the tab order and the F6 groups.
- Give all actions a keyboard equivalent and a visible focus.
- Preserve the heading, landmark, role, state and property relationships.
- In an error message, explain the location, the cause and the way to fix it.
- Produce the alternative text of an image/icon according to the context.
- Check screen reader, keyboard-only, zoom/text resize and high-contrast.
- Make a custom control the last resort; if you choose one, take on the responsibility for ARIA, keyboard, theme, zoom, RTL, security, performance and maintenance.

Sources:

- [Accessibility in SAP Fiori](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/sap-design-system/product-standards/accessibility-in-sap-fiori)
- [Keyboard Support](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/interaction/keyboard-support)
- [UI5 ARIA Labeling](https://ui5.sap.com/#/topic/f38c21c2f71e455e8d4a959522035a1f)

Do not mix up the UI5 ARIA priorities: choose among the `labelFor`, `aria-label` and `aria-labelledby` options according to the context; do not combine them with one another haphazardly.

## 10. UX text and localization

- Keep the action text short and start it with a verb: such as Create, Save, Approve.
- Do not show a technical error code on its own; explain the impact on the user and the way to resolve it.
- Use status text with consistent terminology.
- Do not hard-code translatable text in the controller/XML; move it to i18n.
- Use the framework formatter/type for plurals, parameters, dates, times, numbers, currency and units.
- Test the layout with long German-like text, Turkish characters and RTL.

Source: [Accessible UX Writing](https://www.sap.com/design-system/fiori-design-web/v1-145/foundations/writing-and-wording/ux-writing/ux-writing-guidelines/accessibility)

## 11. Visual quality guardrails

If any of the following is present, do not deliver the design without fixing it:

- Custom HTML/CSS that imitates an SAP control
- Hard-coded brand/semantic color or font
- More than one emphasized primary action within the same page/dialog
- Status conveyed by color alone
- A placeholder standing in for the label
- No mobile alternative for a desktop table
- Focus not visible, or a keyboard trap
- The empty/error/loading/no-auth state skipped
- The PNG showing fields/actions/states that differ from the interactive prototype
- No accessibility and theme testing for a custom control
