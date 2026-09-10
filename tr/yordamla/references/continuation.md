# Kesinti ve revizyon durumları

Kesinti, kısmi sonuç, belirsiz dış işlem veya düzenlenmiş yazı bloğunda oku. Basit görevler için durum dosyası, günlük veya hash üretme.

Gerektiğinde sohbet içinde kısa bir kayıt tut: görev/sürüm, onaylanan tam metin, durum, tamamlanan adımlar, bekleyen adım ve varsa işlem referansı. Kullanıcıya bunu her mesajda dökme. Durumlar: hazırlama, onay bekleme, uygulama, duraklatıldı, sonuç belirsiz, tamamlandı, iptal.

| Durum | Sonraki davranış |
| --- | --- |
| Metin/kapsam revizyonu | Eski onayı taşıma; tam yeni sürümü göster ve onay bekle. |
| Yalnız model notu veya açıklama | Prompt metnini ve AP sürümünü koru; açıklamayı onay sayma. |
| Kullanıcı yazı bloğunu düzenledi | Ortamın sağladığı son metin esas alınır. Metin değiştiyse revizyon göster; eski kopyayı veya görünmeyen düzenlemeyi onaylanmış sayma. |
| Duraklatılmış iş, “devam” | Geçerli onayı ve tamamlanan adımları koru; yalnız kalan işten sürdür. Yeni kapsam varsa yeniden onayla. |
| İstek gönderildi, sonuç belirsiz | Zaman aşımını başarısızlık sayma. İşlem referansı/idempotency anahtarı varsa sonucu sorgula; sonucu bilmeden yeniden yazma/gönderme. Sorgulanamıyorsa belirsizliği ve gereken kullanıcı kararını belirt. |
| Tamamlandı veya iptal | Tekrarlanan onay işi yeniden yürütmez. Kullanıcı açıkça yeni bir tekrar görevi isterse yeni AP oluştur. |
| Tam metin/onay kayboldu | Tahminle devam etme; eldeki kanıttan somut kapsamı yeniden göster ve onay al. |

Bir işlem sonucunu bildirdiğinde niyetini değil gözlemini söyle. Tamamlanan adımları yeniden çalıştırarak başarı görüntüsü oluşturma. Kalıcı yürütme kaydı, otomatik model geçişi veya dış işlem kontrolcüsü bu yönergenin kendisinde yoktur; ayrı ve doğrulanmış bir entegrasyon gerektirir.
