# SAPUI5 ve Fiori elements mühendislik rehberi

Bu referansı proje mimarisi, kaynak kod, model/binding, performans, güvenlik ve test kararı verirken oku.

## İçindekiler

1. Sürüm ve mimari kararı
2. Projeyi kanıt üzerinden okuma
3. Fiori elements / freestyle karar ağacı
4. Manifest-first ve proje yapısı
5. TypeScript, modüller ve public API
6. XML view, fragment ve controller
7. Model, OData ve routing
8. i18n, theming ve accessibility
9. Performans ve güvenlik
10. Test ve build kalite kapıları
11. Kod üretim guardrail'leri

## 1. Sürüm ve mimari kararı

Skill içindeki `version-profiles.json` yalnız gözden geçirilmiş scaffold bağımlılık setidir; hedef sistem runtime kanıtı değildir. Önce gerçek sistem sürümünü ve `minUI5Version` değerini ayrı ayrı bul; API Reference ile kullanılabilirliği doğrula.

Kaynak: [SAPUI5 Demo Kit](https://ui5.sap.com/)

Ana ilke: mümkün olduğunca SAP Fiori elements, gerektiği kadar freestyle SAPUI5.

- Yeni standart iş uygulaması: Fiori elements for OData V4.
- Standart yapı + küçük özel ihtiyaç: resmi extension point/building block.
- Standart yapı + özgün sayfa: Fiori elements custom page/flexible programming model.
- Benzersiz etkileşim, standart dışı protokol veya tam özel UI/performance ihtiyacı: freestyle SAPUI5.
- Mevcut OData V2 app: mevcut modeli koru veya planlı V4 migration yap; V2 servisini V4 modelle sarmalama yaklaşımını kullanma (deprecated).

Kaynaklar:

- [Modern Development](https://ui5.sap.com/docs/topics/4cb54eb25b7e4df794c05268e83c22b4.html)
- [Developing Apps with SAP Fiori Elements](https://ui5.sap.com/docs/topics/03265b0408e2432c9571d6b3feb6b1fd.html)
- [Fiori Elements for OData V4](https://ui5.sap.com/docs/topics/13ee8ba1b0264ba08dc15a4aee02c91f.html)

## 2. Projeyi kanıt üzerinden okuma

Kod yazmadan şunları aç:

- `package.json`, lockfile ve script'ler
- `ui5.yaml` ve tooling sürümü
- `webapp/manifest.json`, `Component.*`, `index.html`
- View, fragment, controller, model, formatter ve custom control'ler
- Annotation XML/CDS metadata extension ve servis `$metadata`
- Test klasörleri ve CI ayarları
- ESLint/UI5 Linter/TypeScript config
- Hedef deploy/FLP ayarı ve approuter/destination bilgisi

Şunları belirle:

- UI5 runtime/minimum sürüm
- Fiori elements V2/V4 veya freestyle
- OData V2/V4, draft, transactional/read-only
- TypeScript/JavaScript ve module formatı
- Mevcut stable ID, i18n, routing ve test stili
- Kullanılan extension point'in public/stable olup olmadığı

Hedef runtime doğrulanamadıysa üretim kodunu güvenli ortak özellik setiyle sınırla ve bunu açık varsayım yap.

## 3. Fiori elements / freestyle karar ağacı

### Fiori elements OData V4 seç

- List Report, Object Page, Analytical List Page veya desteklenen standard pattern uyuyorsa
- Metadata/annotation ile field, value help, action, draft ve navigation tanımlanabiliyorsa
- RAP/OData V4 UI service mevcut veya tasarlanabiliyorsa
- Upgrade dayanıklılığı ve frontend kod azaltımı önemliyse

Standart floorplan, building block etkileşimlerini framework düzeyinde optimize eder ve Design System uyumunu otomatik taşır.

### Fiori elements custom page/building block seç

- Standard floorplan çoğu ihtiyacı karşılıyor ancak sınırlı özgün yerleşim gerekiyorsa
- Framework message, edit flow, draft ve metadata avantajını korumak istiyorsan
- Resmî Flexible Programming Model building block'u ihtiyacı kapsıyorsa

### Freestyle seç

- Standard floorplan/building block karşılamayan benzersiz etkileşim varsa
- OData dışı/çoklu veri kaynağı ve özel orkestrasyon gerekiyorsa
- Özel görselleştirme veya cihaz kabiliyeti uygulamanın merkezindeyse

Kararı `design-contract.json` içinde gerekçelendir. “Daha özgür” veya “daha güzel” tek başına freestyle gerekçesi değildir.

## 4. Manifest-first ve proje yapısı

Freestyle varsayılan yapı:

```text
project/
├─ package.json
├─ ui5.yaml
├─ tsconfig.json                  # TypeScript ise
└─ webapp/
   ├─ manifest.json
   ├─ Component.ts|js
   ├─ view/
   ├─ controller/
   ├─ model/
   ├─ i18n/
   ├─ css/                        # Yalnız gerekirse
   └─ test/{unit,integration,e2e}/
```

Kaynaklar:

- [Basic App Files](https://ui5.sap.com/docs/topics/28b59ca857044a7890a22aec8cf1fee9.html)
- [Folder Structure](https://ui5.sap.com/docs/topics/003f755d46d34dd1bbce9ffe08c8d46a.html)

Manifest kuralları:

- App ID, min UI5, libraries, models, dataSources, root view, routing ve density'yi `manifest.json` içinde tut.
- Yeni proje hedefi UI5 1.136+ ise Manifest Version 2 kullan; daha eski runtime'a Manifest V2 üretme.
- Manifest V1'de root view ve target'ları async yapılandır. Manifest V2'de kaldırılmış `async` alanlarını yazma; asenkron davranış varsayılandır.
- Standalone başlangıçta `sap/ui/core/ComponentSupport`; FLP içinde launchpad lifecycle kullan.
- Libraries'i `sap.ui5/dependencies/libs`, model'i `sap.ui5/models`, servisleri `sap.app/dataSources` altında tanımla.
- Deprecated `sap.ui5/resources/js`, sync component oluşturma ve doğrudan component constructor kullanma.
- `Component.ts|js` içinde `UIComponent` kullan; uygun sürümde `sap.ui.core.IAsyncContentCreation` uygula.

Kaynaklar:

- [Manifest and Manifest-First](https://ui5.sap.com/docs/topics/be0cf40f61184b358b5faedaec98b2da.html)
- [Asynchronous Loading](https://ui5.sap.com/docs/topics/676b636446c94eada183b1218a824717.html)
- [Model Preload](https://ui5.sap.com/docs/topics/26ba6a5c1e5c417f8b21cce1411dba2c.html)

## 5. TypeScript, modüller ve public API

Yeni freestyle projede TypeScript'i tercih et. Mevcut JavaScript projeyi gereksiz toplu migration'a zorlama.

- Resmî SAPUI5 için `@sapui5/types` kullan.
- Runtime, types, UI5 CLI ve plugin sürümlerini hedef sürümle uyumlu pinle.
- Typecheck'i CI kalite kapısı yap.
- Yalnız API Reference'ta public belgelenen API'yi kullan.
- Deprecated, experimental, protected/private API ve private DOM/class kullanma.
- Eager dependency için `sap.ui.define`; lazy kullanım için `sap.ui.require` kullan.
- UI5 sınıflarına `sap.m.Button` gibi global adlarla erişme; modül import'u kullan. Belgelenmiş `sap.ui.define`/`sap.ui.require` loader API'lerini bu yasakla karıştırma. `sap.ui.getCore()` veya global controller çözümlemesi üretme.
- jQuery API yerine UI5 veya native browser API kullan.

Kaynaklar:

- [TypeScript Support](https://ui5.sap.com/docs/topics/a7ee9617bc794b6fad21e4df38e31128.html)
- [TypeScript FAQ](https://ui5.sap.com/docs/topics/8439949bbdc34141bd2b9194f91d42c2.html)
- [Use Only Public APIs](https://ui5.sap.com/docs/topics/b0d5fe2f1b0b497cbd67cd5a1d35fa4c.html)
- [Best Practices for Developers](https://ui5.sap.com/docs/topics/28fcd55b04654977b63dacbee0552712.html)

## 6. XML view, fragment ve controller

- View/fragment için XML'i varsayılan seç.
- HTMLView, JSView ve JSONView üretme; deprecated.
- View'u kısa ve semantik tut; tekrar eden/popup parçayı fragment yap.
- Fragment'i `Controller.loadFragment` ile async yükle.
- View-controller adını eşle; controller yapısını view yapısına paralel tut.
- XML handler'ını `.onPress` biçiminde controller instance'a bağla.
- XML'de gerekli module'ü `core:require` veya templating'de `template:require` ile al.
- `sap.ui.getCore().byId()` veya `Element.getElementById()` yerine `this.byId()`/view scoped lookup kullan.
- Kullanıcı ve test için önemli kontrole stabil, semantik ID ver.
- İş mantığını controller'a yığma; formatter/helper/service module'e ayır.
- Direct DOM manipulation, inline HTML/SVG/CSS ve global event handler kullanma.

Kaynaklar:

- [MVC](https://ui5.sap.com/docs/topics/07afcf400eb344c2916e4eb3a400ff7b.html)
- [Short and Simple Views](https://ui5.sap.com/docs/topics/b0d7db7930f64b9399dc2b4979293873.html)
- [Stable IDs](https://ui5.sap.com/docs/topics/79e910e6a0d949c7acb051b33170bebc.html)

## 7. Model, OData ve routing

Model seçimi:

- Remote business data: gerçek servis sürümüne uygun ODataModel
- Yerel UI state: named JSONModel
- Çevrilebilir metin: named ResourceModel/i18n

Backend verisini gereksiz yere JSONModel'a kopyalama. UI5 data type/binding validation ve formatting kullan. Programatik model ve event handler yaşam döngüsünü temizle.

### OData V4

- Binding tabanlı erişim (`bindContext`, `bindList`, `bindProperty`) kullan.
- Promise döndüren `request*` API'leri kullan.
- Context'i CRUD/bound operation merkezinde tut.
- `autoExpandSelect: true` değerlendirilir; controller'ın ayrıca okuyacağı alanı açık `$select` et.
- Server-side filter/sort/paging kullan; bütün entity set'i client'a çekme.
- Dar `$select`, kontrollü `$expand`, growing/paging ve batch group kullan.
- Transactional akışta ayrı `updateGroupId`, `submitBatch`, `resetChanges`, `hasPendingChanges` planla.
- CSRF işini OData modeline bırak; özel token yönetimini gerekçesiz yazma.
- Metadata kritik başlangıç yolundaysa preload/early request'i hedef sürümde değerlendir.

Kaynaklar:

- [OData V4 Model](https://ui5.sap.com/docs/topics/5de13cf4dd1f4a3480f7e2eaaee3f5b8.html)
- [Data Access](https://ui5.sap.com/docs/topics/9613f1f2d88747cab21896f7216afdac.html)
- [Automatic Expand/Select](https://ui5.sap.com/docs/topics/10ca58b701414f7f93cd97156f898f80.html)
- [Batch Control](https://ui5.sap.com/docs/topics/74142a38e3d4467c8d6a70b28764048f.html)

### Routing

- `routes`, `targets` ve ortak `config` değerlerini manifest'te tut.
- Hash tabanlı deep-link/bookmark uyumlu route kullan.
- Gerekli/opsiyonel/query parametrelerini açık contract yap.
- Not-found/bypassed target sağla.
- Object key'i route'a yazarken encode/decode et.
- View/component oluşturmayı elle tekrar etme; target/lazy loading kullan.

Kaynak: [Routing Configuration](https://ui5.sap.com/docs/topics/902313063d6f45aeaa3388cc4c13c34e.html)

## 8. i18n, theming ve accessibility

- Kullanıcıya görünen label, tooltip, hata, empty state, ARIA metni ve dinamik mesajı i18n'e koy.
- Fallback ve desteklenen locale'leri tanımla.
- UI5 type/formatter ile locale duyarlı tarih/sayı/para/birim üret.
- Input için gerçek `Label`/`labelFor`; icon-only button için accessible name ver.
- `ariaLabelledBy`, `ariaDescribedBy`, landmark, table title ve focus'u doğrula.
- Standart control output'unu elle değiştirme.
- Hard-coded renk/ölçü yerine theme parameter/CSS custom property kullan.
- Standalone prototype'ta Horizon seçilebilir; üretim app'te kullanıcı/sistem tema seçimini gereksiz override etme.

Kaynaklar:

- [Localized Texts](https://ui5.sap.com/docs/topics/91f385926f4d1014b6dd926db0e91070.html)
- [Accessibility Recommendations](https://ui5.sap.com/docs/topics/ee37fc7138b843c0a66700f0aeaba3fe.html)
- [Labeling and Tooltips](https://ui5.sap.com/docs/topics/329a029f39e249a1bf89e3ffc006c8e1.html)
- [Theming](https://ui5.sap.com/docs/topics/497c27a8ee26426faacd2b8a1751794a.html)

## 9. Performans ve güvenlik

### Performans

- Sync module/data yükleme yok.
- Async bootstrap/component/view/fragment/routing.
- Manifest-first ve yalnız gereken library/module.
- UI5 CLI ile Component preload.
- 404 resource path yok.
- Minimal `$select/$expand`, server paging ve küçük payload.
- Büyük aggregation template'inde gereksiz nested control yok.
- Network request, bundle ve render maliyetini ölç.
- UI5 Support Assistant ve console'u kontrol et.

Kaynak: [Performance Checklist](https://ui5.sap.com/docs/topics/9c6400eb7dc145b78e94a81e6e390780.html)

### Güvenlik

- Authentication, authorization ve session'ı backend sorumluluğu say.
- Client validation'ı UX say; server validation'ı zorunlu kıl.
- CSP uyumlu ol: inline script/event, `eval`, `javascript:` URL ve sync loader yok.
- Arbitrary HTML/SVG'yi sanitize et veya kullanma.
- Haricî URL'yi allowlist ile doğrula.
- Hassas veriyi localStorage'a yazma.
- OData model CSRF mekanizmasını kullan.
- Üçüncü taraf kütüphaneyi lisans, CSP ve supply-chain gerekçesi olmadan ekleme.

Kaynaklar:

- [Securing Apps](https://ui5.sap.com/docs/topics/91f3d8706f4d1014b6dd926db0e91070.html)
- [CSP](https://ui5.sap.com/docs/topics/fe1a6dba940e479fb7c3bc753f92b28c.html)

## 10. Test ve build kalite kapıları

Test katmanları:

- QUnit: formatter/helper/controller-domain unit test; sıfır test keşfini başarısız say
- OPA5: aynı app içindeki navigation, binding ve user interaction; güncel UI5 Test Starter yaklaşımını tercih et
- wdi5: gerçek browser, FLP/auth ve uçtan uca sistem akışı

Stable UI5 ID/property selector kullan; CSS/DOM yapısına bağlanma. Sabit sleep yerine framework synchronization kullan.

Önerilen sıra:

1. Dependency install + lockfile
2. TypeScript typecheck
3. UI5 Linter
4. Proje lint/format
5. QUnit
6. OPA5
7. Gerekiyorsa wdi5
8. UI5 CLI production build
9. Build'i gerçek browser/FLP sandbox'ta aç
10. Support Assistant, console ve network kontrolü

Kaynaklar:

- [Testing Overview](https://ui5.sap.com/docs/topics/7cdee404cac441888539ed7bfe076e57.html)
- [QUnit](https://ui5.sap.com/docs/topics/09d145cd86ee4f8e9d08715f1b364c51.html)
- [OPA5](https://ui5.sap.com/docs/topics/2696ab50faad458f9b4027ec2f9b884d.html)
- [UI5 CLI](https://ui5.github.io/cli/stable/)
- [UI5 Linter](https://github.com/UI5/linter)

## 11. Kod üretim guardrail'leri

Şunları hata kabul et:

- Hedef sürüm doğrulanmadan yeni API/Manifest v2 kullanımı
- Deprecated/experimental/private API
- Belgelenmiş loader/bootstrap API'leri dışında global UI5 sınıf erişimi, `sap.ui.getCore()` veya `jQuery.sap.*` kullanımı
- `async: false`, sync XHR veya sync factory
- Inline script/style, `eval`, direct DOM manipulation
- Hard-coded UI metni, renk ve locale formatı
- Backend verisini topluca client'a çekme veya N+1 request
- Frontend visibility/disabled durumunu authorization sayma
- Fiori elements davranışını controller'da yeniden yazma
- Teste ve kullanıcıya önemli kontrolde stable ID olmaması
- UI5 Linter/build başarılı olsa da uygulamanın gerçek render'ının incelenmemesi
- QUnit/OPA5/Playwright komutunun sıfır test keşfetmesi veya sabit sleep ile görünür render'ı taklit etmesi
- `npm audit fix --force` ile incelenmemiş major dependency değişikliği; üretim ve build-time risklerini ayrı raporla
