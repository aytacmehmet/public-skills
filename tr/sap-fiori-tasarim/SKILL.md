---
name: sap-fiori-tasarim
description: "Resmî SAP Design System ve SAPUI5 rehberlerine dayalı uçtan uca SAP Fiori for Web tasarım ve geliştirme becerisi. SAP Fiori, SAPUI5/UI5, Fiori elements, mockup/prototip/PNG, List Report, Object Page, OData/RAP veya S/4HANA ekranı tasarlamak, incelemek, kodlamak ya da refactor etmek; ayrıca yerel ADT/abapGit paketi, ZIP veya yapılandırılmış salt-okunur ADT bağlantısından ABAP paketini okuyup UI'ı CDS/RAP/servis sözleşmesine göre üretmek istendiğinde kullan. Görsel tasarım, backend kanıtı ve üretim kodunu izlenebilir sözleşmelerle bağlar; hedef sürüm, erişilebilirlik, performans, güvenlik ve Clean Core kapıları uygular."
metadata:
  version: "1.2.0"
  language: "tr"
  family: "sap-fiori-design"
  counterpart: "en/sap-fiori-design"
---

# SAP Fiori Tasarım

Ekranı önce iş görevi ve hedef sistem bağlamında tasarla; sonra aynı tasarımı gerçek SAPUI5 kontrolleriyle prototipe ve üretim koduna dönüştür. Görsel kaliteyi SAP standardından, teknik kaliteyi hedef çalışma zamanından ve doğrulanabilir kalite kapılarından türet. Kullanıcıyla onun dilinde konuş; varsayılan Türkçe. Kullanıcının talimatı bu yönergeden önceliklidir.

<invariants>
1. Tasarım ve kodun tek kaynağı `design-contract.json`'dır. PNG, prototip ve üretim kodundaki her sayfa, alan, eylem, durum ve responsive davranışı bu sözleşmeyle eşle; sözleşmedeki her metin anahtarı ve eylem kimliği teslim edilen UI'da bulunmalıdır.
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
12. Sözleşmede şablon metni (`Replace …`, `pending-…`, `YYYY-MM-DD`) bırakma ve kapıyı geçmek için uydurma değer yazma. Bilmediğini `unknown`, ilerlemeyi durduranı `blocked` olarak kaydet.

- Kötü: şablon manifest'inde `minUI5Version: 1.151.0` var → "Hedef sistem SAPUI5 1.151.0" diye raporlamak.
- İyi: `ui5Runtime: unknown` bırak; "1.151.0 yalnız scaffold profilidir, runtime'ı hedef sistemde doğrulayın" de.
</invariants>

<references>
İş başlamadan yalnız gereken dosyayı oku:

| Konu | Dosya |
|---|---|
| Görsel dil, tema, token, tipografi, ikon, yoğunluk, erişilebilirlik | [design-foundations.md](references/design-foundations.md) |
| Floorplan, kontrol ve durum kararları | [floorplans-and-patterns.md](references/floorplans-and-patterns.md) |
| SAPUI5/Fiori elements proje ve kod kuralları, kod üretim guardrail'leri | [ui5-engineering.md](references/ui5-engineering.md) |
| ABAP paketi/ZIP/ADT snapshot okuma, inspector çıktısı, backend → UI eşlemesi | [abap-package-intake.md](references/abap-package-intake.md) |
| RAP, OData V4, ABAP Cloud ve Clean Core veri sözleşmesi | [rap-backend-contract.md](references/rap-backend-contract.md) |
| Teslim biçimleri, doğrulayıcı bulguları, doğrulama matrisi | [delivery-and-quality.md](references/delivery-and-quality.md) |
| Canlı doğrulanacak resmî bağlantılar ve sürüm notu | [official-sources.md](references/official-sources.md) |

`references/behavior-checks.md` ve `references/source-notes.md` yalnız skill bakımı içindir; çalışma zamanında okuma.

Komutlardaki `<skill kökü>`, host'un bu skill için bildirdiği taban dizindir. Betikleri `python -B "<skill kökü>/scripts/<ad>.py"` biçiminde çalıştır; her betik `--help` ile tüm bayraklarını listeler. Git Bash'te `/` ile başlayan servis URI'si yola çevrilir; PowerShell kullan veya komutun başına `MSYS_NO_PATHCONV=1` koy.

Belirli bir UI öğesi veya floorplan için ayrıntı gerekiyorsa resmî, hedef sürümlü SAP sayfasını ayrıca aç. UI5 Demo Kit örneği tek başına Fiori tasarım kanıtı değildir.
</references>

