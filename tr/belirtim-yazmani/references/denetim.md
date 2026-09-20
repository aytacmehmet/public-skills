# Mekanik denetim ve gösterge

Üretilmiş dosyadır (kaynak: assets/tanim.json). Kod çalıştırılabiliyorsa `scripts/bv.py denetle` yetkilidir; çalıştırılamıyorsa aşağıdaki liste elle uygulanır.

## Puanlama motorunun kuralları (mekanik karşılıkları)

| Kural | Ne ister | Ağırlık | Şiddet | Bölüm |
|---|---|---|---|---|
| GEN_001 | Şablon placeholder metni kalmamalı | 3 | warning | tümü |
| GEN_002 | Bölüm yeterince doldurulmuş olmalı | 3 | warning | tümü |
| SCOPE_000 | En az bir kapsam boyutu belirtilmeli | 3 | warning | 2.5 |
| SCOPE_001 | Kapsam sınırı çizilmiş olmalı | 4 | warning | 2.5 |
| SCOPE_002 | Üç boyutun tamamı belirtilmiş | 2 | info | 2.5 |
| ERR_001 | Mesajın türü anlaşılmalı | 4 | warning | 5.1 |
| ERR_002 | Birden fazla hata durumu ele alınmalı | 3 | warning | 5.1 |
| ERR_003 | Mesaj listesi tablo halinde olmalı | 2 | info | 5.1, 5.4 |
| ALGO_001 | Algoritma somut SAP nesnesi içermeli | 8 | error | 3.5 |
| ALGO_002 | İşlem mantığı adımlara ayrılmalı | 4 | warning | 3.5 |
| ALGO_003 | Yuvarlak ifade barındırmamalı | 3 | warning | 3.5 |
| MAP_001 | Alan eşleşmesi somut olmalı | 6 | warning | 3.4 |
| TEST_001 | Test verisi somut olmalı | 4 | warning | 6.1 |
| TEST_002 | Hata / negatif senaryo bulunmalı | 3 | warning | 6.1 |
| PROC_001 | Hedef süreç yuvarlak ifadeye kaçmamalı | 3 | warning | 2.2 |
| PROC_002 | Mevcut süreç somut sorun tanımlamalı | 3 | warning | 2.1 |
| AUTH_001 | Yetki kontrolü somut olmalı | 3 | warning | 5.2, 5.3 |
| OBJ_001 | Nesne adları verilmeli | 2 | info | 4.1 |
| SAP_001 | Kullanılan nesneler katalogda tanımlı olmalı | 4 | warning | 4.1 |
| SAP_002 | Katalogdaki nesneler dokümanda kullanılmalı | 2 | info | 4.1 |
| SAP_003 | Nesne adları SAP tipine çözülebilmeli | 3 | warning | 4.1, 4.2, 4.3 |
| SAP_004 | Adlandırma ve uzunluk kurallarına uyulmalı | 2 | warning | 4.1, 4.2, 4.3 |
| OPEN_001 | Açık noktalar netleştirilmeli | 2 | info | 7.3 |

Eski motor kuralları (ayrıca raporlanır, göstergeye girmez): META_001 Geliştirme türü seçilmiş olmalı (1.1) · META_002 Fiori için OData versiyonu (1.2) · FILL_001 Bölüm minimum doluluk (Tümü) · FILL_002 Zorunlu bölüm boş bırakılmış (Tümü) · COND_001 Fiori için 3.3 (3.3) · COND_002 API/Arayüz için 3.4 (3.4) · COND_003 Rapor için 3.2 (3.2) · COND_004 Rapor için ALV çıktı (3.6) · COND_005 Form için 4.4 (4.4) · CONT_001 Algoritma en az 3 madde (3.5) · CONT_002 En az 2 test senaryosu (6.1) · CONT_003 Açık noktalar netleştirilmeli (7.3) · CONT_004 Kapsam dışı belirtilmeli (2.5) · QUAL_001 Algoritma somut SAP nesnesi (3.5) · QUAL_002 Veri haritalama tablosu (3.4) · QUAL_003 As-Is/To-Be yuvarlak ifade (2.1, 2.2) · QUAL_004 Test somut veri (6.1) · QUAL_005 En az bir hata/edge case (6.1) · QUAL_006 Hata mesaj tipi (E/W/I) (5.1) · QUAL_007 Bağımlılık/Varsayım/Kapsam Dışı üçü de (2.5).

## Skill'in kendi denetimleri

