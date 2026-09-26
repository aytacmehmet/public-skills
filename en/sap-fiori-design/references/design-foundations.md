# SAP Fiori visual and interaction foundations

Read when deciding visual design, theme, tokens, typography, icons, responsive behavior or accessibility.

Sections: 1 version rule · 2 principles · 3 themes and tokens · 4 color · 5 typography · 6 icons and illustration · 7 responsive · 8 density · 9 accessibility · 10 UX text · 11 visual guardrails

## 1. Version and evidence rule

Prepared against SAP Fiori for Web guideline v1.148 and SAPUI5 Demo Kit 1.151.0; the dated research record is in [official-sources.md](official-sources.md) (27 August 2026). The two versions need not match. Per task: verify the target runtime, then use the versioned guideline and API documentation for that runtime ([Guideline versioning](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/versioning)).

SAP's `sap-fiori-guidelines` AI skill (v1.145, May 2026) is experimental: use it as an index, never as a substitute for the live target-version page ([source](https://github.com/SAP/ai-skills-library/tree/main/skills/sap-fiori-guidelines)).

## 2. Design principles

Check every screen against [SAP Design Principles](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/sap-design-system/vision-and-mission/design-principles):

- **Role-based:** support the role's decision and daily task; show decision data, not all data.
- **Adaptive:** adapt to device, input method and working conditions; do not merely shrink the desktop.
- **Coherent:** keep SAP-wide control, action, message and navigation behavior.
- **Simple:** remove unnecessary fields, actions, decoration and steps; use progressive disclosure.
- **Delightful:** fast, predictable, trust-building feedback; task success over visual show.

