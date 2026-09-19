---
name: sap-fiori-tasarim
description: "Resmî SAP Design System ve SAPUI5 rehberlerine dayalı uçtan uca SAP Fiori for Web tasarım ve geliştirme becerisi. SAP Fiori, SAPUI5/UI5, Fiori elements, mockup/prototip/PNG, List Report, Object Page, OData/RAP veya S/4HANA ekranı tasarlamak, incelemek, kodlamak ya da refactor etmek; ayrıca yerel ADT/abapGit paketi, ZIP veya yapılandırılmış salt-okunur ADT bağlantısından ABAP paketini okuyup UI'ı CDS/RAP/servis sözleşmesine göre üretmek istendiğinde kullan. Görsel tasarım, backend kanıtı ve üretim kodunu izlenebilir sözleşmelerle bağlar; hedef sürüm, erişilebilirlik, performans, güvenlik ve Clean Core kapıları uygular."
metadata:
  version: "1.0.0"
  language: "tr"
  family: "sap-fiori-design"
  counterpart: "en/sap-fiori-design"
---

# SAP Fiori Tasarım

SAP Fiori for Web ekranını önce iş görevi ve hedef sistem bağlamında tasarlamak, sonra aynı tasarımı gerçek SAPUI5 kontrolleriyle prototip ve üretim koduna dönüştürmek. Görsel kaliteyi SAP standardından, teknik kaliteyi hedef çalışma zamanından ve doğrulanabilir kalite kapılarından türetmek.

## Değişmez kurallar

1. Tasarım ve kod için tek kaynak olarak `design-contract.json` kullanmak. PNG, interaktif prototip ve üretim kodundaki sayfa, alan, eylem, durum ve responsive davranışları bu sözleşmeyle eşlemek.
2. PNG'yi mümkün olduğunda çalışan UI5 prototipinden almak. Metin ve kontrol ağırlıklı SAP ekranını generatif görselle çizmemek. Generatif görseli yalnız açıkça istenen dekoratif illüstrasyon için kullanmak ve UI katmanından ayırmak.
3. Önce standart floorplan ve SAP Fiori elements OData V4 seçeneğini değerlendirmek. Freestyle SAPUI5'i yalnız doğrulanmış gereksinim standardı aşınca seçmek.
4. Hedef sistemin SAPUI5 sürümünü ve yeteneklerini doğrulamadan en yeni API'yi varsaymamak. Mevcut projede sürüm, dil ve yapı kurallarını korumak.
5. Özel CSS, özel kontrol, controller extension ve frontend iş mantığını son çare yapmak. Tema token'ı, standart kontrol, annotation ve belgelenmiş extension point kullanmak.
6. Erişilebilirlik, responsive/adaptive davranış, i18n, güvenlik, hata/boş/yükleniyor durumları ve yetki modelini tasarımın parçası saymak.
7. Frontend görünürlüğünü yetkilendirme sanmamak. Veri ve eylem yetkisini backend'de zorunlu kılmak.
8. SAP'nin resmî AI Fiori becerisini yararlı bir taban kabul etmek, fakat deneysel olduğunu ve insan doğrulaması gerektirdiğini unutmamak. Hedef sürüm dokümantasyonuyla çapraz doğrulamak.
9. Yalnız kullanıcının sağladığı veya açıkça hedef proje olarak işaretlediği dosyaları proje kanıtı saymak. Skill şablonundaki, örnek prototipteki veya ilgisiz çalışma alanındaki `minUI5Version`/manifest değerini hedef sistem bulgusu gibi raporlamamak; kanıt yoksa değeri `unknown` bırakmak.
10. ABAP paketi verildiyse UI mimarisi seçmeden önce `abap-backend-contract.json` üretmek. CDS/RAP/service kaynağından çıkarılan bilgiyle gerçek `$metadata`, runtime, yetki veya released-object doğrulamasını birbirine karıştırmamak.
11. Canlı paket okumasını yalnız önceden yapılandırılmış salt-okunur ADT araçlarıyla yapmak. Paket okuma isteğini yazma, aktivasyon, publish, transport veya deploy izni saymamak; kullanıcıdan sohbette credential, private key veya RSA istememek.

## Kaynak yönlendirmesi

İş başlamadan yalnız gereken referansları okumak:

- Görsel dil, tema, token, tipografi, ikon, yoğunluk ve erişilebilirlik için [design-foundations.md](references/design-foundations.md).
- Floorplan, kontrol ve durum kararları için [floorplans-and-patterns.md](references/floorplans-and-patterns.md).
- SAPUI5/Fiori elements proje ve kod kuralları için [ui5-engineering.md](references/ui5-engineering.md).
- ABAP paketi/ZIP/ADT snapshot okuma ve backend → UI eşlemesi için [abap-package-intake.md](references/abap-package-intake.md).
- RAP, OData V4, ABAP Cloud ve Clean Core veri sözleşmesi için [rap-backend-contract.md](references/rap-backend-contract.md).
- PNG/interaktif/kod teslim biçimleri ve doğrulama matrisi için [delivery-and-quality.md](references/delivery-and-quality.md).
- Canlı doğrulama yapılacak resmî bağlantılar ve sürüm notu için [official-sources.md](references/official-sources.md).

Komutlardaki `<skill kökü>`, host'un bu skill için bildirdiği taban dizindir; betikleri çalışma dizininden bağımsız olarak `python -B "<skill kökü>/scripts/<ad>.py"` biçiminde çalıştırmak. `-B`, skill klasörüne `__pycache__` yazılmasını önler.

Belirli bir UI öğesi veya floorplan hakkında ayrıntı gerekiyorsa resmî, hedef sürümlü SAP sayfasını ayrıca açmak. UI5 Demo Kit örneğini tek başına Fiori tasarım kanıtı saymamak.

## Uçtan uca çalışma akışı

### 1. İsteği ve çıktıyı kapsamla

Sohbet, mevcut dosyalar, servis metadata'sı, ekran görüntüleri ve kullanıcı gereksinimlerinden şu bilgileri çıkarmak:

- Kullanıcı rolü, karar/görev ve başarı ölçütü
- Ana iş nesnesi, alt nesneler, statüler ve eylemler
- Hedef ürün/sistem: S/4HANA Cloud Public/Private, on-premise, BTP veya bağımsız UI5
- SAPUI5/Fiori guideline sürümü, OData V2/V4, RAP ve draft durumu
- Mevcut proje mi yeni proje mi; Fiori elements, freestyle veya bilinmiyor
- Birincil cihazlar, dil/RTL, tema/markalama ve erişilebilirlik hedefi
- İstenen çıktı: `PNG`, `interactive`, `PNG+interactive`, `code` veya birleşimi
- Test, dağıtım ve teslim sınırları

Bağlamda olanı yeniden sormamak. Sonucu değiştirecek tek büyük eksik varsa bir kısa soru sormak; değilse varsayımı açıkça kaydetmek. Görsel format söylenmemişse `PNG+interactive` varsaymak ve PNG'yi prototipten türetmek.

### 2. Kanıtı aç, ABAP paketini modelle ve hedef sürümü kilitle

Kullanıcı mevcut bir projeyi kapsam içine koyduysa önce o projenin `package.json`, `ui5.yaml`, `manifest.json`, `Component.*`, view/fragment/controller dosyaları, annotation/CDS kaynakları, testleri ve servis metadata'sını okumak. Kullanıcı proje/dosya vermediyse ilgisiz çalışma alanını hedef proje gibi incelememek. `minUI5Version` ile gerçek runtime farkını kontrol etmek.

Kullanıcı ABAP paketi, ADT export'u, abapGit klasörü/ZIP'i veya canlı paket adı verdiyse [abap-package-intake.md](references/abap-package-intake.md) rehberini okumak. Yerel kaynakta:

```powershell
python -B "<skill kökü>/scripts/inspect_abap_package.py" <paket-klasörü-veya-zip> `
  --output <çıktı>/abap-backend-contract.json `
  --package-name <paket> --service-uri <gözlenen-uri> --protocol odata-v4
```

Pakette birden fazla service definition veya birden fazla aday entity set varsa inspector seçim yapmaz; `gaps` içine yazar. UI servisini `--service-definition`, ana entity set'i `--entity-set` ile kanıta dayanarak adlandırmak.

Canlı sistemde yalnız salt-okunur ADT araçları (örneğin `sap-cloud-erp` MCP sunucusu) mevcut ve bağlantı önceden yapılandırılmışsa tüm paket sayfalarını ve gerekli active kaynak sayfalarını SHA-bağlı okuyup normalleştirilmiş ADT snapshot oluşturmak; sonra aynı inspector ile sözleşmeye dönüştürmek. Araç yoksa yerel export istemek ve bunu blocker olarak kaydetmek. Paket adıyla nesne veya servis URI'si tahmin etmemek.

