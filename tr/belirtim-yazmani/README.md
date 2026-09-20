# Belirtim Yazmanı

[Türkçe katalog](../README.md) · [English: Spec Writer](../../en/spec-writer/README.md)

Kararları verilmiş bir SAP Cloud ERP geliştirmesinin FS-TS'sini (fonksiyonel + teknik belirtim) yazar. Önce denetlenmiş bir JSON içerik dosyası üretir, sonra hangi çıktıyı istediğinizi sorar: Word, Excel, tek Markdown dosyası ya da Obsidian vault. Yalnız dokümantasyon yapar: yaklaşım, teknoloji, genişletme noktası ya da API seçmez. Eksik karar ve bilgi tahminle doldurulmaz; işaretlenir ve 7.3 Açık noktalar bölümüne bağlanır.

## Diller ve kurulum

Bu paketin yönergesi ve tanıtımı Türkçedir. [İngilizce karşılığı](../../en/spec-writer/README.md) aynı davranışı İngilizce yönergeyle sunar. Betikler, tanım dosyası, örnekler ve başvuru dosyaları iki pakette bayt düzeyinde aynıdır. Üretilen belgenin içerik modeli (bölüm başlıkları, sütun adları, işaretler, betik komutları ve mesajları) bilinçli olarak Türkçedir; SAP terimleri İngilizce kalır.

Skill Installer kullanılabiliyorsa:

```text
$skill-installer https://github.com/aytacmehmet/public-skills/tree/main/tr/belirtim-yazmani adresindeki skill'i kur.
```

Alternatif olarak yalnız bu skill klasörünü ortamınızın desteklediği skill keşif konumuna kopyalayın. Türkçe ve İngilizce paketi aynı anda kurmayın; aynı işi iki farklı adla tetiklerler.

Çekirdek betik yalnız Python 3.11+ standart kütüphanesini kullanır. Word dökümü `python-docx`, Excel dökümü `openpyxl` ister; ikisi de yoksa JSON, Markdown ve vault yine üretilir. Kod çalıştırılamayan ortamda skill yalnız `SKILL.md` ile çalışır: JSON'u ve Markdown'ı elle kurar, .docx ve .xlsx üretemeyeceğini söyler.

Pakette logo yoktur. Kapakta ve üst bilgide logo isterseniz kendi PNG dosyanızı `assets/logo.png` olarak koyun ya da `dok --logo dosya.png` ile verin.

## Kullanım

```text
$belirtim-yazmani Ekteki geliştirme talebi ve toplantı notlarından FS-TS yaz. Proje profili: proje.json.
```

```text
$belirtim-yazmani spec.json dosyasını denetle ve Word ile Obsidian vault olarak dök.
```

## Nasıl çalışır?

```text
girdi + proje.json ─> tek soru turu ─> spec.json ─> denetle ─> rapor ─> "hangi çıktı?" ─> docx | xlsx | md | vault
                                        (bv.py iskelet, bilgi, yama)   (kusur / girdi bekleyen)      (bv.py dok)
```

- **İçerik modeli:** 7 grupta 32 bölüm; her bölümün ağırlığı, sınıfı (kritik, normal, bonus) ve geçerli olduğu RICEF türleri `assets/tanim.json` içindedir. Başvuru dosyaları, `assets/icerik-semasi.json` ve yönergedeki biçim bloğu bu dosyadan `scripts/derle.py` ile üretilir.
- **Profil:** `hafif`, `standart`, `tam` yalnız hangi bonus bölümlerin açılacağını belirler.
- **İşaretler:** eksik karar `KARAR BEKLİYOR (OPEN-nn)`, eksik bilgi `BİLGİ BEKLİYOR (OPEN-nn)`, girdide ve proje kataloğunda olmayan SAP standart adı `[DOĞRULANACAK]`. Her biri bir 7.3 satırına bağlanır.
- **Denetim:** `bv.py denetle` düzeltilecek kusurları, yalnız bir hücre karar ya da bilgi beklediği için kalan kurallardan ayırır. Anılan her kimliğin tanımlı olmasını, her REQ'in SC, STEP ve TC'sini, 4.1 nesne kataloğunun tutarlılığını ve adlandırma kuralını denetler; 6.2 izlenebilirlik matrisini türetir.
- **Proje profili:** adlandırma kuralları ve doğrulanmış SAP nesne kataloğu skill'in dışında, projede tutulur (`assets/proje-ornek.json` örnektir).

## Doğrulama ve sınırlar

```text
python -B scripts/oz_test.py
```

Öz test türev dosyaların güncelliğini, tanım dosyasının toplamlarını, örnek içeriğin bulgusuz geçmesini, bozulmuş bir kopyada beklenen kuralların yakalanmasını, iskelet ve yama komutlarını ve dört dökümü kapsar (`python-docx` ya da `openpyxl` yoksa ilgili döküm atlanır).

Mekanik gösterge yalnız kural kısmını hesaplar; ağırlıklar, eşikler ve cezalar `assets/tanim.json` içindeki varsayımlardır ve kendi puanlama ölçütlerinize göre uyarlanmalıdır. İçerik kalitesini ölçmez. Denetim, olgu gibi yazılmış bir varsayılanı (örneğin dayanaksız bir `Must`) göremez; bu kural yönergede modele bırakılmıştır. SAP nesne adlarını sistemde doğrulamaz: yalnız girdide ya da proje kataloğunda geçip geçmediğine bakar. Skill SAP sistemine bağlanmaz, kod yazmaz, efor tahmin etmez.
