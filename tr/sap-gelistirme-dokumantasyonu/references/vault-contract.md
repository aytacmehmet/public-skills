# Vault sözleşmesi — şema 1

Sahipliği belirlerken, ayrıntılı belge oluştururken veya mevcut Vault'u uyarlarken oku. Bu düzen skill'in sunduğu proje standardıdır; SAP'nin zorunlu kıldığı bir biçim değildir.

## Klasör düzeni

```text
<proje>/
  AGENTS.md                         # veya kökteki etkin AGENTS.override.md
  obsidian/
    vault.json                      # proje anahtarı, şema, izinli kaynak Markdown dosyaları
    Home.md
    Development-Index.md
    Shared-Index.md
    Documentation-Policy.md
    developments/DEV-001-name/
      Overview.md                   # kimlik, amaç, otorite, bağımlılıklar
      Current-State.md              # yetkili yaşam döngüsü ve devam özeti
      History.md                    # tarihli olaylar; önceki kayıtları koru
      Open-Items.md                 # etkin sorular ve korunan çözümler
      Design.md                     # bundan sonraki sayfaları gerektiğinde ekle
      Process.md
      Objects.md
      UI.md
      Verification.md
      Sources.md
      Handover.md
      decisions/ADR-001.md
      source-snapshots.json          # isteğe bağlı dosya parmak izleri; otorite değildir
    shared/SHR-001-name/             # aynı temel/isteğe bağlı sayfa sözleşmesi
    architecture/                   # ARCH kaydı; aynı sayfa sözleşmesi
    assets/<kayit-ID>/              # ekran görüntüleri ve kapsamı sınırlandırılmış kanıt dosyaları
    assets/guidance-backups/         # önceki kök talimat dosyasının baytları
    templates/                      # İngilizce şablonlar; proje kanıtı içermez
```

Günlük not hiyerarşisi veya her küçük düzenleme için ayrı belge oluşturma. Büyük History sayfalarını ancak gerektiğinde döneme göre böl; özgün kayıtları ve etkin History'den bağlantıları koru. Arşivlemeden önce olay kimliğiyle tekrar aramasını dikkate al: yardımcı araç yalnız etkin History dosyasını arar. Olay işaretlerini bu dosyada tut veya aramayı bilinçli biçimde genişlet; tekrar korumasını sessizce bozma.

## Kimlik ve gezinme

`ACME-ERP`, `DEV-001`, `SHR-001` gibi büyük harfli, sabit proje/kayıt kimlikleri kullan. Ortak mimarinin sahibi `ARCH` kaydıdır. Kimlikler Vault içinde benzersizdir, yeniden kullanılmaz ve görünen başlıktan bağımsızdır. Slug; küçük harf, rakam ve tire kullanır. Klasör adlarını mümkün olduğunca sabit tut.

Üretilmiş bütün notlarda benzersiz `id`, `kind` ve ISO biçimli `updated` alanı bulunur. Geliştirme/bileşen notlarında ayrıca `entity` vardır. Overview, `title` ve `dependencies` (tırnaklı wikilink listesi) ekler. Kaydın yaşam döngüsünün tek sahibi Current State'tir: planned, active, blocked, review, done, archived. ADR'nin ayrı karar durumu vardır: proposed, accepted, rejected, superseded. İsteğe bağlı düz özellikler owner, tags, aliases, source_ref, release, reviewed_at olabilir; tutarlı veri türü kullan. Kanıt tablolarını iç içe YAML biçiminde kodlama.

Her kayıt sayfası Home'a, kendi Overview ve Current State sayfalarına bağlanır. Sayfalar arasında açık Vault-kök yollarını, eklerde gerçek dosya uzantılarını kullan. Gezinmede çalışacak bağlantıları kod bloklarının dışında tut. Tablo içindeki takma ad ayıracı `\|` gerektirir. Yalnız Mermaid düğümlerindeki bağlantılar normal ilişki bağlantılarının yerini almaz.

## Bilginin sahipliği

