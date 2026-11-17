# Yanıt

[Türkçe katalog](../README.md) · [English: Answer](../../en/answer/README.md)

Yanıt, mevcut sohbette **sonraki mesajınız olarak gönderebileceğiniz 2–5 yararlı seçenek** önerir. Hedefi, tamamlanan işleri, açık kararları, engelleri ve son düzeltmelerinizi dikkate alır; farklı seçenekleri **0–100 tahmin puanlarıyla** sıralar. Gerçekten yararlı üç alternatif varsa varsayılan sayı üçtür.

## Kullanım

```text
/yanıt
/yanıt İki kısa seçenek sun.
/yanıt İncelemede açık kalan bulgulara odaklan.
```

İngilizce karşılığı [Answer](../../en/answer/README.md), `/answer` ile çağrılır. Yanıt varsayılan olarak Türkçe, Answer İngilizce yazar. Açık bir istek açıklama dilini değiştirebilir; her giriş kendi puan ve gerekçe etiketlerini korur.

Bunlar skill'in yorumladığı metinsel çağrılardır; uygulamanın yerleşik slash menüsüne komut kaydetmez. İstemciniz slash girişini ayırıyorsa skill'i seçin veya `$yanit` kullanın. Arayüzün hazır `/yanıt $yanit` istemi, istenen metinsel çağrıyla tam native skill seçicisini birlikte taşır. Alıntılanmış komutlar, `/yanıtla` ve skill hakkında sorular öneri üretimini başlatmaz.

## Çıktı

Her seçenekte numaralı kalın başlık, tam sayı puan, kopyalanabilir mesaj ve kısa gerekçe bulunur. İki seçenekli bir gösterim örneği:

**1. PR açıklamasını hazırla — Önerilen** (Tahmin puanı: 99)

> Bu düzeltme için problemi, değişen davranışı ve tamamlanan testleri anlatan kısa bir PR başlığı ve açıklaması hazırla.

Neden: İstenen teslim hazırlığında açık kalan adımı tamamlar.

**2. Davranış değişikliğini açıkla** (Tahmin puanı: 85)

> Düzeltmenin kullanıcı deneyimini nasıl değiştirdiğini açıkla; önceki ve düzeltilmiş davranışı mevcut kanıtlara dayanarak karşılaştır.

Neden: Tamamlanan değişikliği anlamak için farklı bir yol sunar.

Puanlar sezgisel bağlama uygunluk değerlendirmesidir; **olasılık, ölçülmüş doğruluk veya işlem yetkisi kanıtı değildir**. Örnekteki 99 sabit değer değildir. Puanlar azalan sıradadır, eşitlik mümkündür; açık tercih için yeterli dayanak yoksa önerilen işareti eklenmez.

## Bağlam ve işlem sınırları

- Önce mevcut sohbeti kullanır. Eksik bir bilgi önerileri değiştirecekse ilgili proje dosyalarında veya zaten erişilebilir bağlı kaynaklarda en fazla üç hedefli, salt okunur kontrol yapar.
- Güncel kısıtları, reddedilen yolları ve mevcut yetkiyi korur. Somut neden olmadan tamamlanan işi tekrarlamaz veya çalışan işlemi kopyalamaz.
- Bağlam yetersizse ya da iş bitmişse açıklığa kavuşturma veya kapanış seçeneği sunar; listeyi doldurmak için yeni iş uydurmaz.
- Önerileri gösterdikten sonra durur. Öneri üretirken mesaj göndermez, dosya/ayar/hafıza değiştirmez, yeni servis bağlantısı açmaz, araç kurmaz veya önerilen işi uygulamaz.

Sonraki turda bir seçeneği seçmek, gösterilen mesaj için normal bir görev talebidir. Seçeneği kısaltma isteği yalnızca metni düzenler. Belirsiz numara, işlemden önce netleştirilir.

## Kurulum

Codex'in Skill Installer becerisinden bu depodaki `tr/yanit` paketini kurmasını isteyin veya bu tek paketi ortamınızın desteklediği skill keşif dizinine kopyalayın. İngilizce giriş için `en/answer` paketini ayrıca kurun. Referans dosyasını skill ile birlikte tutun ve mevcut kurulumu değiştirmeden önce koruyun.

Skill listesinde **Yanıt** göründüğünü kontrol edin. Paketin MCP sunucusu, arka plan servisi, hook veya Python çalışma zamanı bağımlılığı yoktur. İstemcinin keşif davranışı ve yerleşik komut menüsü, skill'in metinsel çağrı kurallarından ayrıdır.

## Dosyalar ve doğrulama

- [SKILL.md](SKILL.md): giriş, metadata, numaralı kurallar ve çıktı sözleşmesi.
- [Sınır durumları](references/edge-cases.md): eksik bağlam, bitmiş iş ve kısa seçimlerde koşullu yüklenen kurallar.
- [Arayüz bilgileri](agents/openai.yaml): görünen ad ve hazır çağrı.
- [Değişiklik geçmişi](CHANGELOG.md), [arşiv rehberi](archived/README.md) ve [GPL-3.0 lisansı](LICENSE).

İki dil paketi modele dönük aynı İngilizce kuralları ve referansları paylaşır; adlar, açıklamalar ve insanlara yönelik belgeler yerelleştirilmiştir. Deponun [doğrulama ve sürüm yönetimi adımlarını](../CONTRIBUTING.md) kullanın. Paket kontrolleri tahmin kalitesini, native arayüz uyumunu, token tasarrufunu veya Composer Predictions'a üstünlüğü kanıtlamaz. Bunlar ayrı davranış ya da karşılaştırma kanıtı gerektirir; üstünlük iddiası yapılmaz.
