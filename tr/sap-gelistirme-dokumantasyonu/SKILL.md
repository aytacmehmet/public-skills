---
name: sap-gelistirme-dokumantasyonu
description: "SAP Cloud ERP geliştirme dokümantasyonunu ve kaldığı yerden devam edilebilir proje hafızasını proje içindeki Obsidian Vault'ta İngilizce oluştur ve sürdür. Vault kurulumu, geliştirme değişiklikleri, kararlar, bağımlılıklar, nesneler, kanıtlar veya bu kayıtlardan işe devam etme isteklerinde kullan. SAP geliştirmesini uygulamaz; yetkili proje şartnamelerinin yerini almaz."
metadata:
  version: "1.0.0"
  language: "tr"
  family: "sap-development-documentation"
  counterpart: "en/sap-development-documentation"
---

# SAP Geliştirme Dokümantasyonu

Her geliştirmenin tasarımını ve ilerleyişini `<proje>/obsidian` içinde izlenebilir tut. Belgeleri İngilizce yaz; kullanıcıyla onun dilinde konuş. Teknik adları, alıntılanan kaynak metnini ve onaylı kararları koru. Kullanıcının talimatları bu skill'in yönergelerinden önceliklidir.

## Doğru projeyi belirle

Gerçek proje kökünü kullanıcının isteğinden ve etkin çalışma kopyasından belirle. Projesiz sohbet klasörü, SAP projesinin kanıtı değildir. Yazmadan önce geçerli proje talimatlarını ve mevcut Vault'un tanımlayıcı dosyasını/dizinini oku. Hedefi etkileyen bir belirsizlik varsa bağımsız hazırlığa devam ederken yalnız proje kökünü sor.

Kurulumda `scripts/vault.py --project <kok> init --key <sabit-proje-anahtari> --install-guidance` kullan. Önce mevcut Vault'u incele; başlangıç aracı, yönetilmeyen ve dolu bir Vault'u doğrudan değiştirmez, içeriğin bilinçli biçimde eşlenip uyarlanmasını sağlar. Uyarlama ve komutlar için [işlemler](references/operations.md) belgesine bak. Bu durumu aşmak için ikinci bir paralel Vault oluşturma. İstenen yerel kurulum için mevcut yetki yeterlidir; ek onay döngüsü kurma.

Yardımcı araç belgeleri `obsidian` içine yazar; isteğe bağlı talimat adımı kökteki etkin `AGENTS.md` veya `AGENTS.override.md` dosyasını, ilgisiz içeriği ve bir yedeği koruyarak günceller. Geçerli alt klasör talimatlarını da incele. Dokümantasyon işinin yan etkisi olarak global ayarları değiştirme, SAP nesnelerini aktive etme, Obsidian eklentisi kurma veya ilgisiz kaynakları taşıma.

## Düzenlemeden önce bağlamı geri yükle

1. Küçük proje girişini/dizinini oku, ardından `context --id <id>` çalıştır. Sonuç metnin kesildiğini söylüyorsa Current State'in tamamını oku. Bu sınır, okuma çıktısının karakter sınırıdır; token kotası değildir.
2. Seçilen Overview ile yalnız ilgili tasarımı, kabul edilmiş kararları, açık konuları ve doğrudan bağımlılık sözleşmelerini aç. Daha fazla bağımlılığı ancak gerçek etki gerektiriyorsa izle. Kayıtlı tüketicileri bulmak için `impact --id <id>` kullan.
3. Kaynak parmak izinin değişen dosya listesini ve bilinen sürüm/tenant sınırını kontrol et. Eşleşen hash yalnız bayt eşitliğini gösterir; doğruluk, eksiksizlik, çevrimiçi kaynağın güncelliği veya SAP çalışma zamanı kanıtı değildir.
4. Sonraki işi gerçek kayıtlardan çıkar. Mevcut kod, kabul edilmiş tasarım ve özet çelişiyorsa çelişkiyi belirle, yetkili kanıtı kullan ve eski özeti bağlantılı geçmiş kaydıyla düzelt.

Her turda bütün günlükleri okuma, değişmeyen kaynakları tekrar okuma, tüm sohbetleri içe aktarma veya bütün skill referanslarını yükleme. Okumayı genişletmeden önce sabit kimlik, nesne adı, kaynak yolu veya karar kimliğiyle ara. Vault proje hafızasıdır; Codex'in global hafızalarına yazma yetkisi vermez.

## Dokümantasyonu doğru yere yönlendir