<scope>
Sohbet, mevcut dosyalar, servis metadata'sı, ekran görüntüleri ve gereksinimlerden şu alanları doldur; bilinmeyeni `unknown` yaz, uydurma:

`Rol ve görev` (kullanıcı rolü, karar/görev, başarı ölçütü) · `İş nesnesi` (ana nesne, alt nesneler, statüler, eylemler) · `Hedef sistem` (S/4HANA Cloud Public/Private, on-premise, BTP veya bağımsız UI5; FLP ise semantic object ve action) · `Sürüm ve protokol` (SAPUI5 runtime, Fiori guideline sürümü, OData V2/V4, RAP, draft) · `Proje` (mevcut mi yeni mi; Fiori elements, freestyle veya bilinmiyor) · `Cihaz ve dil` (birincil cihazlar, dil/RTL, tema/markalama, erişilebilirlik hedefi) · `Çıktı` (`png`, `interactive`, `png+interactive`, `code`, `all` veya `review`) · `Sınırlar` (test, dağıtım, teslim).

Bağlamda olanı yeniden sorma. Sonucu değiştirecek tek büyük eksik varsa tek kısa soru sor; değilse varsayımı sözleşmeye kaydet ve devam et. Görsel format söylenmemişse `png+interactive` varsay.

| Çıktı | Üretilen | Ön koşul | Hedef `unknown` ise |
|---|---|---|---|
| `png` / `png+interactive` | `prototype/` + `visuals/*.png` | Yok; PNG gerçek tarayıcı capture'ıdır | Bilgi notu; kapı açılabilir |
| `interactive` | `prototype/` | Yok | Bilgi notu; kapı açılabilir |
| `code` / `all` | `app/` (prototipten bağımsız) | Framework, gözden geçirilmiş `--ui5-version` profili, gözlenmiş servis URI'si ve entity set | Uyarı; kapı kapalı kalır |
| `review` | Bulgu raporu; dosya üretilmez | Kapsama alınmış mevcut proje | — |
</scope>

<evidence>
- **Mevcut proje:** kullanıcı kapsam içine koyduysa önce `package.json`, `ui5.yaml`, `manifest.json`, `Component.*`, view/fragment/controller, annotation/CDS kaynakları, testler ve servis metadata'sını oku. Proje verilmediyse ilgisiz çalışma alanını hedef proje gibi inceleme. `minUI5Version` ile gerçek runtime farkını kontrol et.
- **ABAP paketi** (ADT export'u, abapGit klasörü/ZIP'i veya canlı paket adı): önce [abap-package-intake.md](references/abap-package-intake.md) dosyasını oku, sonra:

```powershell
python -B "<skill kökü>/scripts/inspect_abap_package.py" <paket-klasörü-veya-zip> `
  --output <çıktı>/abap-backend-contract.json `
  --package-name <paket> --service-uri <gözlenen-uri> --protocol odata-v4
```

- **Seçim inspector'ın değil kanıtındır:** birden fazla service definition varsa inspector yalnız okunabilen service binding'lerin hepsi aynı tanımı gösteriyorsa onu seçer; aksi halde `gaps` içine yazar. UI servisini `--service-definition`, ana entity set'i `--entity-set` ile kanıta dayanarak adlandır.
- **Canlı sistem:** yalnız salt-okunur ADT araçları (örneğin `sap-cloud-erp` MCP sunucusu) mevcut ve bağlantı önceden yapılandırılmışsa tüm paket sayfalarını ve gerekli active kaynak sayfalarını SHA-bağlı oku, normalleştirilmiş ADT snapshot oluştur, aynı inspector'a ver. Araç yoksa yerel export iste ve blocker olarak kaydet. Paket adından nesne veya servis URI'si tahmin etme.
- **Sözleşmeye aktar:** `uiSemantics` altındaki alan rollerini (`lineItemFields`, `selectionFields`, `valueHelpFields`, `hiddenFields`, …), draft, action, validation, side effect, DCL ve service exposure kanıtlarını tasarım sözleşmesine taşı. `gaps` çözülmeden veya açık blocker/varsayım yazılmadan üretim koduna geçme. `unparsedElements` ile `dynamicFeatureControl` altındakileri gerçek `$metadata` ile doğrula; `draftActions` listesini iş action'ı olarak tasarlama; `searchableEntities` içinde olmayan entity'ye `$search` gönderme. Parser sonucu compiler/activation/service preview kanıtı değildir; yerel export'un eksiksizliği sağlayanın beyanıdır (`inventoryVerified: false`).
- **Sürümü kilitle:** hedef sürüm bilinmiyorsa üretim kodu scaffold etme; yalnız prototip veya sözleşme üret ve sürümü `unknown` bırak. `--ui5-version` yalnız scaffold profilini (tooling ve `minUI5Version`) seçer; hedef sistemde gözlenen runtime `--target-ui5-runtime` ile ayrıca verilir. Profil gözlenen runtime'dan yeniyse veya kendi lockfile'ı yoksa scaffold reddeder; o runtime için gözden geçirilmiş yeni profil ekle.
- **Canlı doğrulama:** internet varsa [official-sources.md](references/official-sources.md) üzerinden resmî dokümanı aç. Bu turda sayfayı gerçekten açıp sürüm göstergesini görmeden "gözlendi/doğrulandı" deme; statik araştırma notu yalnız arama ipucudur. Fiori guideline sürümü ile SAPUI5 runtime sürümünü ayrı alanlarda, tam değer + URL + kontrol tarihiyle kaydet.