| Bilgi | Sahip kayıt | Tüketicinin tuttuğu |
| --- | --- | --- |
| Ortak sözleşme veya kural | Ortak bileşen veya mimari tasarımı/ADR'si | Bağlantı, kullanılan sürüm, yerel uyarlama |
| Geliştirme amacı ve bağımlılık listesi | Overview | Dizinde yalnız türetilmiş bağlantı |
| Güncel yaşam döngüsü ve sonraki iş | Current State | Türetilmiş dizin durumu; tarihli devir bağlantı verebilir |
| Olaylar ve geçmiş sonuçlar | History ve özgün kanıt | Kısa etkin özet ve tam referans |
| Onaylı mimari karar | Kabul edilmiş ADR | Karar kimliği, güncel etkisi, bağlantı |
| SAP nesnesi | Tek sahip geliştirme/ortak bileşen envanteri | Yeniden kullanım bağlantısı; ikinci sahiplik iddiası yok |
| Kaynak otoritesi | Özgün kaynaklara bağlanan Sources | İddia eşlemesi ve inceleme temeli |

`dependencies`, tüketici -> sağlayıcı yönünü ifade eder. `relate --from-id DEV-001 --to-id SHR-001` bu alanı günceller; üretilen tüketici listeleri ters yönde gezinmeyi sağlar. Entegrasyon niteliğini, sürümleri, girdi/çıktı anlamını, hata davranışını, gerekçeyi ve kabul etkisini tüketicinin bağımlılık sözleşmesi ayrıntılarında tut. Açıkça bağımlılık olarak kaydedilmeyen diğer bağlantılar gezinme içindir. Bir döngü geçerli olabilir, fakat mimari açıklama gerektirir; etki sorgusu döngülerde sonlanır.

## Geliştirme kapsamı

Şablonları ilgili kanıtları hatırlatan araçlar olarak kullan; her bölümü uydurarak doldurma zorunluluğu sayma. Her önemli gereksinim sabit referanslarla tasarıma/sürece, sahip olunan uygulama nesnelerine ve doğrulamaya ulaşabilsin. Normal akışın yanında hata/alternatif akışları da kaydet. Basit değişiklik temel sayfalarda ve birkaç bağlantıyla belgelenebilir; içerik bağımsız yaşam döngüsüne ulaştığında veya uzadığında sayfa ekle.

Nesne envanteri; tam nesne türü/adı, paket, amaç, sahiplik/yeniden kullanım, kaynak konumu, bağımlılık, gözlenen durum ve kanıt/tarih içerir. Yararlı gruplar: kalıcılık/CDS, RAP davranışı ve mantık, servis/entegrasyon, UI/gezinme, yetkilendirme/uyarlama, test/operasyon. Planlanan, yerel kaynağı bulunan, tenant'ta gözlenen, aktif/yayımlanmış ve test edilmiş durumlarını gerçek kanıta göre ayır.

Doğrulamada gerçek ortam/client/release, temel sürüm, kapsam, sonuç, zaman ve kanıt gerekir. İlgisiz projenin tenant kimliklerini sabit yazma. Yerel lint/paket kontrolleri aktivasyonu, yetkileri, canlı OData davranışını, iş birimi kabulünü veya canlıya geçişi kanıtlamaz. Bitti ölçütü ilgili geliştirmeye aittir; yerel kodlama tamamlanmış olsa da kalan teslim kapılarını kaydet.

Ekran görüntülerinin gerçek kaynağı ve İngilizce açıklaması olmalıdır; mockup, yerel önizleme ve tenant görüntüsünü ayır. Sahip kaydın varlık klasörüne koyup UI sayfasından bağla. Biliniyorsa gerçek çekim zamanını ve kökenini koru; bilinmiyorsa unknown kullan. Gerçek ekranın kanıtı olarak yapay görüntü üretme. Mermaid diyagramları anlatımı ve kanıtı izlesin; önerilen tasarımları açıkça işaretle.

## Geçmiş ve güncelliğini yitiren bilgi

Olay kimliği, occurred_at (bilinmeyebilir), recorded_at, değişiklik, gerekçe, etki, sonraki adım ve kanıtı kaydet. Hatalar için yeni düzeltme olayı kullan. Kabul edilmiş ADR metnini ve onay kanıtını koru; yerini alan kararı iki yönde bağlantıyla ayrıca kaydet. Kaynak hash'leri seçilmiş özgün dosyalar için isteğe bağlı okuma yardımcılarıdır. Çevrimiçi belgenin güncelliğini, otoriteyi, onayı veya doğru yorumu kanıtlayamazlar.

Değişen kaynağın parmak izini yenilemeden önce kaynağı oku; aksi hâlde dokümantasyon farkı incelenmeden uyarı temizlenir. Önemli farkları uzlaşana kadar açık konu olarak tut. Yeni oturumun az okumayla devam edebilmesi için kabul edilmiş kısıtları ve sonraki adımı Current State'te kısa tut; özeti doğrulayacak yeterli kanıt bağlantısı ekle.
