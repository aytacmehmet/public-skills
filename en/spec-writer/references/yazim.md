# Yazım kuralları

Üretilmiş dosyadır (kaynak: assets/tanim.json).

## Hücre ve kimlik kuralları

- Her hücre boş olmayan bir metindir; değer yoksa `—` yazılır.
- Kimlik `ÖNEK-nn` biçimindedir, iki hanelidir ve belge genelinde tekildir.
- Birden çok kimlik virgülle tek tek yazılır: `STEP-01, STEP-02`. Aralık (`STEP-01…06`) geçersizdir.
- Bir bölüm başka bölüme yalnız kimlikle atıf yapar. Zincir: REQ → SC → STEP → OBJ / MAP / MSG → TC.
- 3.5'te eşleme kullanan adım MAP kimliklerini, hata veren adım MSG kimliğini anar; 4.1 'Kullanıldığı yer' STEP / MAP / UI kimliklerini anar. 6.2 bu atıflardan türetilir.

## İşaretler

- Eksik karar: `KARAR BEKLİYOR (OPEN-nn)` · eksik bilgi: `BİLGİ BEKLİYOR (OPEN-nn)`. Seçenekli sütunlar da işaret alabilir. Bilinmeyen bir olgu varsayılan bir değerle (`Hayır`, `Must`, uydurma tarih) doldurulmaz.
- 7.3 satırı işaret içermez. Sahip: ad, bilinmiyorsa rol. Hedef tarih: verilmişse; yoksa `—`, uydurulmaz. Durum `Açık`. KARAR işaretinin andığı satırın kategorisi `Karar bekleyen konu` olur; diğerlerinde uygun hazırlık kalemi ya da `—`.
- Aynı soruya bağlı karar ve bilgi işaretleri tek bir OPEN-nn paylaşabilir; satırın kategorisi o zaman `Karar bekleyen konu` olur.
- Hücrenin bilinen kısmı yazılır, yalnız bilinmeyen kısmı işaret alır: `HTTP POST; zaman aşımı KARAR BEKLİYOR (OPEN-03)`.
- Geçersiz kılınamayan bir bölümün tamamı tek bir kararı bekliyorsa en az satır sayısı kadar satır yazılır; bilinen hücreler metin, karara bağlı hücreler işaret olur. İşaretli satır çoğaltılmaz.
- Girdide ve proje kataloğunda olmayan SAP standart nesne adı yalnız 4.1'de adın sonuna ` [DOĞRULANACAK]` eklenerek yazılır; bu adların tümü için 7.3'te tek bir açık nokta açılır.
- Özel (Z/Y) adlar projenin adlandırma kuralına göre önerilebilir.

## Hazırlık cezası kategorileri (7.3)

| Kategori | Ne zaman |
|---|---|
| Yayına alınmamış nesne | Released olmayan ya da release durumu doğrulanmamış bir SAP nesnesine bağımlılık |
| Açık ATC/CVA bulgusu | ATC ya da CVA'da kapatılmamış öncelik 1–2 bulgu |
| Tasarım/sözleşme açığı | Eksik tasarım ya da sözleşme bilgisi: karşı sistemin şeması, hata kodları, alan listesi, örnek mesaj |
| Geçici çözüm / hardcode | Bilerek bırakılmış sabit değer ya da geçici çözüm |
| Karar bekleyen konu | Henüz verilmemiş bir karar; KARAR BEKLİYOR işaretinin gösterdiği her satır |
| İstisna kaydı yapılmamış bulgu | Bilinen bir sapma (clean core seviyesi, ATC muafiyeti) için onaylı istisna kaydı yok |
| — | Hiçbiri uymuyor (örneğin yalnız bir tarih ya da sorumlu adı bekleniyor) |

## EARS gereksinim kalıpları (2.2)

| Kalıp | Söz dizimi | Örnek |
|---|---|---|
| Her zaman geçerli | <Sistem> <tepki> yapar. | Sistem her gönderimi ZPO_SEND_LOG tablosuna yazar. |
| Durum (While) | <Durum> sürerken <sistem> <tepki> yapar. | Status = 'Q' iken sistem 'Yeniden gönder' aksiyonunu pasif tutar. |
| Olay (When) | <Olay> olduğunda <sistem> <tepki> yapar. | Sipariş onayı tamamlandığında sistem siparişi 5 dk içinde portala gönderir. |
| Opsiyon (Where) | <Özellik> varsa <sistem> <tepki> yapar. | Tedarikçide portal kullanıcısı varsa sistem e-posta yerine portala gönderir. |
| İstenmeyen durum (If-then) | <İstenmeyen durum> olursa <sistem> <tepki> yapar. | Portal 5xx dönerse sistem 1, 5 ve 15 dk sonra yeniden dener. |
| Bileşik | <Durum> sürerken, <olay> olduğunda <sistem> <tepki> yapar. | Status = 'E' iken kullanıcı 'Yeniden gönder'e bastığında sistem kaydı 'Q' yapar. |

Kabul kriteri Given – When – Then biçimindedir: ön koşul ve test verisi · tetikleyen olay · gözlenebilir sonuç ve nerede gözlendiği.

## Yuvarlak ifade yerine somut karşılık

| Yazma | Bunun yerine |
|---|---|
| gerekli kontroller yapılır | Hangi alan, hangi koşul, hangi MSG: 'Supplier boşsa MSG-04 (E)' |
| ilgili tablolardan okunur | Nesne adı: 'I_PurchaseOrderAPI01'den PurchaseOrder, Supplier okunur' |
| uygun şekilde / gerektiğinde | Koşulu yazın: 'Status = E iken' |
| hızlı / performanslı | Ölçü: '500 sipariş ≤ 10 dk' |
| kullanıcı dostu | Davranış: 'zorunlu alan boşsa alan kırmızı, MSG-05' |
| vb. / gibi / çeşitli | Tam listeyi yazın |
| sisteme kaydedilir | Nereye ve nasıl: 'ZPO_SEND_LOG'a RAP save sequence içinde' |
| standart süreç işletilir | Uygulama adı ve adım: 'Manage Purchase Orders (F0842A) → Onaya gönder' |
| daha sonra belirlenecek | 7.3'e OPEN-nn olarak sahibi ve tarihiyle yazın |

Denetimin aradığı kalıplar: `gerekli kontrol`, `ilgili tablo`, `ilgili alan`, `ilgili yer`, `uygun şekilde`, `gerektiğinde`, `gerekirse`, `mümkünse`, `kullanıcı dostu`, `performanslı`, `hızlı bir şekilde`, `hızlı şekilde`, `sisteme kaydedilir`, `standart süreç`, `daha sonra belirlenecek`, `netleştirilecek`, `çeşitli`, `vb`, `vs.`, `v.b.`, `esnek bir`, `kolayca`, `sorunsuz`.

## Somutluk

- Sıfat yerine ölçü: süre, adet, hacim, saklama süresi, tekrar sayısı sayıyla ve birimiyle yazılır.
- Nesne ve alan adı yazılır: `I_PurchaseOrderAPI01.PurchaseOrder`; 'ilgili tablo' yazılmaz.
- Test verisi gerçek biçimlidir: belge numarası, ana veri numarası, şirket kodu.
- RAP'te kalıcılık save sequence içinde olur; `COMMIT WORK` yazılmaz.
