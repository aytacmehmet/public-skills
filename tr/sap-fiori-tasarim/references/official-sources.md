# Resmî SAP kaynak indeksi ve güncellik kuralı

Bu referansı hedef sürümü doğrulamak veya belirli bir kontrol/pattern/API hakkında canlı kaynak bulmak için kullan.

## Güncellik akışı

1. Hedef sistem ürününü ve gerçek SAPUI5 runtime sürümünü bul.
2. `manifest.json` içindeki minimum sürümü, sistem runtime'ı sanma.
3. Hedefe uygun versioned SAP Fiori guideline sayfasını aç.
4. Kontrol/API'nin target UI5 API Reference'ta public ve non-deprecated olduğunu doğrula.
5. Fiori elements feature/prerequisite'i hedef sürüm Help/Demo Kit'te doğrula.
6. ABAP object/API release durumunu hedef S/4HANA release/ADT içinde doğrula.
7. Kaynak URL, sayfa sürümü ve kontrol tarihini `design-contract.json` içine yaz.

27 Ağustos 2026 araştırma fotoğrafı:

- SAP Fiori for Web portal sürümü: 1.151; içerik güncellemeleri 1.148'e kadar konsolide edilmiş
- Skill scaffold profili: SAPUI5/types 1.151.0; bunu hedef runtime kanıtı sayma
- SAP'nin deneysel Fiori AI skill'i: v1.145 (Mayıs 2026) tabanlı

Bu değerleri gelecekte sabit gerçek olarak kullanma.

## Ana portallar