Mockup reference: the [SAP Fiori for Web UI Kit](https://www.sap.com/design-system/fiori-design-web/v1-148/resources/libraries/sap-fiori-for-web-ui-kit). Pick the UI Kit/SAPUI5 counterpart of a control instead of redrawing it.

## 3. Themes and design tokens

Default: Horizon. Keep the theme the target system is pinned to. Morning Horizon (light), Evening Horizon (dark), High Contrast Black/White; Quartz Light/Dark only if the target requires it. Morning/Evening target WCAG 2.2 AA, high contrast WCAG 2.2 AAA. Never reproduce theme support with app CSS ([Theming](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/theming)).

Tokens ([Design Tokens](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/design-tokens)):

1. No hard-coded colors, fonts, shadows, radii or control dimensions.
2. Main/base tokens for quick branding; stable semantic component tokens for control implementation.
3. Never bind a reference palette value directly to control CSS.
4. Record the same semantic token name in the design decision and in code.
5. Customer branding through the UI Theme Designer/token chain, not one-off CSS.
6. Verify hover, focus, active, selected, disabled and high-contrast states together.

If custom CSS is unavoidable: exhaust control properties, aggregations, layout data, utility classes and theme parameters first; keep it small, scoped and theme-independent; no private DOM/class selectors (patch releases break them); no inline styles or native HTML/SVG in XML.

## 4. Color and semantics

Morning Horizon reference values: accent `#0070F2`, app background `#F5F6F7`, main text `#131E29`, secondary text `#556B82` — read them from theme parameters, never write them into code ([Morning Horizon Colors](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/colors/morning-horizon)).

| Semantic | Meaning | Use |
|---|---|---|
| Neutral | Needs no interpretation | Regular state |
| Positive | Good, persistent success | Completed, suitable |
| Critical | Attention, non-blocking risk | Approaching deadline, review needed |
| Negative/Error | Error or bad state | Blocking issue, rejected |
| Information | Genuine information | Neutral, needs attention |

No semantic color as decoration; color never carries meaning alone — add text, status or icon. Industry/indication colors only where the domain has an established convention, never mixed with the semantic palette inside one control ([Semantic and Industry-Specific Colors](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/best-practices/ui-elements/how-to-use-semantic-colors)).

Contrast: normal text and text-like icons ≥ 4.5:1; large text, bold text-like icons and meaningful graphics ≥ 3:1; focus indicator and state difference perceivable without color.

## 5. Typography

[Typography – Horizon](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/typography/typography-horizon): font family `72`, fallback order `72full`, Arial, Helvetica, sans-serif · use the control's typographic style, never fake a title with font size · semantic heading hierarchy page → section → subsection · no small text as main content, no light weight on small labels · line height ≈ 1.5 for wrapping content · locale-formatted numbers, dates, times, currency and units.

## 6. Iconography and illustration

[Iconography – Horizon](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/iconography/iconography-horizon): use an existing SAP Horizon icon first. Icons are for functional cues, established metaphors and narrow toolbars; never a replacement for an essential text label, never ornament, never the sole carrier of a complex or culture-specific concept. Sizes: standard 16 px, minimum 12 px, maximum 48 px inside a standard component; SVG default, icon font supported. Icon-only interactions get an accessible name and tooltip; decorative icons are hidden from assistive technology; meaningful icons carry text; check LTR/RTL mirroring and cultural metaphors.

Never render an SAP control or a text-bearing screen with a generative image model. A requested decorative illustration is a separate asset with verified style and alt text; the UI itself is real SAPUI5.

## 7. Responsive and adaptive design

Responsive = the same function reflows as space changes; adaptive = a different presentation when device capability, context or task changes ([Responsiveness and Adaptiveness](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/sap-design-system/vision-and-mission/responsiveness-adaptiveness), [Responsive Spacing](https://www.sap.com/design-system/fiori-design-web/v1-148/page-types/page-layouts/spacing)).

| Class | Width |
|---|---:|
| S | ≤ 599 px |
| M | 600–1023 px |
| L | 1024–1439 px |
| XL | ≥ 1440 px |

Rules: mobile-first information priority · 12-column responsive grid with a fitting layout · no fixed width/height layout · Grid/Analytical/Tree Table are not phone-responsive: design a Responsive Table, card/list or a separate adaptive view · on a phone keep identity and decision fields, pop-in/hide the rest · test overflow with long translations, RTL and browser zoom.

## 8. Content density

[Cozy and Compact](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/cozy-compact): cozy for touch, compact for intensive mouse/keyboard; keep the user/environment choice on hybrid devices; cozy target ≈ 2.75 rem / 44 px; never mix cozy and compact within one page and navigation hierarchy; never shrink fonts to show more data — fix priority and layout instead.

## 9. Accessibility

Framework accessibility is the starting point; the application context must still be verified ([Accessibility in SAP Fiori](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/sap-design-system/product-standards/accessibility-in-sap-fiori), [Keyboard Support](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/interaction/keyboard-support), [UI5 ARIA Labeling](https://ui5.sap.com/#/topic/f38c21c2f71e455e8d4a959522035a1f)).

Every delivery: clear persistent labels, placeholder never the label · logical initial focus, verified tab order and F6 groups · keyboard equivalent and visible focus for every action · heading, landmark, role, state and property relations intact · error messages state location, cause and fix · context-specific alt text · screen reader, keyboard-only, zoom/text resize and high-contrast checks · custom control only as last resort, then you own ARIA, keyboard, theme, zoom, RTL, security, performance and maintenance.

Choose `labelFor`, `aria-label` or `aria-labelledby` by context; never combine them haphazardly.

## 10. UX text and localization

[Accessible UX Writing](https://www.sap.com/design-system/fiori-design-web/v1-145/foundations/writing-and-wording/ux-writing/ux-writing-guidelines/accessibility): action texts short and verb-first (Create, Save, Approve) · never a bare technical error code — state impact and resolution · consistent status terminology · no hard-coded translatable text in controller/XML, everything in i18n · framework formatters/types for plurals, parameters, dates, times, numbers, currency, units · test layout with long German-like text, Turkish characters and RTL.

## 11. Visual quality guardrails

Do not deliver with any of: custom HTML/CSS imitating an SAP control · hard-coded brand/semantic color or font · more than one emphasized primary action per page/dialog · status by color alone · placeholder standing in for a label · desktop table without a mobile alternative · invisible focus or a keyboard trap · a skipped empty/error/loading/no-auth state · PNG fields/actions/states differing from the prototype · a custom control without accessibility and theme tests.
