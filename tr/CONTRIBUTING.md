# Katkı ve sürüm yönetimi

[Türkçe katalog](README.md) · [English](../en/CONTRIBUTING.md)

## Skill ekleme

`tr/` altında bir klasör, `en/` altında İngilizce karşılığını oluşturun. Gerektiğinde tire içeren kısa, küçük harfli adlar kullanın. Adlar, `yordamla` ve `prompter` örneğinde olduğu gibi dile göre farklı olabilir.

Her pakette `SKILL.md`, `README.md`, `CHANGELOG.md`, deponun `LICENSE` dosyasının bir kopyası, `agents/openai.yaml` ve `archived/README.md` bulunmalıdır. `references/`, `scripts/` veya `assets/` yalnız ihtiyaç varsa eklenir. Tanıtımlar, yönergeler, arayüz açıklamaları ve destek açıklamaları paketin dilinde yazılır; LICENSE'ın özgün hukuki metni korunur.

`SKILL.md` başındaki metadata, skill'i ve eşleştirilmiş sürümü tanımlar:

```yaml
name: yordamla
description: Skill'i ve tam tetikleme koşulunu açıklayın.
metadata:
  version: "1.0.0"
  language: "tr"
  family: "contextual-prompting"
  counterpart: "en/prompter"
```

Karşılık dosyası geri bağlantı vermeli, diğer dili kullanmalı ve aynı aile ile sürüm değerlerini taşımalıdır. Yeni bir skill için ayrı aile kimliği kullanın. İki paketi de dil kataloglarına ekleyin. Çevirinin davranış bakımından eşdeğerliğini inceleyin; yapısal doğrulama çevirinin doğruluğunu kanıtlayamaz.

İlk herkese açık yayın `1.0.0` ile başlar. `archived/` içinde yalnız açıklama bulunur; daha önce yayımlanmamış bir sürüm için arşiv uydurulmaz.

## Yayımlanmış skill'i güncelleme

En güncel dosyalar paket kökünde kalır. `latest/` klasörü açmayın veya aktif skill'i sürüm numaralı bir alt klasöre taşımayın.

1. `main` dalının güncel bir kopyasından başlayın. Yeni yayını hazırlamadan önce iki dildeki mevcut **commit'li** sürümü arşivleyin:

   ```text
   python .github/scripts/skills.py archive tr/yordamla --ref HEAD
   python .github/scripts/skills.py archive en/prompter --ref HEAD
   ```

   Yardımcı araç, commit edilmemiş değişiklikleri değil Git içeriğini okur. `1.0.0` sürümü için `archived/v1.0.0.zip` oluşturur, mevcut arşivin üzerine yazmaz ve önceki arşivleri ZIP'e eklemez. Aktif skill'i düzenlemez; commit veya push yapmaz.

2. Güncel dosyaları yerinde düzenleyin. Her iki dilde `metadata.version` değerini `MAJOR.MINOR.PATCH` biçiminde artırın: uyumsuz davranışta major, yeni yetenekte minor, uyumlu düzeltme veya belge güncellemesinde patch. İki dilde değişiklik geçmişi kaydı ekleyin ve tanıtımları gözden geçirin.
3. Daha önce yayımlanmış tüm ZIP'leri bayt düzeyinde aynen koruyun. Her arşiv, önceki paketi ve Git kaynağıyla dosya bazında SHA-256 değerlerini kaydeden `ARCHIVE-MANIFEST.json` dosyasını içerir.
4. Aşağıdaki kontrolleri çalıştırın. Yeni arşivleri, güncellenen iki paketi ve ilgili katalog değişikliklerini aynı commit'e alın. Push öncesinde farkları inceleyin.

Yayımlanmış paketin aktif dosyalarındaki her değişiklik, tanıtım veya lisans kopyası dahil, sürüm artışı ve önceki sürümün arşivini gerektirir. Yalnız dil kataloğunun değişmesi skill sürümünü değiştirmez. Düzeltme tek dilde başlasa da iki çeviri aynı sürüme birlikte geçer.

## Doğrulama

Depo kökünden, Python 3.12 veya üzeri ve Git ile:

```text
python -m pip install -r .github/requirements.txt
python -B -m unittest discover -s .github/tests -v
python -B .github/scripts/skills.py validate --base HEAD
```

Commit öncesinde `--base HEAD`, değişiklikleri önceki commit'li yayınla karşılaştırır. Commit sonrasında önceki commit'i veya bilinen eski bir yayını temel alın. Yalnız yapısal kontrol için `--base` kullanmayın. GitHub Actions, push'u önceki dal başıyla; pull request'i temel commit'iyle karşılaştırır.

Kontroller metadata, arayüz çağrısı, yerel bağlantılar, dil eşliği, sürüm uyumu, arşiv hash'leri, yayımlanmış arşivlerin tutulması ve önceki paketin tam olarak korunmasını kapsar. Çalışma zamanı davranışını, arayüz uyumluluğunu veya token tasarrufunu kanıtlamaz; davranış değiştiğinde ilgili senaryoları ayrıca sınayın.

## Eski sürümü inceleme

Eski ZIP'leri ilgili skill'in `archived/` klasöründe tutun. İncelemek için yalnız skill keşif yollarının dışındaki ayrı bir klasöre açın. Geri dönüş veya ayrı kurulum hazırlamadan önce manifestini doğrulayın. Arşivdeki `SKILL.md` dosyalarını aktif kurulumun altında açmayın.