- Kötü: pakette `Z_UI_ORDER` ve `Z_API_ORDER` var, binding okunamıyor → ilkini seçip manifest'e yazmak.
- İyi: `gaps` satırını göster, UI servisini kaynaktan belirle, `--service-definition Z_UI_ORDER` ile yeniden çalıştır.
</evidence>

<contract>
Çalışma alanını oluştur veya genişlet:

```powershell
python -B "<skill kökü>/scripts/scaffold_fiori_workspace.py" <çıktı> --app-id <ad.alanı> --name <ad> `
  --language <tr|en> --output <tip> [--backend-contract <çıktı>/abap-backend-contract.json] `
  [--semantic-object <nesne> --action <eylem>]
```

Var olan `design-contract.json` tasarımcının emeğidir: sonraki çalıştırma (örneğin prototipten sonra `--output all`) sözleşmeyi korur, yalnız eksik ağacı ve scaffold'a ait alanları ekler. `--force` yalnız `prototype/` ve `app/` dosyalarını yeniler; sözleşmeyi baştan başlatmak için `--reset-contract` gerekir ve eski dosya `.bak` olarak saklanır. Şemalar skill'e aittir ve her çalıştırmada yenilenir; şablon alanlarının türünü geçici cevap için değiştirme, yeni ihtiyaçta şemayı ve doğrulayıcıyı aynı değişiklikte güncelle.

Şu alanların hepsini doldur:

- `context`: rol, görev, nesne, sistem, sürüm, FLP ise `launchIntent`; `context.evidence[].status` yalnız `verified`, `assumed`, `unknown` veya `blocked`
- `architecture`: floorplan, framework, gerekçe, reddedilen alternatifler; üretim kodunda `minUI5Version`
- `informationArchitecture`: sayfalar, bölümler, navigasyon, öncelik
- `fieldsAndActions`: alan semantiği, zorunluluk, value help, eylem yeri ve yetki; her `labelKey`/`titleKey` i18n'de, her eylem `id`'si view'da aynı stabil ID ile bulunur
- `states`: `initial`, `loading`, `populated`, `empty`, `no-results`, `error`, `no-auth` ve ilgili edit/draft durumları; `verification.states` aynı listeyi taşır
- `responsive`: S/M/L/XL davranışı, cozy/compact, tablonun telefon alternatifi
- `accessibility`: başlık hiyerarşisi, etiketler, klavye/odak, ARIA ilişkileri, metin alternatifleri
- `dataContract`: entity, navigation, action/function, `initialSelect`, dar `$expand`, paging, side effects, `serverCapabilities.search`, `releasedApisVerified`
- `backendEvidence`: ABAP sözleşmesi yolu/hash'i, paket, kaynak modu, bütünlük, aktif sürüm, açık boşluklar
- `verification`: komutlar ve gerçekten sınananı `check`/`method`/`result` ile yazan `accessibilityEvidence`
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

List/filter/drill-down için List Report + Object Page'i; analitik filtre-grafik-tablo işi için Analytical List Page'i; gerçek list-detail(-detail) akışı için Flexible Column Layout'u değerlendir. Seçimi görünüşe göre değil görev, veri hacmi, düzenleme akışı, cihaz ve backend kabiliyetine göre yap. Inspector'ın `recommendation.framework` değeri öneridir; gerekçeli freestyle kararı ondan ayrılabilir ve reddedilen alternatif sözleşmeye yazılır. Ayrıntı: [floorplans-and-patterns.md](references/floorplans-and-patterns.md), [ui5-engineering.md](references/ui5-engineering.md).
</architecture>

