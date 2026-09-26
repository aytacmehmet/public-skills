# SAP Fiori Tasarım

[Türkçe katalog](../README.md) · [English: SAP Fiori Design](../../en/sap-fiori-design/README.md)

SAP Fiori for Web ekranını iş görevinden başlayarak tasarlar; aynı tasarımı gerçek SAPUI5 kontrolleriyle çalışan prototipe, PNG'ye ve üretim koduna dönüştürür. ABAP paketi verildiğinde CDS/RAP/servis kaynaklarını okuyup UI'ı o sözleşmeye bağlar. Görmediğini doğrulanmış saymaz: her varsayım, boşluk ve sürüm bilgisi sözleşmede `verified`, `assumed` veya `unknown` olarak kalır.

Bu public paket, bakımı süren bağımsız sürümdür. Yazarın özel geliştirme deposu kendi kopyasını özel bir plugin lehine emekliye ayırdı; orada görülen 2.0.0 bir yönlendirmedir, bu skill değildir.

## Diller ve kurulum

Bu paketin tanıtımı, değişiklik geçmişi ve arayüz bilgileri Türkçedir. `SKILL.md` ve `references/` modele dönük dosyalardır: İngilizce yazılır ve [İngilizce paketle](../../en/sap-fiori-design/README.md) bayt düzeyinde aynıdır (yalnız frontmatter'daki ad, dil ve karşılık farklıdır); skill kullanıcıya kullanıcının dilinde cevap verir. Betikler, testler, şemalar ve UI5 şablonları da iki pakette aynıdır; betik mesajları, bulgu kodları ve sözleşme anahtarları İngilizcedir. `--language tr|en` prototipin mock verisini ve üretilen `index.html` dil özniteliğini seçer; i18n paketleri her iki dilde gelir.

Skill Installer kullanılabiliyorsa:

```text
$skill-installer https://github.com/aytacmehmet/public-skills/tree/main/tr/sap-fiori-tasarim adresindeki skill'i kur.
```

Alternatif olarak yalnız bu skill klasörünü ortamınızın desteklediği skill keşif konumuna kopyalayın. Uygun konum için [resmî skill belgesine](https://learn.chatgpt.com/docs/build-skills) bakın. Değiştirmeden önce mevcut kurulumu koruyun ve skill'in seçim listesinde göründüğünü doğrulayın. Türkçe ve İngilizce paketi aynı anda kurmayın; aynı işi iki farklı adla tetiklerler.

Betikler yalnız Python 3.12+ standart kütüphanesini kullanır. Üretim şablonları Node.js `^20.11.0 || >=22` ve npm 10+ ister; bağımlılıklar `assets/version-profiles.json` içindeki profile tam sürümle sabitlenmiştir.

## Kullanım

```text
$sap-fiori-tasarim Satış siparişi onayı için List Report + Object Page tasarla; PNG ve interaktif prototip üret. Hedef sistem S/4HANA Cloud Public Edition.
```

```text
$sap-fiori-tasarim ./abapgit-export klasöründeki ABAP paketini incele, backend sözleşmesini çıkar ve buna uygun Fiori elements uygulamasını üret. Servis URI'si: /sap/opu/odata4/...; hedef SAPUI5 runtime 1.152.1.
```

```text
$sap-fiori-tasarim Mevcut webapp/ projesini Fiori rehberine, erişilebilirliğe ve deprecated API kullanımına göre incele; bulguları dosya ve satırla raporla. Dosya değiştirme.
```

## Nasıl çalışır?

```text
gereksinim ─┐
            ├─> abap-backend-contract.json ─> design-contract.json ─┬─> prototype/   (mock verili, çalışan UI5)
ABAP paketi ┘      (inspect_abap_package)     (scaffold_fiori_…)    ├─> visuals/*.png (prototipten alınır)
                                                                    └─> app/          (TypeScript veya Fiori elements V4)
                                          validate_fiori_delivery: şema, hash zinciri, sözleşme ↔ manifest, riskli kalıplar
```

- **Backend sözleşmesi:** `--metadata` verilirse gözlenen servis `$metadata`'sındaki her entity set'i ve beyan edilmiş `$search` desteğini de kaydeder. Yerel ADT/abapGit klasörü, ZIP veya salt-okunur ADT snapshot'ından entity, alan, anahtar, association, draft, action, validation, yetki ve servis sınırını çıkarır. Okuyamadığı elementi, birden fazla servis veya entity set adayını tahmin etmez; `gaps` içine yazar.
- **Tasarım sözleşmesi:** PNG, prototip ve kodun tek kaynağıdır; sayfa, alan, eylem, durum, responsive davranış, erişilebilirlik ve gereksinim → kontrol → backend nesnesi → test izlenebilirliğini taşır.
- **Artımlı çalışma alanı:** sözleşme bir kez oluşur; prototipten koda geçerken aynı klasörde `--output all` çalıştırılır ve tasarımcının doldurduğu sözleşme korunur. `--force` yalnız scaffold ağaçlarını yeniler.
- **Sürüm ayrımı:** `--ui5-version` yalnız scaffold profilini (tooling ve `minUI5Version`) seçer. Hedef sistemde gözlenen runtime `--target-ui5-runtime` ile verilir; verilmezse `unknown` kalır; kod tesliminde kapı kapalı durur, yalnız prototip/PNG tesliminde bilgi notudur.
- **Doğrulayıcı:** `error` ve `warning` kapıyı kapatır, `info` kapatmaz. Kapı biçimle yetinmez: sözleşmede kalan şablon metni, UI'da karşılığı olmayan metin anahtarı veya eylem, boş erişilebilirlik kanıtı doğrulanmamış `$search`/FLP inbound'u, verilen `$metadata`'nın reddettiği arama iddiası ve kaydedilmemiş veya değişmiş yakalamalar da bulgudur. `--allow-warnings` yalnız tasarım sürerken kullanılır; `--review` sözleşmesi olmayan mevcut projeyi inceler; proje kurallarını (Manifest V2, locale, density) uyarı olarak bildirir ve yalnız gerçek kusurda başarısız olur.
- **Prototip durumları:** `prototype/index.html?state=initial|loading|populated|empty|no-results|error|no-auth` tasarlanan her durumu yeniden üretir; PNG'ler bu adreslerden alınır ve `record_captures.py` ile kaydedilir; oluşamayacak zorunlu bir durum atılmak yerine gerekçesiyle `stateExceptions` listesine yazılır.

## Doğrulama ve sınırlar

```text
python -B tests/test_skill_tools.py
```

Testler scaffold girdilerini ve artımlı çalıştırmayı, teslim kapısının şablon metnini reddedip tamamlanmış sözleşmeyi geçirmesini, sözleşme ↔ UI eşlemesini, inceleme modunu, ABAP paket okumayı (abapGit/ADT service binding biçimleri, çok entity'li behavior definition, satır içi annotation'lı element listesi), `$metadata` arama desteğini, durum istisnalarını, kayıtlı yakalamaları, inceleme modundaki açık handler'ları, ZIP yol güvenliğini, hash bütünlüğünü, şema zorlamasını ve sürüm denetimini kapsar.

Inspector lexical bir okuyucudur; ABAP derleyicisi, ADT aktivasyonu, service preview veya çalışma zamanı yetki kanıtı değildir. `ready` sonucu gerçek `$metadata`, hedef release ve released-object doğrulamasının yerine geçmez. Statik doğrulayıcı build, test, tarayıcı render'ı ve gözle incelemenin yerini tutmaz. Skill SAP sistemine yazmaz, aktivasyon, transport veya deploy yapmaz; sohbette parola veya anahtar istemez. `references/official-sources.md` içindeki sürüm notları araştırma tarihine aittir; hedef sürümü canlı kaynaktan doğrulayın.

## Dosyalar ve sürümler

- [SKILL.md](SKILL.md): emir kipinde, XML bölümlü yönerge — değişmez kurallar, referans yönlendirmesi, kapsam alanları, kanıt, sözleşme, mimari, prototip, üretim, doğrulama, öz-kontrol ve teslim — ve sürüm bilgileri.
- [Arayüz bilgileri](agents/openai.yaml): görünen ad, açıklama ve hazır çağrı.
- Çalışma zamanında yalnız gerektiğinde okunan alan referansları: [tasarım temelleri](references/design-foundations.md), [floorplan ve pattern'ler](references/floorplans-and-patterns.md), [UI5 mühendisliği](references/ui5-engineering.md), [ABAP paketi okuma](references/abap-package-intake.md), [RAP backend sözleşmesi](references/rap-backend-contract.md), [teslim ve kalite](references/delivery-and-quality.md), [resmî kaynaklar](references/official-sources.md).
- [Davranış kontrolleri](references/behavior-checks.md): FD01–FD36 bakım senaryolarıdır; tüm senaryoların her ortamda geçtiği iddiası değildir. Çalışma zamanında okunmaz.
- [Kaynak ve tasarım notları](references/source-notes.md): dayanaklar, yapı tercihleri ve sınırlar. Çalışma zamanında okunmaz.
- `scripts/`, `assets/`, `tests/`: iki dilde bayt düzeyinde aynı betikler, şemalar, UI5 şablonları ve betik testleri.
- [Değişiklik geçmişi](CHANGELOG.md) ve [arşivlenmiş sürümler](archived/README.md).
- [GPL-3.0 lisansı](LICENSE).

Güncel sürüm 2.0.0'dır ve `latest/` veya sürüm numaralı bir alt klasörde değil, doğrudan burada bulunur. Önceki yayımlanmış sürümler, deponun [sürüm yönetimi talimatlarına](../CONTRIBUTING.md) göre `archived/` içinde değiştirilmeyen ZIP kopyaları olarak saklanır. Bu ZIP'leri skill keşfi yapılan bir dizinin içinde açmayın.
