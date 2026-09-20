# Soru setleri (tek tur, en çok 10 soru)

Amaç, danışmanın yazmayı unuttuğu olguları ve **verilmiş** kararları almaktır. Bu dosya bir kontrol listesidir, senaryo değildir: girdide yanıtı olanı at, yakın soruları birleştir, bu geliştirmenin açıkça gerektirdiği soruyu (örneğin "riskli tedarikçi hangi ölçütle, hangi alandan belirleniyor?") kendin ekle. Seçenek sunma, öneri yapma: "X mi Y mi olsun?" yerine "X kararlaştırıldı mı, nedir?" diye sor. Soruları bölüm ağırlığına göre sırala (3.5, 3.4, 6.1, 2.2, 3.3, 2.1, 2.5, 5.1 önce). Yanıt gelmeyen her soru bir işaret ve 7.3'te bir OPEN satırı olur.

## Her türde

| Soru | Beslediği bölüm |
|---|---|
| Bugün bu iş hangi uygulamada, kim tarafından, hangi adımlarla yapılıyor; sorun tam olarak hangi adımda? | 2.1 |
| Sorunun ölçülebilir etkisi ve hacmi nedir (adet/gün, süre, hata sayısı)? Gerçek bir örnek belge numarası ve tarihi var mı? | 2.1 |
| Genişletme yaklaşımı, kullanılacak SAP teknolojisi ve hedef clean core seviyesi kararlaştırıldı mı; karar nedir? | 1.1, 2.2 |
| Kapsam sınırı nedir: hangi şirket kodları, belge türleri, kanallar içeride; bilerek dışarıda bırakılan ne? | 2.5 |
| Hangi dış ekip ya da sisteme bağımlılık var; doğru kabul edilen varsayımlar kim tarafından, ne zaman doğrulandı? | 2.5 |
| Bir adım başarısız olursa sistem ne yapacak, kullanıcı ne görecek, kim müdahale edecek? | 3.5, 5.1 |
| Uygulamayı kim kullanacak; hangi organizasyon düzeyinde (şirket kodu, satınalma org. vb.) yetki kısıtı isteniyor? | 5.2, 5.3 |
| Test için kullanılabilecek gerçek veri nedir (belge no, ana veri, şirket kodu)? | 6.1 |
| Canlıya geçiş tarihi, taşıma sorumlusu ve her sistemde elle yapılacak adımlar belli mi? | 7.2 |
| Üretimde sorun çıktığında neye bakılacak: hangi olaylar, nereye, ne kadar süreyle loglanacak? | 7.1 |
| Açık kalan konuların sahibi ve hedef tarihi kim, ne zaman? | 7.3 |
| Doğrulanmış SAP nesne listesi (CDS view, API, BAdI, App ID) ve projenin adlandırma standardı var mı? | 4.1 |

## R · Rapor

| Soru | Bölüm |
|---|---|
| Seçim alanları hangileri; hangileri zorunlu, varsayılanları ve değer yardımları ne? | 3.2 |
| Çıktı kolonları, sıralama, toplam/ara toplam ve navigasyon hedefleri ne? | 3.6 |
| Veri hacmi ve kabul edilebilir yanıt süresi ne? | 3.11 |
| Çıktı tipi ve dışa aktarma ihtiyacı kararlaştırıldı mı? | 3.6 |

## I · Arayüz / API

| Soru | Bölüm |
|---|---|
| Yön, protokol, format ve kimlik doğrulama yöntemi karşı tarafla kararlaştırıldı mı; uç nokta ne? | 3.4, 3.10 |
| Tetikleyici ne (olay, job, kullanıcı) ve sıklığı ne; hacim ve en büyük mesaj boyu ne? | 3.4 |
| Alan eşlemesinin kaynağı var mı (karşı sistemin şeması, örnek mesaj)? | 3.4 |
| Aynı mesaj iki kez giderse ya da gelirse ne olacak; tekilleştirme anahtarı kararlaştırıldı mı? | 3.9 |
| Karşı sistem yanıt vermezse: zaman aşımı, tekrar sayısı ve aralığı, vazgeçme noktası kararlaştırıldı mı? | 3.9 |
| Karşı sistemin hata kodları ve her biri için beklenen davranış ne; SLA ne? | 3.10 |
| Hatalı mesajları kim, hangi uygulamadan izleyecek ve yeniden işleyecek? | 3.9, 7.1 |

## C · Dönüşüm

| Soru | Bölüm |
|---|---|
| Kaynak sistem, dosya biçimi, kayıt sayısı ve yükleme penceresi ne? | 3.4, 3.11 |
| Dönüşüm ve temizleme kuralları kimden onaylı; eşleme tablosu var mı? | 3.4 |
| Hatalı kayıt ne olacak: atlanır mı, yük durur mu; hata raporu kime gider? | 5.1 |
| Yükleme yeniden çalıştırılırsa çift kayıt nasıl önlenecek? | 3.9 |
| Yükleme sonrası mutabakat nasıl yapılacak (adet, tutar kontrolü)? | 6.1 |

## E · Genişletme

| Soru | Bölüm |
|---|---|
| Hangi genişletme noktası kullanılacak; released olduğu doğrulandı mı? | 4.3 |
| Mantık hangi anda, hangi belge türü ve koşullarda çalışacak; hangi durumda standart davranış korunacak? | 3.5 |
| Standart alanları mı değiştirecek, özel alan mı dolduracak; özel alanlar tanımlı mı? | 4.2, 4.3 |
| Kaydetme süresine etkisi için bir sınır var mı? | 3.5 (profil `tam` ise 3.11) |

## F · Form

| Soru | Bölüm |
|---|---|
| Form teknolojisi, çıktı kanalları (yazdırma, e-posta) ve diller kararlaştırıldı mı? | 4.4 |
| Hangi koşulda basılacak; çıktı belirleme kuralı ne? | 4.4 |
| Onaylı bir örnek çıktı ya da alan listesi var mı; logo, imza, yasal metin gereksinimi ne? | 4.4 |

## W · İş akışı

| Soru | Bölüm |
|---|---|
| Adımlar ve her adımda onaycı nasıl belirleniyor (rol, tutar eşiği, organizasyon)? | 2.3, 3.5 |
| Ret, geri gönderme, vekâlet ve süre aşımı durumlarında ne olacak? | 2.3, 3.8 |
| Onay sırasında hangi alanlar değişebilir; değişiklik akışı yeniden başlatır mı? | 3.5 |
| Kime, ne zaman, hangi bildirim gidecek? | 5.1, 7.1 |

## U · Fiori / UI5 uygulaması

| Soru | Bölüm |
|---|---|
| Floorplan ve UI yaklaşımı (Fiori elements, freestyle) kararlaştırıldı mı; OData versiyonu ve draft kullanımı ne? | 1.2, 3.3 |
| Ekranlar, filtreler, kolonlar ve alanlar hangileri; hangileri düzenlenebilir, zorunlu, koşullu görünür? | 3.3, 3.7 |
| Aksiyonlar hangileri; hangi durumda etkin, yetkisi olmayan kullanıcı ne görecek? | 3.3, 5.3 |
| Kaydın durumları ve izinli geçişleri ne? | 3.8 |
| Launchpad yerleşimi, cihazlar ve diller ne? | 3.3 |