| Kural | Önem | Ne denetler |
|---|---|---|
| YAPI_001–009 | hata / uyarı | Şema sürümü, tür ve profil, tanımsız bölüm ya da alan, satır uzunluğu, seçenek değerleri, kimlik biçimi, yinelenen kimlik |
| KRITIK_001 | hata | Kritik bölüm elle geçersiz kılınamaz |
| ZINCIR_001 | hata | Anılan her kimlik tanımlı olmalı |
| ZINCIR_002 | uyarı | Her REQ'in en az bir SC, STEP ve TC'si olmalı |
| UYD_001 | hata | SAP standart nesne adı girdide ya da proje kataloğunda olmalı ya da `[DOĞRULANACAK]` ile işaretlenmeli |
| UYD_002 | uyarı | Doğrulanacak nesneler için 7.3'te açık nokta olmalı |
| KARAR_001 | uyarı | BEKLİYOR işareti bir OPEN-nn taşımalı |
| KARAR_002 | uyarı | KARAR işaretinin andığı açık noktanın hazırlık kategorisi olmalı |
| OPEN_001 | uyarı / bilgi | Açık noktanın sahibi olmalı (ad ya da rol; kusur). Hedef tarihi olmayan satırlar girdi bekleyen olarak sayılır |
| OPEN_002 | uyarı | 7.3 'Etkilediği bölüm' bu belgede geçerli bölüm numaraları içermeli |
| ZINCIR_003 | bilgi | E ve A tipindeki her mesajın bir test senaryosu olmalı |
| YAPI_010 | uyarı | meta, surum_gecmisi ve onaylar hücreleri dolu olmalı (yoksa —) |

## Kusur ve girdi bekleyen

`denetle` iki tür sonuç verir. **Kusur**: yazımdan doğan, düzeltilmesi gereken bulgu. **Girdi bekleyen**: kural yalnız bir hücre karar ya da bilgi beklediği için kalır; gösterge bunu sayar ama düzeltilecek bir şey yoktur, içerik uydurulmaz. Çıkış kodu yalnız kusur düzeyindeki hatada 1 olur.

## Elle kontrol listesi (kod çalıştırılamıyorsa)

1. `«…»`, TBD, TODO, boş hücre yok; yoksa `—`.
2. 2.5'te Bağımlılık, Varsayım, Kapsam dışı üçü de var; kapsam sınırı yazılı.
3. 2.1'de 'Evet' işaretli sorunlu adım ve sayısal etkisi var.
4. 2.2 ve 3.5'te yuvarlak ifade yok.
5. 3.5 en az 3 adım; adımların çoğu SAP nesnesi adı içeriyor; hata → MSG ve commit/rollback yazılı.
6. 3.4'te her satırda kaynak, hedef, tip, örnek değer dolu.
7. 5.1 en az 2 satır; tip E/W/I/S/A.
8. 6.1 en az 2 senaryo; en az biri Negatif ya da Sınır; test verisinde gerçek biçimli numara var.
9. 5.2 / 5.3 satırlarında nesne, alan-değer, aktivite, katalog adları dolu.
10. Başka bölümlerde geçen her nesne adı 4.1'de; 4.1'deki her ad başka bir bölümde geçiyor; tip listeden; Z adları kurala uygun.
11. Anılan her kimlik tanımlı; her REQ'in SC, STEP ve TC'si var.
12. Her BEKLİYOR işareti ve her `[DOĞRULANACAK]` bir 7.3 satırına bağlı; açık satırların sahibi (ad ya da rol) ve etkilediği bölüm numaraları var.

## Gösterge

Yalnız mekanik kurallardan hesaplanır; kalite (LLM) puanını gerçek motor ölçer. Hedef değil, yan üründür.

- Bölüm kural puanı = 100 × (1 − kalan kural ağırlığı / değerlendirilen kural ağırlığı); `info` kuralı × 0.5; `error` kuralı kaldıysa en çok 40.
- Ortalama = ağırlıklı ortalama; geçerli taban bölümler ve yazılmış bonus bölümler.
- Cezalar: puanı 40'ın altındaki her kritik bölüm −5; en düşük 2 taban bölüm ortalamanın 30+ altındaysa −5, 45+ altındaysa −7.5 (en çok −15); 7.3'te kategorili her açık nokta −2 (kalem başına en çok −5, toplam en çok −20).
- Bantlar: ≥ 85 Geliştirmeye hazır · 70–84 Koşullu · < 70 Revizyon.
- Eşik ve katsayılar puanlama motorunun kodu görülmeden belirlenmiş varsayımlardır; gösterge içindir, hedef değildir.