- [SAP Design System](https://www.sap.com/design-system)
- [SAP Fiori for Web](https://www.sap.com/design-system/fiori-design-web)
- [SAPUI5 Demo Kit](https://ui5.sap.com/)
- [SAP Help Portal](https://help.sap.com/)
- [SAP'nin Fiori AI skill açıklaması](https://www.sap.com/design-system/fiori-design-web/v1-145/resources/ai-skills/sap-fiori-guidelines)
- [SAP AI Skills Library kaynakları](https://github.com/SAP/ai-skills-library/tree/main/skills/sap-fiori-guidelines)

## Görsel sistem ve erişilebilirlik

- [Design Principles](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/sap-design-system/vision-and-mission/design-principles)
- [Guideline Versioning](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/versioning)
- [Fiori for Web UI Kit](https://www.sap.com/design-system/fiori-design-web/v1-148/resources/libraries/sap-fiori-for-web-ui-kit)
- [Design Tokens](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/design-tokens)
- [Theming](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/theming)
- [Typography Horizon](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/typography/typography-horizon)
- [Iconography Horizon](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/visual/iconography/iconography-horizon)
- [Accessibility in SAP Fiori](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/sap-design-system/product-standards/accessibility-in-sap-fiori)
- [Keyboard Support](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/interaction/keyboard-support)
- [UI5 ARIA Labeling](https://ui5.sap.com/#/topic/f38c21c2f71e455e8d4a959522035a1f)

## Floorplan ve pattern

- [When to Use Which Floorplan](https://www.sap.com/design-system/fiori-design-web/v1-145/page-types/floorplans/when-to-use-which-floorplan)
- [List Report](https://www.sap.com/design-system/fiori-design-web/v1-145/page-types/floorplans/list-report-floorplan-sap-fiori-element)
- [Object Page Content Area](https://www.sap.com/design-system/fiori-design-web/v1-148/discover/frameworks/sap-fiori-elements/object-page/object-page-content-area-sap-fiori-elements)
- [Dynamic Page](https://www.sap.com/design-system/fiori-design-web/v1-136/page-types/page-layouts/dynamic-page-layout/usage)
- [Flexible Column Layout](https://www.sap.com/design-system/fiori-design-web/v1-96/page-types/page-layouts/flexible-column-layout/)
- [Table Overview](https://www.sap.com/design-system/fiori-design-web/v1-145/foundations/best-practices/ui-elements/tables/table-overview)
- [Filter Bar](https://www.sap.com/design-system/fiori-design-web/ui-elements/filter-bar/)
- [UI Element States](https://www.sap.com/design-system/fiori-design-web/v1-148/foundations/best-practices/ui-elements/ui-element-states)
- [Messaging](https://www.sap.com/design-system/fiori-design-web/v1-120/foundations/best-practices/global-patterns/messaging/messaging)
- [Busy Handling](https://www.sap.com/design-system/fiori-design-web/v1-136/foundations/best-practices/ui-elements/busy-handling)

## UI5 mühendislik

- [Best Practices for Developers](https://ui5.sap.com/docs/topics/28fcd55b04654977b63dacbee0552712.html)
- [Performance Checklist](https://ui5.sap.com/docs/topics/9c6400eb7dc145b78e94a81e6e390780.html)
- [TypeScript Support](https://ui5.sap.com/docs/topics/a7ee9617bc794b6fad21e4df38e31128.html)
- [Manifest and Manifest-First](https://ui5.sap.com/docs/topics/be0cf40f61184b358b5faedaec98b2da.html)
- [Asynchronous Loading](https://ui5.sap.com/docs/topics/676b636446c94eada183b1218a824717.html)
- [Stable IDs](https://ui5.sap.com/docs/topics/79e910e6a0d949c7acb051b33170bebc.html)
- [Use Only Public APIs](https://ui5.sap.com/docs/topics/b0d5fe2f1b0b497cbd67cd5a1d35fa4c.html)
- [OData V4 Model](https://ui5.sap.com/docs/topics/5de13cf4dd1f4a3480f7e2eaaee3f5b8.html)
- [Fiori Elements for OData V4](https://ui5.sap.com/docs/topics/13ee8ba1b0264ba08dc15a4aee02c91f.html)
- [Fiori Elements V4 Prerequisites](https://ui5.sap.com/docs/topics/f2344b5e78164b2b9c27ef8b068f295c.html)
- [Testing Overview](https://ui5.sap.com/docs/topics/7cdee404cac441888539ed7bfe076e57.html)
- [UI5 CLI](https://ui5.github.io/cli/stable/)
- [UI5 Linter](https://github.com/UI5/linter)

## RAP, ABAP Cloud ve Clean Core

- [ABAP RAP](https://help.sap.com/docs/abap-cloud/abap-rap)
- [Defining Business Service for Fiori UI](https://help.sap.com/docs/abap-cloud/abap-rap/defining-business-service-for-fiori-ui?version=s4hana_cloud)
- [Back End-Driven UI Features](https://help.sap.com/docs/abap-cloud/abap-rap/back-end-driven-ui-features)
- [Service Binding](https://help.sap.com/docs/abap-cloud/abap-rap/service-binding)
- [Released APIs](https://help.sap.com/docs/ABAP_Cloud/abap-development-tools-user-guide/released-apis)
- [Public Released APIs](https://help.sap.com/docs/abap-cloud/abap-cloud/public-released-apis)
- [Clean Core Extensibility](https://help.sap.com/docs/abap-cloud/developer-guide-from-classic-abap-to-abap-cloud/clean-core-extensibility-and-abap-based-extensions)

## Kaynak kullanma guardrail'i

- Resmî SAP/official UI5 birincil kaynağını tercih et.
- Search sonucu özetini, açılmış kaynak sayfasının yerine kullanma.
- Eski `experience.sap.com` sayfasını yalnız güncel `sap.com/design-system` eşdeğeri yoksa ve sürümü açıkça not ederek kullan.
- Demo/sample'ın çalışması, pattern'in Fiori uyumlu olduğunu tek başına kanıtlamaz.
- Public API dokümanı olmayan module/class/property üretme.
- “Latest” kelimesini tarih ve sürümle mutlaklaştır.