`abap-backend-contract.json` içindeki entity, field, association, annotation, draft, action, validation, side effect, DCL ve service exposure kanıtlarını tasarım sözleşmesine aktarmak. `gaps` listesini çözmeden veya açık blocker/varsayım yapmadan üretim koduna geçmemek. Parser sonucunu compiler/activation/service preview kanıtı saymamak. Inspector'ın okuyamadığı alanları (`unparsedElements`) ve `dynamicFeatureControl` altındaki çalışma zamanına bağlı işlemleri gerçek `$metadata` ile doğrulamak; `draftActions` listesini iş action'ı olarak tasarlamamak.

Yeni projede hedef sürüm bilinmiyorsa üretim kodu scaffold etmemek; yalnız prototip veya sözleşme üretmek ve sürümü `unknown` bırakmak. Üretim scaffold'u için hedefle uyumlu, gözden geçirilmiş exact profil istemek. `--ui5-version` yalnız scaffold profilini (tooling ve `minUI5Version`) seçer; hedef sistemde gözlenen runtime `--target-ui5-runtime` ile ayrıca verilir ve verilmedikçe sözleşmede `unknown` kalır. Profil gözlenen runtime'dan yeniyse scaffold reddeder; o runtime için gözden geçirilmiş yeni profil (kendi lockfile'ıyla) eklemek. İnternet erişimi varsa [official-sources.md](references/official-sources.md) üzerinden resmî dokümanı canlı doğrulamak. Bu turda canlı sayfayı gerçekten açıp sürüm göstergesini görmeden “gözlendi/doğrulandı” dememek; statik araştırma fotoğrafını yalnız arama ipucu saymak. Fiori guideline sürümüyle SAPUI5 runtime sürümünü ayrı alanlarda, tam değer + URL + kontrol tarihiyle kaydetmek ve birbirinin yerine yazmamak.

### 3. Tasarım sözleşmesini oluştur

`python -B "<skill kökü>/scripts/scaffold_fiori_workspace.py" <çıktı> --app-id <ad.alanı> --name <ad> --language <tr|en> --output <tip>` ile çalışma alanını oluşturmak; bu işlem `design-contract.json` ile yerel `design-contract.schema.json` dosyasını birlikte üretir. Şablon alanlarının türünü veya kök şemasını geçici cevap için değiştirmemek; yeni ihtiyaç varsa şema ve doğrulayıcıyı aynı değişiklikte güncellemek. Doğrulanmış/varsayılmış/bilinmeyen ayrımını `context.evidence`, kaynak sürümünü `sources` içinde tutmak. Şunları mutlaka tanımlamak:

- `context`: rol, görev, nesne, sistem, sürüm ve doğrulanmış/varsayılmış bilgiler
- `architecture`: seçilen floorplan, framework, gerekçe, reddedilen alternatifler ve üretim kodunda `minUI5Version`
- `informationArchitecture`: sayfalar, bölümler, navigasyon ve öncelik
- `fieldsAndActions`: alan semantiği, zorunluluk, value help, eylem yeri ve yetki
- `states`: initial, loading, populated, empty, error, no-auth ve ilgili edit/draft durumları
- `responsive`: S/M/L/XL davranışı, cozy/compact ve tablonun telefon alternatifi
- `accessibility`: başlık hiyerarşisi, etiketler, klavye/odak, ARIA ilişkileri ve metin alternatifleri
- `dataContract`: entity, navigation, action/function, `$select`, dar `$expand`, paging ve side effects
- `backendEvidence`: ABAP sözleşmesi yolu/hash'i, paket, kaynak modu, bütünlük, aktif sürüm ve açık boşluklar
- `traceability`: gereksinim → ekran/kontrol → ABAP nesnesi/dosya → servis/annotation → test eşlemesi

Tasarım sözleşmesini koddan önce yeniden okumak. Görsel ve teknik karar çelişirse çelişkiyi burada çözmek.

### 4. Floorplan ve teknoloji kararını ver

Şu öncelik sırasını kullanmak:

1. Standart SAP Fiori elements OData V4 floorplan
2. Fiori elements + belgelenmiş building block/extension point
3. Fiori elements custom page/flexible programming model
4. Freestyle SAPUI5
5. Özel kontrol; yalnız diğerleri gereksinimi karşılamıyorsa

List/filter/drill-down için List Report + Object Page'i; analitik filtre-grafik-tablo işi için Analytical List Page'i; gerçek list-detail(-detail) akışı için Flexible Column Layout'u değerlendirmek. Floorplan seçimini yalnız görünüşe göre değil görev, veri hacmi, düzenleme akışı, cihaz ve backend kabiliyetine göre yapmak.

Karar ayrıntısı için [floorplans-and-patterns.md](references/floorplans-and-patterns.md) ve [ui5-engineering.md](references/ui5-engineering.md) okumak.

### 5. İnteraktif tasarımı üret

`--output interactive` ile `assets/ui5-prototype/` iskeletini ayrı `prototype/` klasörüne üretmek veya mevcut uygulamayı prototip olarak kullanmak. Bu şablonu üretim kodu diye teslim etmemek. Gerçek SAPUI5 kontrolleri, sabitlenmiş prototip runtime'ı, Horizon tema ve mock JSON/OData verisiyle çalışır bir akış kurmak.

- Shell ile uygulama içeriğini ayırmak; üretim app içinde FLP shell'i tekrar etmemek.
- Kritik akışları çalıştırmak: filtreleme, seçim, navigasyon, create/edit/save/cancel, doğrulama, dialog ve mesajlar.
- İlgili boş, yoğun, hata, yetkisiz ve yükleniyor durumlarını erişilebilir şekilde göstermek.
- Sabit piksel yerleşimi yerine UI5 responsive kontrol ve layout'larını kullanmak.
- Gerçek kullanıcı verisi veya üretim servisine varsayılan olarak bağlanmamak; mock veri kullanmak.
- Kontrol metinlerini i18n kaynağına koymak; tasarım örneğinde dahi locale duyarlı sayı/tarih/birim göstermek.

### 6. PNG üret

PNG istenirse prototipi gerçek tarayıcıda açmak, yüklenme tamamlanınca görseli incelemek ve ekran görüntüsü almak. En az birincil hedef görünümü teslim etmek; ayrıca kalite kontrolü için S/M/L/XL sınıflarını örneklemek. Dosya adında ekran, durum, breakpoint, tema ve yoğunluğu belirtmek.

PNG ile interaktif prototip birlikte istenirse aynı build ve aynı veri durumunu kullanmak. İki çıktıyı elle ayrı ayrı tasarlamamak.

### 7. Üretim kodunu yaz

Mevcut projede yerel stile uymak. Yeni kod scaffold'u üretirken framework, UI5 sürümü, servis protokolü/URI'si ve entity set'i kullanıcı kanıtından veya doğrulanmış `abap-backend-contract.json` dosyasından gelmeden ilerlememek. `--output code` üretimi `app/` altında prototipten bağımsız proje oluşturur. Yeni scaffold yalnız OData V4 üretir; mevcut OData V2 uygulamayı okuyup koruyabilir fakat V4 şablonuyla taklit etmez. Yeni freestyle uygulamada TypeScript kullanmak; mevcut JavaScript projeyi gerekçesiz toplu migration'a zorlamamak. Şunları uygulamak:

- Manifest V2 hedefinde kaldırılmış `async` alanlarını eklememek; framework'ün asenkron varsayılanını ve asenkron bootstrap'ı kullanmak
- Exact-pinned UI5 CLI, UI5 Linter, runtime/types/tooling sürümleri ve güncel lockfile
- XML View/Fragment veya uygun typed view; kısa view, stabil ID ve controller'a noktalı event handler
- Global adlar, deprecated/experimental API, sync XHR, inline script/style ve doğrudan DOM müdahalesinden kaçınma
- `i18n`, UI5 veri tipleri, message handling, busy handling, hata yakalama ve yaşam döngüsü temizliği
- OData V4 model/binding; server-side filtre/sort/page, dar veri seçimi ve kontrollü batch group
- Fiori elements'te annotation/config ile çözme; extension kodunu yalnız belgelenmiş extension point'e koyma
- Standart tema parametreleri ve layout sınıfları; hard-coded renk/font/gölge/radius kullanmama
- Hassas bilgi sızdırmama, dinamik HTML enjekte etmeme ve frontend'de güvenlik kararı vermeme
- QUnit birim testleri, OPA5 entegrasyon akışları, sıfır-test denetimi ve kapsam uygunsa wdi5/Playwright uçtan uca testleri

Backend tasarımı veya UI annotation gerekiyorsa [rap-backend-contract.md](references/rap-backend-contract.md) kurallarını uygulamak. Kullanılabilir SAP API/nesnesinin release durumunu canlı sistemde doğrulamadan “released” diye iddia etmemek.

### 8. Katmanında doğrula

Önce teslim tipine göre [delivery-and-quality.md](references/delivery-and-quality.md) matrisini uygulamak. Sonra statik denetimi çalıştırmak:

```powershell
python -B "<skill kökü>/scripts/validate_fiori_delivery.py" <çıktı-klasörü> --contract <çıktı-klasörü>/design-contract.json
```

Doğrulayıcı uyarıda varsayılan olarak başarısız olur. Manifest `minUI5Version` değerini sözleşmedeki `architecture.minUI5Version` ile eşit, hedef `ui5Runtime` değerinden ise yeni olmamak üzere denetler; runtime `unknown` ise uyarı kapıyı kapalı tutar. Yalnız tasarım sürerken geçici `--allow-warnings` kullanılabilir; teslim kapısında kullanmamak. Uygun projede ayrıca `npm ci`, typecheck/manifest doğrulaması, UI5 Linter, production build, QUnit, OPA5/wdi5/Playwright, UI5 Support Assistant ve browser console çalıştırmak. Sadece çıkış koduna güvenmemek; keşfedilen test sayısını, uygulamayı ve PNG'yi gözle incelemek.

Karşıt test yapmak:

- Uzun çeviri ve RTL
- Sıfır kayıt, binlerce kayıt ve geciken servis
- Yetkisiz eylem, backend validation hatası ve concurrency/draft çakışması
- Klavye-only ve görünür odak
- S/M/L/XL, cozy/compact, Morning/Evening/HCB/HCW
- PNG/prototip/kod arasında aynı alan, eylem, durum ve öncelik

İki kez aynı doğrulama hatasına yama uygulanırsa varsayımı yeniden test etmek.

### 9. Kalibre teslim et

Önce sonucu vermek. Ardından yalnız karar için gerekli kanıtı sunmak:

- Dosya bağlantıları: PNG, interaktif prototip, kaynak kod ve `design-contract.json`
- Seçilen floorplan/framework ve kısa gerekçe
- Hedef/varsayılan UI5 ve Fiori guideline sürümü
- Çalıştırılan testler ve gözlenen sonuçlar
- Doğrulanamayan varsayımlar ve kalan gerçek riskler
- Gereksinim → tasarım → kod → test izlenebilirliği

Bir dosya üretilmiş ama açılıp incelenmemişse bitmiş saymamak. Sağlanmayan bir dosyayı, çalıştırılmayan testi veya görülmeyen runtime değerini gözlenmiş kanıt gibi raporlamamak.

## Hazır kaynaklar

- `assets/design-contract.template.json` ve `assets/design-contract.schema.json`: görsel ile kodu bağlayan sözleşme ve makine-okunur şeması.
- `assets/abap-backend-contract.schema.json`: paket envanteri ile RAP/OData/UI kanıtının şeması.
- `assets/version-profiles.json`: yeni proje için birlikte doğrulanmış, exact-pinned UI5/tooling profil kümesi ve `defaultProfile`. Şablon lockfile'ları bu profile aittir; yeni profil eklerken lockfile'ı o profille yeniden üretmek.
- `assets/ui5-prototype/`: yalnız interaktif tasarım için mock verili prototip.
- `assets/ui5-production-freestyle/`: TypeScript, UI5 CLI/Linter, QUnit, OPA5 ve tarayıcı kalite kapılı üretim iskeleti.
- `assets/ui5-production-fiori-elements/`: OData V4 List Report/Object Page ve tarayıcı smoke testli metadata-first iskelet.
- `scripts/scaffold_fiori_workspace.py`: çıktı tipine göre prototip ile üretim projesini ayrı ve güvenli biçimde oluşturur.
- `scripts/inspect_abap_package.py`: yerel paket/ZIP veya salt-okunur ADT snapshot'ından backend sözleşmesi üretir.
- `scripts/validate_fiori_delivery.py`: strict JSON, sözleşme-kod semantiği, proje yapısı ve riskleri fail-closed denetler.
- `tests/test_skill_tools.py`: üç betiğin davranış testleri; betik veya şablon değiştiğinde `python -B "<skill kökü>/tests/test_skill_tools.py"` ile çalıştırmak.

Şablonları kör kopyalamamak; hedef sürüm ve mevcut proje yapısına uyarlamak.