<prototype>
`--output interactive` ile `assets/ui5-prototype/` iskeletini ayrı `prototype/` klasörüne üret veya mevcut uygulamayı prototip olarak kullan. Bu şablonu üretim kodu diye teslim etme. Gerçek SAPUI5 kontrolleri, sabitlenmiş prototip runtime'ı (CDN; çevrimdışı çalışmaz), Horizon tema ve dile göre seçilen mock veriyle çalışan akış kur.

- Shell ile uygulama içeriğini ayır; üretim app içinde FLP shell'i tekrar etme.
- Kritik akışları çalıştır: filtreleme, seçim, navigasyon, create/edit/save/cancel, doğrulama, dialog ve mesajlar. Dialog'u fragment olarak yükle; alan hatasını `valueState` ile alanın üzerinde göster ve odağı ilk hatalı alana taşı.
- Tasarlanan her durumu `?state=loading|empty|no-results|error|no-auth` ile yeniden üretilebilir kıl; şablon bu anahtarı taşır, yeni durum eklersen genişlet.
- Sabit piksel yerleşimi yerine UI5 responsive kontrol ve layout'larını kullan.
- Gerçek kullanıcı verisine veya üretim servisine bağlanma; mock veri kullan.
- Kontrol metinlerini i18n kaynağına koy; örnekte dahi locale duyarlı sayı/tarih/birim göster.

**PNG:** prototipi gerçek tarayıcıda aç, yüklenme bitince incele ve ekran görüntüsü al. En az birincil hedef görünümü teslim et; kalite kontrolü için S/M/L/XL sınıflarını örnekle. Dosya adı `<app>-<ekran>-<durum>-<S|M|L|XL>-<tema>-<cozy|compact>.png` biçimindedir ve `<durum>` sözleşmedeki bir durum kimliğidir. PNG ile prototip birlikte istendiyse aynı build ve aynı veri durumunu kullan; ikisini elle ayrı tasarlama.
</prototype>

<production>
Mevcut projede yerel stile uy. Yeni scaffold'da framework, UI5 profili, servis protokolü/URI'si ve entity set kullanıcı kanıtından veya doğrulanmış `abap-backend-contract.json` dosyasından gelmeden ilerleme. `--output code`, `app/` altında prototipten bağımsız proje oluşturur. Yeni scaffold yalnız OData V4 üretir; mevcut OData V2 uygulamayı okuyup korur fakat V4 şablonuyla taklit etmez. Yeni freestyle uygulamada TypeScript kullan; mevcut JavaScript projeyi gerekçesiz toplu migration'a zorlama.

Kod yazmadan önce [ui5-engineering.md](references/ui5-engineering.md) dosyasını oku ve 11. bölümdeki guardrail'leri hata say. Şablonların taşıdığı sözleşmeyi koru:

- Manifest-first, asenkron bootstrap, Manifest V2 hedefinde kaldırılmış `async` alanı yok; tam sabitlenmiş tooling ve güncel lockfile.
- Freestyle: deep-link'lenebilir ayrıntı route'u (anahtar hash'te kodlanır, yalnız key predicate kabul edilir), `bypassed` → not-found hedefi, stabil ID, i18n, server-side filtre/sort/page. `$search` yalnız `serverCapabilities.search: true` ise kalır; değilse `$filter` ile değiştir.
- Fiori elements: annotation/config ile çöz; `webapp/annotations/annotation.xml` yalnız doğrulanmış, UI'ya özgü ihtiyaç içindir; extension kodunu yalnız belgelenmiş extension point'e koy.
- FLP: `--semantic-object`/`--action` manifest'e inbound ekler; intent'i hedef katalogla doğrulamadan `verified` yazma.
- Tema parametreleri ve layout sınıfları; hard-coded renk/font/gölge/radius, dinamik HTML, frontend'de güvenlik kararı yok.
- QUnit, OPA5 (liste → ayrıntı ve not-found yolculukları dahil), sıfır-test denetimi; kapsam uygunsa wdi5/Playwright uçtan uca testleri.

Backend tasarımı veya UI annotation gerekiyorsa [rap-backend-contract.md](references/rap-backend-contract.md) kurallarını uygula. SAP API/nesnesinin release durumunu canlı sistemde doğrulamadan "released" deme.
</production>

<verification>
Önce teslim tipine göre [delivery-and-quality.md](references/delivery-and-quality.md) matrisini uygula, sonra statik denetimi çalıştır:

```powershell
python -B "<skill kökü>/scripts/validate_fiori_delivery.py" <çıktı-klasörü> --contract <çıktı-klasörü>/design-contract.json
```

Doğrulayıcı üç önem düzeyi kullanır: `error` ve `warning` kapıyı kapatır, `info` kapatmaz. `--allow-warnings` yalnız tasarım sürerken geçicidir; teslim kapısında kullanma. Kapı biçimle yetinmez: şablon metni, eksik durum, UI'da karşılığı olmayan metin anahtarı veya eylem, boş erişilebilirlik kanıtı, doğrulanmamış `$search`/FLP inbound'u/released durumu ve sürüm uyumsuzluğu da bulgudur. Her bulgu kodunun anlamı ve çözümü [delivery-and-quality.md](references/delivery-and-quality.md) 10. bölümdedir; bulguyu uydurma değerle susturma.

Uygun projede ayrıca `npm ci`, typecheck/manifest doğrulaması, UI5 Linter, production build, QUnit, OPA5/wdi5/Playwright, UI5 Support Assistant ve browser console çalıştır. Yalnız çıkış koduna güvenme: keşfedilen test sayısını oku, uygulamayı ve PNG'yi gözle incele.

Karşıt test yap: uzun çeviri ve RTL · sıfır kayıt, binlerce kayıt, geciken servis · yetkisiz eylem, backend validation hatası, concurrency/draft çakışması · klavye-only ve görünür odak · S/M/L/XL, cozy/compact, Morning/Evening/HCB/HCW · PNG/prototip/kod arasında aynı alan, eylem, durum ve öncelik.

Aynı doğrulama hatasına iki kez yama uyguladıysan yamayı bırak, varsayımı yeniden test et.
</verification>

<review>
Mevcut bir uygulamayı incelemen istendiyse tasarım akışını başlatma ve dosya değiştirme:

```powershell
python -B "<skill kökü>/scripts/validate_fiori_delivery.py" <proje-kökü> --review
```

`--review` sözleşme istemez; manifest, view, controller ve stil dosyalarını tarar ve yalnız `error` bulgusunda başarısız olur. Betik yalnız statik kalıpları görür; üstüne projeyi `<evidence>` sırasıyla oku ve floorplan uygunluğu, eylem yerleşimi, durumlar, erişilebilirlik, i18n, OData kullanımı ve yetki varsayımlarını ilgili referansa göre değerlendir. Her bulguyu şu biçimde ver, önem sırasıyla:

`dosya:satır` · `engelleyici | önemli | öneri` · kural ve kaynağı (referans bölümü veya resmî sayfa) · gözlem · önerilen değişiklik

Görmediğin runtime, servis veya ekran davranışını bulgu olarak yazma; "doğrulanamadı" başlığında topla. Düzeltme yalnız kullanıcı isterse yapılır ve projenin kendi stiline uyar.
</review>

<self_check>
"Bitti" demeden önce: her dosyayı yeniden açtın · script/build/test çıktısını okudun · uygulamayı ve PNG'yi gördün · ilk, son ve en tuhaf senaryoyu örnekledin · sözleşmede şablon metni kalmadığını gördün · sonucu asıl istekle karşılaştırdın. Üretilmiş ama açılıp incelenmemiş dosya bitmiş değildir.
</self_check>

<delivery>
Önce sonucu ver, sonra yalnız karar için gereken kanıtı; süreç anlatımı yok:

1. Dosya bağlantıları: PNG, interaktif prototip, kaynak kod, `design-contract.json`
2. Seçilen floorplan/framework ve tek cümle gerekçe
3. Hedef ve scaffold UI5 sürümü, Fiori guideline sürümü — ayrı ayrı
4. Çalıştırılan testler ve gözlenen sonuçlar; doğrulayıcının `error`/`warning`/`info` sayıları
5. Doğrulanamayan varsayımlar, açık `gaps` ve kalan gerçek riskler
6. Gereksinim → tasarım → kod → test izlenebilirliği

Sağlanmayan dosyayı, çalıştırılmayan testi veya görülmeyen runtime değerini gözlenmiş kanıt gibi raporlama. Niyeti değil gözlemi bildir.
</delivery>

<resources>
`assets/`: sözleşme şablonu ve iki şema, `version-profiles.json` (profiller, `defaultProfile`, şablon lockfile'ının ait olduğu `templateLockfileProfile`, profil başına `lockfileDir`), prototip ve iki üretim iskeleti. `scripts/`: `inspect_abap_package.py`, `scaffold_fiori_workspace.py`, `validate_fiori_delivery.py`. `tests/test_skill_tools.py`: betik ve şablon değişince `python -B "<skill kökü>/tests/test_skill_tools.py"` ile çalıştır. Şablonları kör kopyalama; hedef sürüme ve mevcut proje yapısına uyarla.
</resources>