Geliştirme için `developments/<ID>-<slug>/`, yeniden kullanılabilir bileşen için `shared/<ID>-<slug>/`, proje genelindeki mimari için `architecture/` kullan. Dört temel sayfa oluşturulur: Overview, Current State, History ve Open Items. Design, Process, Objects, UI, Verification, Sources, Handover ve bağımsız ADR sayfalarını yalnız yararlı olduğunda ekle. Sorumlulukları ve SAP kanıt alanlarını [Vault sözleşmesi](references/vault-contract.md) tanımlar.

`assets/templates/` içindeki İngilizce şablonları kullan. Yol uydurmak yerine sayfaları yardımcı araçla ekle. Windows'ta da `/` kullanarak Vault köküne göre wikilink'leri koru. Her bilginin tek sahibi olsun; ortak sözleşmeleri kopyalamak yerine bağlantı ver. Üretilen dizinler, sayfa listeleri ve tüketici listeleri türetilmiş bilgidir; asıl kayıtları güncelleyip `reindex` çalıştır. İlişkinin gerekçesini ve kullanılan sözleşme sürümünü tüketicinin Overview sayfasında tut.

Mevcut yetkili FS/TS veya kod, kullanıcı açıkça değiştirmedikçe otoritesini korur. Sources sayfası; kaynakları iddialar, sürümler, köken ve inceleme tarihleriyle eşler. Geçmiş olayları yalnız erişilebilir kanıtlardan oluştur; `occurred_at` ile `recorded_at` alanlarını ayır. Eksik geçmiş açık konudur; olay veya kabul uydurma yetkisi değildir.

## Anlamlı işi kaydet

Mantıksal bir değişiklik tamamlandığında, karar kabul edildiğinde, engel oluştuğunda, iş devredildiğinde veya kesinti sınırında:

- Değişikliğin gerektirdiği tasarım, nesne, kanıt, açık konu ve bağımlılık tüketicisi kayıtlarını güncelle.
- `checkpoint` ile sabit kimlikli olay ekle; araç History'ye ekler ve Current State'i yeniler. Aynı olayın tekrarı işlem yapmaz; farklı içerik yeni düzeltme olayı gerektirir. Kabul edilmiş ADR'leri koru; gerektiğinde bağlantılı yeni kararla yürürlükten kaldır.
- Current State'i kısa tut: amaç, etkin kısıtlar/kararlar, son gerçek doğrulama, engeller, sonraki uygulanabilir adım ve yalnız gerekli bağlantılar. Kanıtları silmeden eski ayrıntıyı History'ye taşı. Kaynak parmak izlerini ancak değişen kaynağı inceleyip bağlı kayıtları güncelledikten sonra yenile.
- `reindex` ve `check` çalıştır. Kurulum, mevcut içerik uyarlaması veya dokümantasyon konumu incelemesinde `check --audit-project` kullan. Tamamlandı demeden önce hataları çözümle. Test, aktivasyon, UAT ve canlıya geçiş ayrı kanıt seviyeleridir.

Yetkilendirilmiş geliştirme değişikliğinin dokümantasyonu aynı işin parçasıdır; ayrı dokümantasyon isteği bekleme. Skill tek başına her sonraki oturumu denetleyemez veya her dosya yazımını engelleyemez. Proje talimatları yerleşim anlaşmasını sağlar; yardımcı araç kendi yazımlarını sınırlar, denetim sınıflandırılmamış Markdown dosyalarını tespit eder.

## Doğrulama ve sınırlar

Yardımcı araç Python 3.12+ ve PyYAML 6.x gerektirir. Mevcut çalışma ortamını kullan; gereksiz bağımlılık kurma. Komutlar, güvenli güncellemeler, kanıt yönetimi ve sınırlı öz test [işlemler](references/operations.md) belgesindedir. Kaynak gerekçeleri ve kontrol edilmiş resmî bağlantılar [kaynaklar](references/sources.md) dosyasındadır; yalnız dayanak davranışın yeniden doğrulanması gerektiğinde aç.

Yapısal kontroller İngilizce anlatım kalitesini, diyagram görünümünü, ekran görüntüsü kaynağını, anlamsal tutarlılığı veya SAP hazırlığını kanıtlamaz. Bu sonuç görevin parçasıysa ilgili diyagramları/UI'ı mevcut araçlarla görsel incele. Tam olarak neyin kontrol edildiğini belirt. Karşılaştırılabilir ölçüm olmadan ölçülmüş token tasarrufu iddia etme.
