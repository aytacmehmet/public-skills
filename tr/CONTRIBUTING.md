# Katkı ve sürüm yönetimi

[Türkçe katalog](README.md) · [English](../en/CONTRIBUTING.md)

## Skill ekleme

`tr/` altında bir klasör, `en/` altında İngilizce karşılığını oluşturun. Gerektiğinde tire içeren kısa, küçük harfli adlar kullanın. Adlar, `yordamla` ve `prompter` örneğinde olduğu gibi dile göre farklı olabilir.

Her pakette `SKILL.md`, `README.md`, `CHANGELOG.md`, deponun `LICENSE` dosyasının bir kopyası, `agents/openai.yaml` ve `archived/README.md` bulunmalıdır. `references/`, `scripts/` veya `assets/` yalnız ihtiyaç varsa eklenir. Tanıtımlar, değişiklik günlükleri, arayüz açıklamaları ve destek açıklamaları paketin dilinde yazılır. Yönergeler (`SKILL.md` gövdesi ve `references/`) paketin dilinde ya da, çift modele dönük dosyalarını paylaşıyorsa, İngilizce ve iki pakette bayt düzeyinde aynı yazılır (SAP Fiori Design / SAP Fiori Tasarım böyledir; model yine kullanıcının dilinde yanıt verir ve tetikleyici metin `description` içinde kalır); LICENSE'ın özgün hukuki metni korunur.

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

## Başka bir host için kopya üretme

Depo, skill'lerin tek kaynağıdır. Bir plugin veya başka bir host için kopya gerekiyorsa aktif paketi elle kopyalayıp düzenlemeyin:

```text
python .github/scripts/skills.py export tr/sap-fiori-tasarim --dest <depo-dışı-klasör> --name <host-adı> --overlay <host-kuralları.md>
```

Komut `archived/` dışındaki dosyaları kopyalar, istenirse skill adını ve hazır çağrıyı değiştirir, overlay dosyasını `SKILL.md` sonuna ekler ve kaynak sürümü ile commit'ini `EXPORT-MANIFEST.json` içine yazar. Host'a özgü kurallar overlay'de kalır; düzeltmeler önce bu depoda yapılır, kopya yeniden üretilir. Hedef klasör deponun dışında ve boş olmalıdır.

## Eski sürümü inceleme

Eski ZIP'leri ilgili skill'in `archived/` klasöründe tutun. İncelemek için yalnız skill keşif yollarının dışındaki ayrı bir klasöre açın. Geri dönüş veya ayrı kurulum hazırlamadan önce manifestini doğrulayın. Arşivdeki `SKILL.md` dosyalarını aktif kurulumun altında açmayın.

Dil köklerinin hemen altındaki her klasör bir skill paketidir ve SKILL.md içermelidir. Hazır çağrı tam skill adını belirtmelidir; örneğin $yordamla-eski, $yordamla yerine geçmez.

## Tam plugin paketleri

Skill'leri ortak runtime, MCP sunucusu veya veritabanına bağlı olan plugin'i bağımsız dil paketlerinin dışında `plugins/<ad>/` altında tutun. Tek bir tam dağıtım kullanın; `aytacmehmet-public` adıyla hem `.claude-plugin/marketplace.json` hem `.agents/plugins/marketplace.json` dosyasına kaydedin. İngilizce/Türkçe tanıtımlarını depo ve dil kataloglarına bağlayın. Plugin içindeki skill'leri `en/` ve `tr/` altında ayrı yönetilen kopyalar olarak çoğaltmayın.

Her plugin'de eşleşen Claude/Codex manifestleri, `README.md` / `README.tr.md`, `CHANGELOG.md` / `CHANGELOG.tr.md`, deponun birebir `LICENSE` kopyası, korunan upstream kaynak koşulları ve dosya bazlı `PACKAGE-MANIFEST.json` bulunur. Her skill'de SKILL.md, İngilizce/Türkçe tanıtımlar ve Codex arayüz metadatası gerekir. Yanıtlar kullanıcının dilini izliyorsa modele dönük yönergeler İngilizce kalabilir. Paket girdilerini, skill ad/sürümlerini, yerel bağlantıları, marketplace yollarını ve dosya hash'lerini doğrulayın; rastgele iç içe SKILL.md dosyaları yasaktır.

Mevcut yayından alınan plugin, upstream sürüm çizgisini korur; kaynak repo, commit ve uyarlamaları kaydeder. Uyumlu dağıtım/belge değişikliği patch sürümünü artırır; uydurma 1.0.0 kaynak yayını veya eski public arşiv oluşturulmaz. Runtime, host, marketplace ve skill sürümleri birlikte ilerler. Public plugin geçmişi commit'li Git sürümlerinde korunur; tam teslim ZIP'lerini veya açılmış SQLite dosyalarını repo içinde çoğaltmayın. Bağımsız skill arşivlerinin yukarıdaki kuralları korunur.

Yula için mevcut repo testlerini ve `skills.py validate --base HEAD` komutunu çalıştırın; ardından:

```text
python -B -m unittest discover -s plugins/yula/tests -v
python -B plugins/yula/scripts/check_package.py --work-dir <harici-klasör>
python -B plugins/yula/scripts/build_package.py --output-dir <harici-artifact-klasörü>
```

Üretilen paket manifestini plugin'e kopyalayın; commit öncesi doğrulamayı yeniden çalıştırıp diff'i inceleyin. Tarihsel yeterlilik raporlarının sürümlerini koruyun. Yerel kontroller ve hosted CI ayrı kanıtlardır; ikisi de SAP tenant uygunluğunu kanıtlamaz. Branch üzerinde çalışıp inceleme için PR açın; branch'in yayımlanması main'e merge edildiği anlamına gelmez.

## Claude inceleme işletimi

Otomatik incelemeler varsayılan olarak mevcut `CLAUDE_CODE_OAUTH_TOKEN` secret'ını kullanır. Action, `subtype: success` ile birlikte `is_error: true` döndürebilir; bu başarısız yürütmedir. Workflow, SDK yürütme dosyasından yalnız sınırlı hata sınıfı ve sıfırlanma bilgisini saklar. Ham model/araç çıktısı ve kimlik bilgileri yüklenmez. Kullanım limiti hatası başarısız kalır; yeniden çalıştırmadan önce bildirilen sıfırlanmayı bekleyin veya hesapta kullanılabilir kullanım sağlayın. Manuel kimlik kontrolü workflow'u mevcut OAuth kimliğiyle iki kısa, araçsız sorgu yapar.

API kimliği repo sahibinin açık seçimidir. API ücretlendirmesini onayladıktan sonra GitHub repo secret'larına `ANTHROPIC_API_KEY` ekleyin ve repo değişkenini `CLAUDE_REVIEW_AUTH_MODE=api` yapın. Workflow bu durumda yalnız API anahtarını; varsayılan/`oauth` modunda yalnız abonelik OAuth token'ını geçirir. API kullanımı Claude aboneliğinden ayrı ücretlendirilir; [resmî GitHub Actions belgesine](https://code.claude.com/docs/en/github-actions) bakın. Kimlik bilgilerini issue, PR, yorum veya loga yapıştırmayın. Anthropic GitHub App kimlik kontrolünün değişmiş inceleme workflow'unu çalıştırabilmesi için workflow değişikliği default branch'te etkinleşmelidir; kimlik kontrolünün atladığı koşu NOT_RUN'dır, inceleme kabulü değildir.
