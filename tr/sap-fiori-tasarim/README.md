# SAP Fiori Tasarım

[Türkçe katalog](../README.md) · [English: SAP Fiori Design](../../en/sap-fiori-design/README.md)

SAP Fiori for Web ekranını iş görevinden başlayarak tasarlar; aynı tasarımı gerçek SAPUI5 kontrolleriyle çalışan prototipe, PNG'ye ve üretim koduna dönüştürür. ABAP paketi verildiğinde CDS/RAP/servis kaynaklarını okuyup UI'ı o sözleşmeye bağlar. Görmediğini doğrulanmış saymaz: her varsayım, boşluk ve sürüm bilgisi sözleşmede `verified`, `assumed` veya `unknown` olarak kalır.

## Diller ve kurulum

Bu paketin yönergeleri ve referansları Türkçedir. [İngilizce karşılığı](../../en/sap-fiori-design/README.md) aynı davranışı İngilizce yönergelerle sunar. Betikler, testler, şemalar ve UI5 şablonları iki pakette bayt düzeyinde aynıdır; betik mesajları, bulgu kodları ve sözleşme anahtarları bilinçli olarak İngilizcedir. Üretilen uygulamanın dili `--language tr|en` ile seçilir.

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
$sap-fiori-tasarim Mevcut webapp/ projesini Fiori rehberine, erişilebilirliğe ve deprecated API kullanımına göre incele; bulguları dosya ve satırla raporla.
```

## Nasıl çalışır?

```text
gereksinim ─┐
            ├─> abap-backend-contract.json ─> design-contract.json ─┬─> prototype/   (mock verili, çalışan UI5)
ABAP paketi ┘      (inspect_abap_package)     (scaffold_fiori_…)    ├─> visuals/*.png (prototipten alınır)
                                                                    └─> app/          (TypeScript veya Fiori elements V4)
                                          validate_fiori_delivery: şema, hash zinciri, sözleşme ↔ manifest, riskli kalıplar
```

- **Backend sözleşmesi:** yerel ADT/abapGit klasörü, ZIP veya salt-okunur ADT snapshot'ından entity, alan, anahtar, association, draft, action, validation, yetki ve servis sınırını çıkarır. Okuyamadığı elementi, birden fazla servis veya entity set adayını tahmin etmez; `gaps` içine yazar.
- **Tasarım sözleşmesi:** PNG, prototip ve kodun tek kaynağıdır; sayfa, alan, eylem, durum, responsive davranış, erişilebilirlik ve gereksinim → kontrol → backend nesnesi → test izlenebilirliğini taşır.
- **Sürüm ayrımı:** `--ui5-version` yalnız scaffold profilini (tooling ve `minUI5Version`) seçer. Hedef sistemde gözlenen runtime `--target-ui5-runtime` ile verilir; verilmezse `unknown` kalır ve teslim kapısı kapalı durur.
- **Doğrulayıcı:** uyarıda da başarısız olur. `--allow-warnings` yalnız tasarım sürerken kullanılır.

## Doğrulama ve sınırlar

```text
python -B tests/test_skill_tools.py
```

Testler scaffold girdilerini, ABAP paket okumayı (abapGit/ADT service binding biçimleri, çok entity'li behavior definition, satır içi annotation'lı element listesi), ZIP yol güvenliğini, hash bütünlüğünü, şema zorlamasını ve sürüm denetimini kapsar.

Inspector lexical bir okuyucudur; ABAP derleyicisi, ADT aktivasyonu, service preview veya çalışma zamanı yetki kanıtı değildir. `ready` sonucu gerçek `$metadata`, hedef release ve released-object doğrulamasının yerine geçmez. Statik doğrulayıcı build, test, tarayıcı render'ı ve gözle incelemenin yerini tutmaz. Skill SAP sistemine yazmaz, aktivasyon, transport veya deploy yapmaz; sohbette parola veya anahtar istemez. `references/official-sources.md` içindeki sürüm notları araştırma tarihine aittir; hedef sürümü canlı kaynaktan doğrulayın.

## Paket

[Yönerge](SKILL.md) · [Tasarım temelleri](references/design-foundations.md) · [Floorplan ve pattern'ler](references/floorplans-and-patterns.md) · [UI5 mühendisliği](references/ui5-engineering.md) · [ABAP paketi okuma](references/abap-package-intake.md) · [RAP backend sözleşmesi](references/rap-backend-contract.md) · [Teslim ve kalite](references/delivery-and-quality.md) · [Resmî kaynaklar](references/official-sources.md) · [Değişiklik geçmişi](CHANGELOG.md) · [Arşivler](archived/README.md) · [GPL-3.0 lisansı](LICENSE)

Bu, 1.0.0 sürümlü ilk herkese açık yayındır. Güncel dosyalar paket kökünde bulunur. Sonraki güncellemelerde önceki commit'li sürüm, deponun [sürüm yönetimi talimatlarına](../CONTRIBUTING.md) göre arşivlenir.
