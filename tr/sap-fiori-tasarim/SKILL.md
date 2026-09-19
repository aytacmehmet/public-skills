---
name: sap-fiori-tasarim
description: "Resmî SAP Design System ve SAPUI5 rehberlerine dayalı uçtan uca SAP Fiori for Web tasarım ve geliştirme becerisi. SAP Fiori, SAPUI5/UI5, Fiori elements, mockup/prototip/PNG, List Report, Object Page, OData/RAP veya S/4HANA ekranı tasarlamak, incelemek, kodlamak ya da refactor etmek; ayrıca yerel ADT/abapGit paketi, ZIP veya yapılandırılmış salt-okunur ADT bağlantısından ABAP paketini okuyup UI'ı CDS/RAP/servis sözleşmesine göre üretmek istendiğinde kullan. Görsel tasarım, backend kanıtı ve üretim kodunu izlenebilir sözleşmelerle bağlar; hedef sürüm, erişilebilirlik, performans, güvenlik ve Clean Core kapıları uygular."
metadata:
  version: "1.1.0"
  language: "tr"
  family: "sap-fiori-design"
  counterpart: "en/sap-fiori-design"
---

# SAP Fiori Tasarım

Ekranı önce iş görevi ve hedef sistem bağlamında tasarla; sonra aynı tasarımı gerçek SAPUI5 kontrolleriyle prototipe ve üretim koduna dönüştür. Görsel kaliteyi SAP standardından, teknik kaliteyi hedef çalışma zamanından ve doğrulanabilir kalite kapılarından türet. Kullanıcıyla onun dilinde konuş; varsayılan Türkçe. Kullanıcının talimatı bu yönergeden önceliklidir.

<invariants>
1. Tasarım ve kodun tek kaynağı `design-contract.json`'dır. PNG, prototip ve üretim kodundaki her sayfa, alan, eylem, durum ve responsive davranışı bu sözleşmeyle eşle.
2. PNG'yi çalışan UI5 prototipinden al. Metin ve kontrol ağırlıklı SAP ekranını generatif görselle çizme; generatif görseli yalnız açıkça istenen dekoratif illüstrasyonda kullan ve UI katmanından ayır.
3. Önce standart floorplan ve SAP Fiori elements OData V4 seçeneğini değerlendir. Freestyle SAPUI5'i yalnız doğrulanmış gereksinim standardı aşınca seç.
4. Hedef sistemin SAPUI5 sürümünü ve yeteneklerini doğrulamadan en yeni API'yi varsayma. Mevcut projede sürüm, dil ve yapı kurallarını koru.
5. Özel CSS, özel kontrol, controller extension ve frontend iş mantığı son çaredir. Tema token'ı, standart kontrol, annotation ve belgelenmiş extension point kullan.
6. Erişilebilirlik, responsive/adaptive davranış, i18n, güvenlik, hata/boş/yükleniyor durumları ve yetki modeli tasarımın parçasıdır.
7. Frontend görünürlüğü yetkilendirme değildir. Veri ve eylem yetkisini backend'de zorunlu kıl.
8. SAP'nin resmî AI Fiori becerisi yararlı bir tabandır, fakat deneyseldir ve insan doğrulaması ister. Hedef sürüm dokümantasyonuyla çapraz doğrula.
9. Yalnız kullanıcının sağladığı veya açıkça hedef proje olarak işaretlediği dosyalar proje kanıtıdır. Skill şablonundaki, örnek prototipteki veya ilgisiz çalışma alanındaki `minUI5Version`/manifest değerini hedef sistem bulgusu gibi raporlama; kanıt yoksa değeri `unknown` bırak.
10. ABAP paketi verildiyse UI mimarisi seçmeden önce `abap-backend-contract.json` üret. Kaynaktan çıkarılan bilgiyi gerçek `$metadata`, runtime, yetki veya released-object doğrulamasıyla karıştırma.
11. Canlı paketi yalnız önceden yapılandırılmış salt-okunur ADT araçlarıyla oku. Okuma isteği yazma, aktivasyon, publish, transport veya deploy izni değildir; sohbette credential, private key veya RSA isteme.

- Kötü: şablon manifest'inde `minUI5Version: 1.151.0` var → "Hedef sistem SAPUI5 1.151.0" diye raporlamak.
- İyi: `ui5Runtime: unknown` bırak; "1.151.0 yalnız scaffold profilidir, runtime'ı hedef sistemde doğrulayın" de.
</invariants>

<references>
İş başlamadan yalnız gereken dosyayı oku:

| Konu | Dosya |
|---|---|
| Görsel dil, tema, token, tipografi, ikon, yoğunluk, erişilebilirlik | [design-foundations.md](references/design-foundations.md) |
| Floorplan, kontrol ve durum kararları | [floorplans-and-patterns.md](references/floorplans-and-patterns.md) |
| SAPUI5/Fiori elements proje ve kod kuralları | [ui5-engineering.md](references/ui5-engineering.md) |
| ABAP paketi/ZIP/ADT snapshot okuma, backend → UI eşlemesi | [abap-package-intake.md](references/abap-package-intake.md) |
| RAP, OData V4, ABAP Cloud ve Clean Core veri sözleşmesi | [rap-backend-contract.md](references/rap-backend-contract.md) |
| PNG/interaktif/kod teslim biçimleri ve doğrulama matrisi | [delivery-and-quality.md](references/delivery-and-quality.md) |
| Canlı doğrulanacak resmî bağlantılar ve sürüm notu | [official-sources.md](references/official-sources.md) |

`references/behavior-checks.md` ve `references/source-notes.md` yalnız skill bakımı içindir; çalışma zamanında okuma.

Komutlardaki `<skill kökü>`, host'un bu skill için bildirdiği taban dizindir. Betikleri çalışma dizininden bağımsız olarak `python -B "<skill kökü>/scripts/<ad>.py"` biçiminde çalıştır; `-B`, skill klasörüne `__pycache__` yazılmasını önler.

Belirli bir UI öğesi veya floorplan için ayrıntı gerekiyorsa resmî, hedef sürümlü SAP sayfasını ayrıca aç. UI5 Demo Kit örneği tek başına Fiori tasarım kanıtı değildir.
</references>

<scope>
Sohbet, mevcut dosyalar, servis metadata'sı, ekran görüntüleri ve gereksinimlerden şu alanları doldur; bilinmeyeni `unknown` yaz, uydurma:

`Rol ve görev` (kullanıcı rolü, karar/görev, başarı ölçütü) · `İş nesnesi` (ana nesne, alt nesneler, statüler, eylemler) · `Hedef sistem` (S/4HANA Cloud Public/Private, on-premise, BTP veya bağımsız UI5) · `Sürüm ve protokol` (SAPUI5 runtime, Fiori guideline sürümü, OData V2/V4, RAP, draft) · `Proje` (mevcut mi yeni mi; Fiori elements, freestyle veya bilinmiyor) · `Cihaz ve dil` (birincil cihazlar, dil/RTL, tema/markalama, erişilebilirlik hedefi) · `Çıktı` (`png`, `interactive`, `png+interactive`, `code` veya birleşimi) · `Sınırlar` (test, dağıtım, teslim).

Bağlamda olanı yeniden sorma. Sonucu değiştirecek tek büyük eksik varsa tek kısa soru sor; değilse varsayımı sözleşmeye kaydet ve devam et. Görsel format söylenmemişse `png+interactive` varsay.

| Çıktı | Üretilen | Ön koşul |
|---|---|---|
| `png` / `png+interactive` | `prototype/` + `visuals/*.png` | Yok; PNG gerçek tarayıcı capture'ıdır |
| `interactive` | `prototype/` | Yok |
| `code` | `app/` (prototipten bağımsız) | Framework, gözden geçirilmiş `--ui5-version` profili, gözlenmiş servis URI'si ve entity set |
| `all` | Hepsi | `code` ön koşulları |
</scope>

<evidence>
- **Mevcut proje:** kullanıcı kapsam içine koyduysa önce `package.json`, `ui5.yaml`, `manifest.json`, `Component.*`, view/fragment/controller, annotation/CDS kaynakları, testler ve servis metadata'sını oku. Proje verilmediyse ilgisiz çalışma alanını hedef proje gibi inceleme. `minUI5Version` ile gerçek runtime farkını kontrol et.
- **ABAP paketi** (ADT export'u, abapGit klasörü/ZIP'i veya canlı paket adı): önce [abap-package-intake.md](references/abap-package-intake.md) dosyasını oku, sonra:

```powershell
python -B "<skill kökü>/scripts/inspect_abap_package.py" <paket-klasörü-veya-zip> `
  --output <çıktı>/abap-backend-contract.json `
  --package-name <paket> --service-uri <gözlenen-uri> --protocol odata-v4
```

