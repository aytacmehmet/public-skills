# Teslim biçimleri ve kalite kapıları

Bu referansı PNG, interaktif tasarım, kod veya birleşik teslim üretirken ve “bitti” demeden önce oku.

## İçindekiler

1. Ortak teslim modeli
2. PNG sözleşmesi
3. İnteraktif tasarım sözleşmesi
4. Üretim kodu sözleşmesi
5. Birleşik teslim ve izlenebilirlik
6. Görsel doğrulama matrisi
7. Teknik doğrulama matrisi
8. Karşıt senaryolar
9. Teslim raporu

## 1. Ortak teslim modeli

Her kapsamda önce `design-contract.json` üret. Bu dosya şu çıktılar arasında tek kaynak olsun:

```text
requirements
    ↓
ABAP package / service metadata
    ↓
abap-backend-contract.json
    ↓
design-contract.json
    ├─ interactive prototype
    ├─ PNG captures
    ├─ production UI5/Fiori elements code
    └─ tests + verification report
```

Sözleşmede `verified`, `assumed`, `blocked` ayrımı yap. Hedef sürüm, servis veya yetki doğrulanmadıysa bunu kaybetme.

## 2. PNG sözleşmesi

PNG yalnız estetik görsel değildir; uygulanabilir ekran spesifikasyonudur.

Zorunlu:

- Çalışan UI5 prototipi veya doğrulanmış gerçek app render'ından capture
- Net viewport, breakpoint, theme, density ve state
- Okunabilir gerçekçi örnek veri; hassas/üretim verisi yok
- Uygulamanın ana görevini ve primary action'ı gösterme
- Gereksinime göre loading, empty, error, no-auth ve mobile varyant
- PNG ile prototip aynı build/data state'ten

Adlandırma:

```text
<app>-<screen>-<state>-<breakpoint>-<theme>-<density>.png
```

Örnek:

```text
sales-order-list-populated-L-horizon-compact.png
sales-order-object-validation-S-horizon-cozy.png
```

Capture öncesi:

1. Font/theme/resource yüklenmesini bekle.
2. Busy state'in istemeden kalmadığını kontrol et.
3. Console error ve 404 kontrol et.
4. Başlık, navigation, action, status ve tablo kolonunu gözle incele.
5. En tuhaf/uzun metinli örneği de capture et.

Generatif image modelini yazılı SAP ekranı için kullanma. Kullanıcı yalnız konsept moodboard istese dahi bunun uygulanabilir SAPUI5 spesifikasyonu olmadığını ayır.

## 3. İnteraktif tasarım sözleşmesi

İnteraktif tasarım, üretim backend'i olmadan görev akışını çalıştırmalı.

Zorunlu akışlardan kapsamla ilgili olanları uygula:

- Search/filter/go veya live filtering
- Table/list selection ve navigation
- Create/edit/save/cancel
- Dialog/popover/value help
- Validation/message popover
- Busy/loading → success/error
- Empty/no-results/no-auth
- Responsive navigation ve mobile adaptation

Teknik:

- Gerçek SAPUI5 control ve layout
- Horizon/default tema ve mock JSON/OData veri
- Async bootstrap ve manifest-first
- Stable ID ve i18n
- Üretim servisine yazma yok
- Mock state seçimi veya fixture ile deterministik demo
- Klavye ve görünür focus

Prototype “sahte shell” içeriyorsa bunu yalnız bağlam sunumu için işaretle. Üretim app kodunda FLP shell'i tekrar etme.

## 4. Üretim kodu sözleşmesi

Kod teslimi yalnız snippet değil, kapsamın gerektirdiği runnable bütünlükte olmalı.

Yeni freestyle app için tipik dosyalar:

- `package.json`, lockfile, `ui5.yaml`, TypeScript config
- `webapp/manifest.json`, `Component.*`
- XML view/fragment, controller/helper/model
- `i18n.properties`
- Mock/config yalnız geliştirme profili için
- QUnit/OPA5 ve gerekiyorsa wdi5
- Lint/build config

Fiori elements için:

- Generator/proje yapısını koru
- Manifest target/page config
- Backend/local annotation ve gerekliyse CDS metadata extension
- Yalnız resmî extension fragment/controller/building block
- Draft/action/side effect ve navigation contract
- Service metadata ile çalışan test/preview

Mevcut projede yalnız gereken dosyayı değiştir; style ve dependency düzenini koru. Kullanıcı istemedikçe geniş migration yapma.

## 5. Birleşik teslim ve izlenebilirlik

PNG + interactive + code varsa şu eşleşmeyi doğrula:

| Contract öğesi | PNG | Interactive | Code | Test |
|---|---|---|---|---|
| Page/section | Görünür | Navigable | Route/view/page config | OPA5/wdi5 |
| Field | Label/value/state | Editable/display | Binding/annotation | Unit/integration |
| Action | Yer/semantic | Çalışır | Handler/RAP action | Happy + failure |
| Loading | Görünür durum | Transition | Busy lifecycle | Delayed mock |
| Empty/error/no-auth | Ayrı state | Yeniden üretilebilir | Message/state logic | Edge case |
| Responsive | S/M/L/XL | Reflow/adapt | Responsive control/config | Viewport test |
| Accessibility | Label/focus görünümü | Keyboard | ARIA/stable ID | Manual/tool check |

Sözleşmede olup çıktılardan birinde olmayan öğeyi blocker veya açık kapsam dışı olarak işaretle.

