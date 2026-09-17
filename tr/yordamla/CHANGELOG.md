# Değişiklik geçmişi

## 2.0.0 — 2026-09-17

- Tek çalışma zamanı dosyası: `SKILL.md` bağlantı içermez ve referans yüklemez; hazırlık, model seçimi ve devam notları `<preparation>`, `<model_note>` ve `<recovery>` bölümlerine taşındı, üç referans dosyası kaldırıldı.
- Zorunlu `Kaynaklar`, `Kapsam dışı`, `Çıktı`, `Kabul` ve `Durma` alanlı şablon (karmaşık işte ayrıca `Bağımlılıklar` ve `Belirsizlikler`), sabit araç bütçesi satırı, belirsiz niteliklerin ölçülebilir ifadeye çevrilmesi ve prompt gösterilmeden önce üç maddelik öz-kontrol.
- Açık profil ölçütleri; tek alanlı belirsizlik `[?]` işaretli taslakla birlikte sorulur.
- Davranış değişikliği: yan etkisiz basit işler gösterilir ve aynı turda uygulanır; diğer işlerde sürüme bağlı onay korunur. Kısa olumlu yanıt bekleyen tek promptun onayı sayılır; eski sürüme onay yürütmek yerine sorar.
- Öneri mevcut modelle aynıysa tek satırlık model notu; onaylanan metin yürütmenin tek kapsamı; bitiş raporu en fazla üç satır.
- Yönerge emir kipinde, XML bölümleriyle ve iki iyi/kötü örnekle yeniden yazıldı; çıktı dili kullanıcıyı izler (varsayılan Türkçe).
- Bakım: PW29–PW34 davranış kontrolleri, güncellenmiş yapısal kontroller, model seçimi kaynakları kaynak notlarına taşındı. 1.2.0 arşivlendi.

## 1.2.0 — 2026-09-10

- Küçük çekirdek ve yalnız gerektiğinde okunan hazırlık/devam referansları; göreve göre iç profil seçimi.
- Model notu, metin revizyonu ve açıklama yanıtlarının ayrılması; duraklatılmış ve sonucu belirsiz işlemlerin ele alınması.
- Önerilen modelden ayrı, doğrulanmış gerçek yürütme durumu.
- İki dilde eşlenmiş değerlendirme girdileri ve verilmiş sonuçları/ölçümleri özetleyen, model çağırmayan bakım aracı.
- Paylaşılan depo doğrulamasında eksik giriş dosyası ve yanlış hazır çağrı açıkları için regresyon kontrolleri.
- 1.1.0 arşivlendi. Ana yönerge küçültüldü; gerçek toplam token tasarrufu veya otomatik model geçişi iddiası yoktur.

## 1.1.0 — 2026-09-07

- Her hazır prompta yürütme modeli, desteklenen düşünme seviyesi ve kısa gerekçe eklendi.
- Model seçimi gerekli yetenekleri, kaliteyi ve toplam çalışma ekonomisini dikkate alır; model adları sabitlenmez.
- Bilinmeyen erişim/ayarlar açıkça belirtilir; prompt onayı model değiştirmez.
- Model seçimi bakım notları ve yeni davranış senaryoları eklendi; 1.0.0 arşivlendi.

## 1.0.0 — 2026-09-05

- Yordamla'nın ilk herkese açık sürümü; İngilizce karşılığı Prompter ile birlikte yayımlandı.
- Sohbet bağlamına uygun prompt üretimi, sürüme bağlı onay ve aynı sohbette yürütme.
- Gerekli doğrulamayı koruyarak gereksiz işi sınırlayan yönergeler.
- Türkçe kurulum, kullanım, kaynak, davranış kontrolü ve arşiv belgeleri.

Önceki herkese açık sürüm: yok.
