# SAP Geliştirme Dokümantasyonu

[Türkçe katalog](../README.md) · [English: SAP Development Documentation](../../en/sap-development-documentation/README.md)

Geliştirmelerin tasarımını, ilerleyişini, kararlarını, bağımlılıklarını, SAP nesne envanterini ve kanıtlarını proje içindeki tek Obsidian Vault'ta tutar. Kısa Current State kaydı, yeni görevin tüm geçmişi okumadan kaldığı yerden devam etmesini sağlar.

## Diller ve kurulum

Bu paketin yönergeleri Türkçedir. [İngilizce karşılığı](../../en/sap-development-documentation/README.md) aynı davranışı İngilizce yönergelerle sunar. **Her iki sürüm de Vault belgelerini İngilizce üretir.** Üretilen belge şablonları ve içerikleri, şema anahtarları, komut adları ve yapılandırılmış yardımcı araç mesajları bilinçli olarak İngilizce kalır. Uygulama kodu ve testler iki pakette bayt düzeyinde aynıdır; üretilen proje talimatı her paketin kendi skill adını çağırır.

Skill Installer kullanılabiliyorsa:

```text
$skill-installer https://github.com/aytacmehmet/public-skills/tree/main/tr/sap-gelistirme-dokumantasyonu adresindeki skill'i kur.
```

Alternatif olarak yalnız bu skill klasörünü Codex ortamınızın desteklediği konuma kopyalayın. Uygun konum için [resmî skill belgesine](https://learn.chatgpt.com/docs/build-skills) bakın. Değiştirmeden önce mevcut kurulumu koruyun; skill'in seçim listesinde göründüğünü doğrulayın. Yeni bir tur veya istemcinin yeniden başlatılması gerekebilir. Eski sürümleri skill keşif klasörlerinin içine açmayın.

Yardımcı araç Python 3.12+ ve PyYAML 6.x gerektirir; bağımlılığı [requirements](scripts/requirements.txt) dosyasında bulunur. Bu alt sürüm sınırı Windows'taki dizin bağlantısı kontrollerini destekler. Obsidian topluluk eklentisi veya arka plan servisi gerekmez.

## Kullanım

Gerçek proje üzerinde bir görev açıp gerekli işlemi isteyin:

```text
$sap-gelistirme-dokumantasyonu Bu projenin İngilizce Obsidian geliştirme dokümantasyonunu kur, mevcut kaynak otoritesini koru ve proje dokümantasyon talimatını ekle.
```

```text
$sap-gelistirme-dokumantasyonu DEV-001 için Current State kaydından devam et. Belgeleri güncellemeden önce değişen kaynakları ve gerekli bağımlılık sözleşmelerini incele.
```

```text
$sap-gelistirme-dokumantasyonu Verilen kaynak dosyaları ve geçmişten tamamlanan değişiklikleri belgele. Olayın gerçekleşme zamanı ile kayıt zamanını ayır; eksik kanıtları açık konu olarak tut.
```

Kurulum gerçek proje kökünü belirler, `obsidian/` alanını oluşturur veya mevcut yapıyı kurallara uyarlar; kısa kuralı etkin proje talimatı dosyasına birleştirebilir. Yönetilmeyen mevcut Vault, uyarlanmadan önce okunup eşlenir. Geçici sohbet klasörü kendiliğinden SAP projesi sayılmaz. Yetkilendirilmiş ilgili geliştirme işi, belgelerinin güncellenmesini de kapsar; her değişiklikte ayrı dokümantasyon isteği gerekmez.

## Düzen ve bağlam okuma

- `developments/<ID>-<slug>/`: her geliştirme için ayrı klasör.
- `shared/<ID>-<slug>/`: yeniden kullanılabilir bileşenler ve sözleşmeleri.
- `architecture/`: ortak mimari ve birden fazla alanı ilgilendiren kararlar.
- Her kayıt için dört temel sayfa: Overview, Current State, History ve Open Items.
- Gerektiğinde eklenen sayfalar: Design, Process, Objects, UI, Verification, Sources, Handover ve bağımsız ADR'ler.
- `assets/<ID>/`: gerçek ekran görüntüleri ve kanıtlar; `templates/`: İngilizce çıktı şablonları.

Wikilink'ler sayfa geçişlerini, ilişkileri ve Obsidian backlink'lerini sağlar. Bağımlılık listesi tüketiciden sağlayıcıya yönü tutar; üretilen tüketici listeleri ters yönde gezinmeyi sağlar. Ortak bilgi tek sahibinde kalır. Özgün onaylı şartnameler ve kod kendi otoritelerini korur.

Devam okuması ilgili Current State kaydını, doğrudan bağımlılıkları ve kaynak değişikliği işaretlerini getirir; tüm günlükleri yüklemez. Anlamlı değişiklikler, kimliği sabit geçmiş kaydını ekler ve güncel durumu yeniler. Aynı olayın aynı içerikle tekrarı işlem yapmaz; düzeltme yeni olay kimliği kullanır. Yapı, gereksiz okumayı azaltmayı amaçlar; ölçülmüş token tasarrufu iddiası içermez.

## Doğrulama ve sınırlar

```text
python -X utf8 -B scripts/test_vault.py
```

Yalıtılmış testler kurulum, gezinme, bağımlılık, kaynak değişikliği, olay tekrarı, geçmişin korunması, yol sınırları ve eşzamanlı düzenlemeleri kapsar. Komutlar ve doğrulama kapsamı için [işlemler](references/operations.md) belgesine bakın. Proje talimatı ve araç kontrolleri dosya yerleşimini yönlendirir; bir skill her türlü dosya yazımını engelleyemez veya sonraki her oturumun kurala uyacağını garanti edemez.

Yapısal doğrulama; anlatım kalitesini, tüm iş kapsamını, diyagram görünümünü, ekran görüntüsü kaynağını veya SAP tenant hazırlığını kanıtlamaz. Yerel kontrolleri, tenant okumalarını, aktivasyonu, çalışma zamanı testlerini, iş birimi kabulünü ve canlıya geçiş onayını ayrı izleyin. İlgili diyagramları ve UI kanıtlarını gerçek hedef ortamda doğrulayın.

## Paket

[Yönerge](SKILL.md) · [Vault sözleşmesi](references/vault-contract.md) · [İşlemler](references/operations.md) · [Kaynaklar](references/sources.md) · [Değişiklik geçmişi](CHANGELOG.md) · [Arşivler](archived/README.md) · [GPL-3.0 lisansı](LICENSE)

Bu, 1.0.0 sürümlü ilk herkese açık yayındır. Güncel dosyalar paket kökünde bulunur. Sonraki güncellemelerde önceki commit'li sürüm, deponun [sürüm yönetimi talimatlarına](../CONTRIBUTING.md) göre arşivlenir.
