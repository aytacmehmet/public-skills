# Değişiklik geçmişi

## 1.1.0 — 2026-09-28

- Modele dönük metin iki dil paketinde de İngilizce: `tr/belirtim-yazmani` paketinin `SKILL.md` gövdesi artık `en/spec-writer` ile aynı İngilizce yönerge kümesi (yalnız ad, açıklamadaki tetikleyiciler ve varsayılan kullanıcı dili farklı); `assets/tanim.json` içindeki rehber düzyazısı (amaç, kural, ipucu, iyi pratik, kural başlıkları, hazırlık kategorileri, profiller), üretilen referanslar, `soru-setleri.md` ve `sap-sozluk.md`, `bv.py`, `derle.py` ve `oz_test.py` mesaj, yardım ve yorumları İngilizce.
- Belge içerik modeli bilinçli olarak Türkçe kalır: bölüm başlıkları, alan etiketleri, sütun adları, seçenek değerleri, işaretler (`KARAR BEKLİYOR`, `BİLGİ BEKLİYOR`, `[DOĞRULANACAK]`), EARS kalıpları, iyi/kötü örnek hücreleri ve dökülen belgeler değişmedi. Dökülen belgenin denetim ekinde artık İngilizce denetim mesajları bulunur.
- Davranış değişmedi; öz test iki pakette 14/14. 1.0.0 arşivlendi.

## 1.0.0 — 2026-09-20

- İlk herkese açık yayın. Kararları verilmiş bir SAP Cloud ERP geliştirmesi için önce denetlenmiş JSON içerik dosyası üretir, sonra istenen çıktıya döker: Word, Excel, tek Markdown dosyası ya da Obsidian vault.
- İçerik modeli: 7 grupta 32 bölüm (taban ağırlık 119, bonus 35, 9 kritik bölüm), `ÖNEK-nn` kimlikleri ve REQ → SC → STEP → OBJ / MAP / MSG → TC zinciri. Tek kaynak `assets/tanim.json`; başvuru dosyaları, JSON şeması ve yönergedeki biçim bloğu `scripts/derle.py` ile ondan üretilir.
- `scripts/bv.py` (yalnız standart kütüphane): `bilgi`, `iskelet`, `eksik`, `denetle`, `yama`, `ozet`, `dok`. Denetim, düzeltilecek **kusur** ile karar ya da bilgi bekleyen hücreden doğan **girdi bekleyen** bulguyu ayırır; girdide ve proje kataloğunda olmayan SAP standart nesne adını yakalar; 6.2 izlenebilirlik matrisini atıflardan türetir.
- Yalnız dokümantasyon: tasarım kararı vermez. Eksik karar `KARAR BEKLİYOR (OPEN-nn)`, eksik bilgi `BİLGİ BEKLİYOR (OPEN-nn)`, doğrulanmamış SAP adı `[DOĞRULANACAK]` olarak yazılır ve 7.3'e bağlanır.
- Mekanik gösterge bir hedef değil yan üründür; yalnız kural kısmını hesaplar.
- İki çalışma biçimi: paket modu (betiklerle) ve metin modu (yalnız `SKILL.md`; JSON ve Markdown).

Önceki herkese açık sürüm: yok.