## 6. Görsel doğrulama matrisi

En az şu sınıfları test et:

| Boyut | Örnek viewport | Kontrol |
|---|---:|---|
| S | 390×844 | Tek kolon, mobile table/dialog/navigation |
| M | 768×1024 | Tablet collapse/reflow |
| L | 1280×800 | Desktop ana hedef |
| XL | 1600×1000 | Max width/spacing/çok kolon |

Temalar:

- Morning Horizon
- Evening Horizon
- High Contrast Black
- High Contrast White

Density:

- Cozy
- Compact

Her kombinasyon için ayrı PNG teslim etmek zorunlu değildir; ancak kritik ekranların görünümünü doğrula ve hangi kombinasyonları gerçekten kontrol ettiğini raporla.

Gözle kontrol:

- Sayfa hiyerarşisi ve whitespace
- Primary action tekliği
- Label/field alignment
- Table identity ve column priority
- Semantic color + text/icon
- Focus, selected, hover, disabled/read-only
- Truncation, overflow, pop-in ve scroll
- Long localization ve RTL
- Empty/error/loading/no-auth

## 7. Teknik doğrulama matrisi

Statik denetim:

```powershell
python -B "<skill kökü>/scripts/validate_fiori_delivery.py" <delivery-root> --contract <delivery-root>/design-contract.json
```

Bu script strict JSON, sözleşme/manifest semantiği ve temel yapısal riskleri denetler; uyarılar varsayılan olarak kapıyı kapatır. `--allow-warnings` yalnız geliştirme sırasında geçici kaçış kapısıdır; gerçek build/test/render'ın yerine geçmez.

Sürüm denetimi iki ayrı değeri karşılaştırır: manifest `minUI5Version`, sözleşmedeki `architecture.minUI5Version` ile aynı olmalı (`SEMANTIC_MIN_UI5`) ve hedef `context.targetSystem.ui5Runtime` değerinden yeni olmamalıdır (`SEMANTIC_UI5_VERSION`). Runtime `unknown` ise `CONTRACT_TARGET_UNKNOWN` uyarısı teslim kapısını kapalı tutar. Renk denetimi yalnız CSS değerlerini ve tırnaklı renk literal'lerini işaretler; route hash'i veya ID seçicisi renk sayılmaz.

ABAP paketi kapsamdaysa doğrulayıcı ayrıca `abap-backend-contract.json` şemasını, dosya SHA-256 bütünlüğünü, active/complete durumunu, paket envanter hash'ini, servis protokolü/URI/entity set uyumunu ve backend → tasarım izlenebilirliğini kontrol eder. `partial` backend sözleşmesi uyarı üretir ve strict teslim kapısını kapatır.

Uygun komutları projeden keşfet ve çalıştır:

- Dependency install/lockfile
- TypeScript typecheck
- UI5 Linter ve proje lint
- QUnit
- OPA5
- wdi5 (kapsam uygunsa)
- UI5 CLI production build
- Support Assistant
- Browser console/network

Kanıt katmanları:

| İddia | Kanıt |
|---|---|
| JSON/manifest doğru | Parse + schema/yapı kontrolü |
| Kod derleniyor | Typecheck/build çıktısı |
| Test geçiyor | Test raporu; test sayısını oku |
| App açılıyor | Gerçek browser render |
| Görsel doğru | PNG/screenshot gözle inceleme |
| Responsive | S/M/L/XL gerçek viewport |
| Accessible | Keyboard, focus, screen reader/ARIA ve high contrast |
| Backend uyumlu | Metadata, preview/integration ve target release |
| Paket kanıtı bütün | Envanter sayısı + kaynak hash'i + backend contract hash'i + active/truncation kontrolü |

Sıfır test bulunup komut 0 dönerse başarılı test sayma. Fazla temiz sonuçta test discovery ve target path'i doğrula.

## 8. Karşıt senaryolar

Mutlu yol dışında en az ilgili olanları çalıştır:

- Sıfır kayıt, bir kayıt, binlerce kayıt
- Uzun metin, çok uzun object ID ve null/eksik alan
- Yavaş servis, timeout, 4xx/5xx ve retry
- Backend validation, warning ve multi-message
- Yetkisiz field/action ve tüm sayfa no-auth
- Draft çakışması, stale ETag, concurrent edit ve cancel data loss
- Offline/connection loss (ürün bunu destekliyorsa)
- RTL, Türkçe karakterler, German-length expansion
- Keyboard-only, focus return after dialog, screen reader label
- Zoom/text resize ve high contrast
- Phone'da Grid/Analytical/Tree Table alternatifi

## 9. Teslim raporu

Kısa ama kanıtlı raporla:

1. Sonuç ve dosya bağlantıları
2. Seçilen floorplan/framework ve gerekçe
3. Hedef UI5/Fiori guideline/backend release
4. Çalıştırılan doğrulamalar ve gözlenen sonuçlar
5. Görsel matrisin gerçekten kontrol edilen hücreleri
6. Doğrulanan/varsayılan/bloke kalan konular
7. Bilinen risk veya kullanıcı kararı gerektiren tek sonraki adım

“Bitti” demek için:

- Dosyaları yeniden aç
- Diff'i oku
- Script/build/test çıktısını oku
- App/PNG'yi gör
- İlk, son ve en tuhaf senaryoyu örnekle
- Asıl istekle yeniden karşılaştır