- **Seçim inspector'ın değil kanıtındır:** pakette birden fazla service definition veya entity set adayı varsa inspector seçmez, `gaps` içine yazar. UI servisini `--service-definition`, ana entity set'i `--entity-set` ile kanıta dayanarak adlandır.
- **Canlı sistem:** yalnız salt-okunur ADT araçları (örneğin `sap-cloud-erp` MCP sunucusu) mevcut ve bağlantı önceden yapılandırılmışsa tüm paket sayfalarını ve gerekli active kaynak sayfalarını SHA-bağlı oku, normalleştirilmiş ADT snapshot oluştur, aynı inspector'a ver. Araç yoksa yerel export iste ve blocker olarak kaydet. Paket adından nesne veya servis URI'si tahmin etme.
- **Sözleşmeye aktar:** entity, field, association, annotation, draft, action, validation, side effect, DCL ve service exposure kanıtlarını tasarım sözleşmesine taşı. `gaps` çözülmeden veya açık blocker/varsayım yazılmadan üretim koduna geçme. `unparsedElements` ile `dynamicFeatureControl` altındakileri gerçek `$metadata` ile doğrula; `draftActions` listesini iş action'ı olarak tasarlama. Parser sonucu compiler/activation/service preview kanıtı değildir.
- **Sürümü kilitle:** hedef sürüm bilinmiyorsa üretim kodu scaffold etme; yalnız prototip veya sözleşme üret ve sürümü `unknown` bırak. `--ui5-version` yalnız scaffold profilini (tooling ve `minUI5Version`) seçer; hedef sistemde gözlenen runtime `--target-ui5-runtime` ile ayrıca verilir. Profil gözlenen runtime'dan yeniyse scaffold reddeder; o runtime için gözden geçirilmiş yeni profil (kendi lockfile'ıyla) ekle.
- **Canlı doğrulama:** internet varsa [official-sources.md](references/official-sources.md) üzerinden resmî dokümanı aç. Bu turda sayfayı gerçekten açıp sürüm göstergesini görmeden "gözlendi/doğrulandı" deme; statik araştırma notu yalnız arama ipucudur. Fiori guideline sürümü ile SAPUI5 runtime sürümünü ayrı alanlarda, tam değer + URL + kontrol tarihiyle kaydet.

- Kötü: pakette `Z_UI_ORDER` ve `Z_API_ORDER` var → ilkini seçip manifest'e yazmak.
- İyi: `gaps` satırını göster, UI servisini kaynaktan belirle, `--service-definition Z_UI_ORDER` ile yeniden çalıştır.
</evidence>

<contract>
Çalışma alanını oluştur; işlem `design-contract.json` ile yerel `design-contract.schema.json` dosyasını birlikte üretir:

```powershell
python -B "<skill kökü>/scripts/scaffold_fiori_workspace.py" <çıktı> --app-id <ad.alanı> --name <ad> `
  --language <tr|en> --output <tip> [--backend-contract <çıktı>/abap-backend-contract.json]
```

Şablon alanlarının türünü veya kök şemasını geçici cevap için değiştirme; yeni ihtiyaçta şemayı ve doğrulayıcıyı aynı değişiklikte güncelle. Şu alanların hepsini doldur:

- `context`: rol, görev, nesne, sistem, sürüm; `context.evidence` içinde doğrulanmış/varsayılmış/bilinmeyen ayrımı
- `architecture`: floorplan, framework, gerekçe, reddedilen alternatifler; üretim kodunda `minUI5Version`
- `informationArchitecture`: sayfalar, bölümler, navigasyon, öncelik
- `fieldsAndActions`: alan semantiği, zorunluluk, value help, eylem yeri ve yetki
- `states`: initial, loading, populated, empty, error, no-auth ve ilgili edit/draft durumları
- `responsive`: S/M/L/XL davranışı, cozy/compact, tablonun telefon alternatifi
- `accessibility`: başlık hiyerarşisi, etiketler, klavye/odak, ARIA ilişkileri, metin alternatifleri
- `dataContract`: entity, navigation, action/function, `$select`, dar `$expand`, paging, side effects
- `backendEvidence`: ABAP sözleşmesi yolu/hash'i, paket, kaynak modu, bütünlük, aktif sürüm, açık boşluklar
- `traceability`: gereksinim → ekran/kontrol → ABAP nesnesi/dosya → servis/annotation → test
- `sources`: URL, sürüm, kontrol tarihi

Koddan önce sözleşmeyi yeniden oku. Görsel ve teknik karar çelişirse çelişkiyi burada çöz.
</contract>

<architecture>
Öncelik sırası:

1. Standart SAP Fiori elements OData V4 floorplan
2. Fiori elements + belgelenmiş building block/extension point
3. Fiori elements custom page/flexible programming model
4. Freestyle SAPUI5
5. Özel kontrol; yalnız diğerleri gereksinimi karşılamıyorsa

List/filter/drill-down için List Report + Object Page'i; analitik filtre-grafik-tablo işi için Analytical List Page'i; gerçek list-detail(-detail) akışı için Flexible Column Layout'u değerlendir. Seçimi görünüşe göre değil görev, veri hacmi, düzenleme akışı, cihaz ve backend kabiliyetine göre yap. Ayrıntı: [floorplans-and-patterns.md](references/floorplans-and-patterns.md), [ui5-engineering.md](references/ui5-engineering.md).
</architecture>

<prototype>
`--output interactive` ile `assets/ui5-prototype/` iskeletini ayrı `prototype/` klasörüne üret veya mevcut uygulamayı prototip olarak kullan. Bu şablonu üretim kodu diye teslim etme. Gerçek SAPUI5 kontrolleri, sabitlenmiş prototip runtime'ı, Horizon tema ve mock JSON/OData verisiyle çalışan akış kur.

- Shell ile uygulama içeriğini ayır; üretim app içinde FLP shell'i tekrar etme.
- Kritik akışları çalıştır: filtreleme, seçim, navigasyon, create/edit/save/cancel, doğrulama, dialog ve mesajlar.
- Boş, yoğun, hata, yetkisiz ve yükleniyor durumlarını erişilebilir şekilde göster.
- Sabit piksel yerleşimi yerine UI5 responsive kontrol ve layout'larını kullan.
- Gerçek kullanıcı verisine veya üretim servisine bağlanma; mock veri kullan.
- Kontrol metinlerini i18n kaynağına koy; örnekte dahi locale duyarlı sayı/tarih/birim göster.

**PNG:** prototipi gerçek tarayıcıda aç, yüklenme bitince incele ve ekran görüntüsü al. En az birincil hedef görünümü teslim et; kalite kontrolü için S/M/L/XL sınıflarını örnekle. Dosya adı: `<app>-<ekran>-<durum>-<breakpoint>-<tema>-<yoğunluk>.png`. PNG ile prototip birlikte istendiyse aynı build ve aynı veri durumunu kullan; ikisini elle ayrı tasarlama.
</prototype>

<production>
Mevcut projede yerel stile uy. Yeni scaffold'da framework, UI5 profili, servis protokolü/URI'si ve entity set kullanıcı kanıtından veya doğrulanmış `abap-backend-contract.json` dosyasından gelmeden ilerleme. `--output code`, `app/` altında prototipten bağımsız proje oluşturur. Yeni scaffold yalnız OData V4 üretir; mevcut OData V2 uygulamayı okuyup korur fakat V4 şablonuyla taklit etmez. Yeni freestyle uygulamada TypeScript kullan; mevcut JavaScript projeyi gerekçesiz toplu migration'a zorlama.

- Manifest V2 hedefinde kaldırılmış `async` alanlarını ekleme; framework'ün asenkron varsayılanını ve asenkron bootstrap'ı kullan.
- UI5 CLI, UI5 Linter, runtime/types/tooling sürümlerini tam sabitle; lockfile güncel olsun.
- XML View/Fragment veya uygun typed view; kısa view, stabil ID, controller'a noktalı event handler.
- Global ad, deprecated/experimental API, sync XHR, inline script/style ve doğrudan DOM müdahalesi yok.
- `i18n`, UI5 veri tipleri, message handling, busy handling, hata yakalama ve yaşam döngüsü temizliği.
- OData V4 model/binding; server-side filtre/sort/page, dar veri seçimi, kontrollü batch group.
- Fiori elements'te annotation/config ile çöz; extension kodunu yalnız belgelenmiş extension point'e koy.
- Standart tema parametreleri ve layout sınıfları; hard-coded renk/font/gölge/radius yok.
- Hassas bilgi sızdırma, dinamik HTML enjekte etme, frontend'de güvenlik kararı verme.
- QUnit birim testleri, OPA5 entegrasyon akışları, sıfır-test denetimi; kapsam uygunsa wdi5/Playwright uçtan uca testleri.

Backend tasarımı veya UI annotation gerekiyorsa [rap-backend-contract.md](references/rap-backend-contract.md) kurallarını uygula. SAP API/nesnesinin release durumunu canlı sistemde doğrulamadan "released" deme.
</production>

<verification>
Önce teslim tipine göre [delivery-and-quality.md](references/delivery-and-quality.md) matrisini uygula, sonra statik denetimi çalıştır:

```powershell
python -B "<skill kökü>/scripts/validate_fiori_delivery.py" <çıktı-klasörü> --contract <çıktı-klasörü>/design-contract.json
```

Doğrulayıcı uyarıda da başarısız olur; `--allow-warnings` yalnız tasarım sürerken geçicidir, teslim kapısında kullanma. Manifest `minUI5Version` değeri sözleşmedeki `architecture.minUI5Version` ile eşit olmalı ve hedef `ui5Runtime` değerinden yeni olmamalıdır; runtime `unknown` ise uyarı kapıyı kapalı tutar. Uygun projede ayrıca `npm ci`, typecheck/manifest doğrulaması, UI5 Linter, production build, QUnit, OPA5/wdi5/Playwright, UI5 Support Assistant ve browser console çalıştır. Yalnız çıkış koduna güvenme: keşfedilen test sayısını oku, uygulamayı ve PNG'yi gözle incele.

Karşıt test yap: uzun çeviri ve RTL · sıfır kayıt, binlerce kayıt, geciken servis · yetkisiz eylem, backend validation hatası, concurrency/draft çakışması · klavye-only ve görünür odak · S/M/L/XL, cozy/compact, Morning/Evening/HCB/HCW · PNG/prototip/kod arasında aynı alan, eylem, durum ve öncelik.

Aynı doğrulama hatasına iki kez yama uyguladıysan yamayı bırak, varsayımı yeniden test et.
</verification>

<self_check>
"Bitti" demeden önce: her dosyayı yeniden açtın · script/build/test çıktısını okudun · uygulamayı ve PNG'yi gördün · ilk, son ve en tuhaf senaryoyu örnekledin · sonucu asıl istekle karşılaştırdın. Üretilmiş ama açılıp incelenmemiş dosya bitmiş değildir.
</self_check>

<delivery>
Önce sonucu ver, sonra yalnız karar için gereken kanıtı; süreç anlatımı yok:

1. Dosya bağlantıları: PNG, interaktif prototip, kaynak kod, `design-contract.json`
2. Seçilen floorplan/framework ve tek cümle gerekçe
3. Hedef ve scaffold UI5 sürümü, Fiori guideline sürümü — ayrı ayrı
4. Çalıştırılan testler ve gözlenen sonuçlar
5. Doğrulanamayan varsayımlar, açık `gaps` ve kalan gerçek riskler
6. Gereksinim → tasarım → kod → test izlenebilirliği

Sağlanmayan dosyayı, çalıştırılmayan testi veya görülmeyen runtime değerini gözlenmiş kanıt gibi raporlama. Niyeti değil gözlemi bildir.
</delivery>

<resources>
- `assets/design-contract.template.json`, `assets/design-contract.schema.json`: görsel ile kodu bağlayan sözleşme ve makine-okunur şeması.
- `assets/abap-backend-contract.schema.json`: paket envanteri ile RAP/OData/UI kanıtının şeması.
- `assets/version-profiles.json`: birlikte doğrulanmış, tam sabitlenmiş UI5/tooling profilleri ve `defaultProfile`. Şablon lockfile'ları bu profile aittir; yeni profil eklerken lockfile'ı o profille yeniden üret.
- `assets/ui5-prototype/`: yalnız interaktif tasarım için mock verili prototip.
- `assets/ui5-production-freestyle/`: TypeScript, UI5 CLI/Linter, QUnit, OPA5 ve tarayıcı kalite kapılı üretim iskeleti.
- `assets/ui5-production-fiori-elements/`: OData V4 List Report/Object Page ve tarayıcı smoke testli metadata-first iskelet.
- `scripts/scaffold_fiori_workspace.py`: çıktı tipine göre prototip ile üretim projesini ayrı ve üzerine yazmadan oluşturur.
- `scripts/inspect_abap_package.py`: yerel paket/ZIP veya salt-okunur ADT snapshot'ından backend sözleşmesi üretir.
- `scripts/validate_fiori_delivery.py`: strict JSON, sözleşme-kod semantiği, proje yapısı ve riskleri fail-closed denetler.
- `tests/test_skill_tools.py`: üç betiğin davranış testleri; betik veya şablon değişince `python -B "<skill kökü>/tests/test_skill_tools.py"` ile çalıştır.

Şablonları kör kopyalama; hedef sürüme ve mevcut proje yapısına uyarla.
</resources>
