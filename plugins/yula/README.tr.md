# Yula 1.4.1

[English](README.md) · Türkçe

Kanıta dayalı SAP S/4HANA Cloud Public Edition nesne danışmanlığı, ABAP Cloud çağrı sözleşmeleri ve uyarlama mimarisini tek bir **Codex ve Claude Code** plugin'inde birleştirir. Yanıtlar kullanıcının dilindedir; model talimatları, araç şemaları ve ortak teknik referanslar İngilizcedir.

## İçerik

- [Released nesne danışmanı](skills/sap-released-object-advisor/README.tr.md): nesne seçimi ve açıklama.
- [Released nesne geliştiricisi](skills/sap-released-object-developer/README.tr.md): kesin public imzalar ve çağrı bağlamı.
- [Uyarlama mimarı](skills/sap-configuration-architect/README.tr.md): SSCUI/CBC, bağımlılıklar, hata teşhisi ve sürüm etkisi.
- Dört çevrimdışı okuma aracı: `yula_search`, `yula_get`, `yula_check`, `yula_status`. Güncellemeler açık CLI işlemleridir.
- Dolu SQLite başlangıç veritabanı: **37.030 katalog kaydı, 33.307 nesne bağlamı, 244.715 üye, 4.328 uyarlama aktivitesi**. Tarih, hash ve eksikler `data/manifest.json` içindedir.

## Kurulum

Host'un PATH'inde `python` adıyla erişilen **Python 3.11+ ve SQLite FTS5** gerekir. Çevrimdışı kullanım için pip/npm kurulumu veya SAP bağlantısı gerekmez. Bu herkese açık repo için özel GitHub erişimi gerekmez.

Claude Code:

```text
/plugin marketplace add aytacmehmet/public-skills
/plugin install yula@aytacmehmet-public
```

Codex CLI:

```text
codex plugin marketplace add aytacmehmet/public-skills --sparse .agents --sparse .claude-plugin --sparse plugins/yula
codex plugin add yula@aytacmehmet-public
```

Yeni host oturumu başlatın. Ön kontrol, yerel/ZIP kurulumu ve host ayrıntıları için [kurulum ve güncelleme](references/installation.tr.md) belgesine bakın. Plugin'in tamamını kurun; tekil skill klasörleri ortak dosyalara bağlıdır.

## Veritabanı ve güncellemeler

`data/yula.sqlite.zip`, **472.088.576 baytlık SQLite veritabanının tamamını** 78.681.985 bayta sıkıştırılmış olarak içerir. Git LFS istemcisi veya veritabanı indirmesi gerekmez. İlk kullanımda arşiv hash'i, üye adı, açılmış boyut, CRC, SQLite hash'i ve şeması doğrulanır; ardından harici snapshot yayımlanır. Açılmış veritabanının SHA-256 değeri `bf16b36d56dd4382dea07a3c5cd63250095e9ba3500b8a607f37b5228996b620` olup 1.2.0 ile aynıdır.

MCP manifesti `@user/yula` hedefini açıkça seçer: tanımlıysa `YULA_DATA_ROOT`; yoksa Windows'ta `%LOCALAPPDATA%/yula`, diğer sistemlerde `$XDG_DATA_HOME/yula` veya `~/.local/share/yula`. Host'ları ayırmak için host başlatma ortamında `YULA_DATA_ROOT` ayarlayın. İlk açılışın geçici kopyaları için yaklaşık 1 GB boş alan ayırın; güncellemeler ve saklanan geri dönüş snapshot'ları ek alan gerektirir. Plugin klasörü değiştirilmez.

Kurulu plugin klasöründen çalıştırın; somut harici `--data-root PATH` ortam değişkenine üstün gelir:

```text
python scripts/yula.py --data-root @user/yula status
python scripts/yula.py --data-root @user/yula check --source sap-released
python scripts/yula.py --data-root @user/yula apply --plan /path/from/check/plan.json --hash SHA256_FROM_CHECK
python scripts/yula.py --data-root @user/yula rollback --expected-active CURRENT_SHA256 --to BACKUP_SHA256
```

`check` çıktısındaki plan yolunu ve hash'i aynen kullanın. İsteğe bağlı kaynaklar için `config/sources.example.json` dosyasını plugin dışına kopyalayın; `check --config /external/sources.json --source SOURCE_ID` ile seçin. Desteklenen girdiler: resmî released nesne JSON'u, SAP Help konu/belgeleri, uyumlu nesne/uyarlama SQLite dosyaları, uyarlama klasörleri/çalışma kitapları, kanıt kayıtları ve salt okunur SAP CLAS/INTF metadatası. Kimlik bilgileri yalnız ortam değişkeni adlarıyla referanslanır. Metadata yenilemesi public imzaları yenilemez. Güncellemeler atomik yayından önce hazırlanıp doğrulanır; önceki snapshot'lar geri dönüş için saklanır. Zamanlayıcı veya arka plan güncelleyicisi kurulmaz.

## Doğrulama ve sınırlar

```text
python scripts/preflight.py --host both
python scripts/check_package.py --work-dir /external/yula-check
python -B -m unittest discover -s tests -v
```

Testler geçici klasör kullanır; üst klasörü seçmek için `YULA_TEST_ROOT` ayarlayın. CI; sıkıştırılmış ve açılmış veritabanını, paket hash'lerini, repo kurallarını ve runtime testlerini doğrular. `tests/validation.json`, `tests/host-compatibility.json` ve `tests/review-1.2.0.json` açıkça sürümlenmiş geçmiş 1.2.0 kanıtıdır; güncel repo CI'ı 1.4.1 sürümünü doğrular.

Güncel released nesnelerden **2.539'unun zenginleştirilmiş bağlamı yoktur**. Yalnız iki yetenek ve bir tarif elle eşlenmiştir; diğer adaylar için sözleşme kanıtı gerekir. Bilinmeyen kaynak tarihleri ve geçmiş başarısız veri alma kayıtları görünür kalır. Yerel testler SAP tenant/derleyici/ATC/runtime uygunluğunu kanıtlamaz. Kontrollü Codex MCP, aktivasyon ve güvenlik sonuçları [tarihsel 1.4.0 qualification kanıtında](tests/qualification-1.4.0.json) kayıtlıdır; genel token tasarrufu veya SAP tenant doğrulaması iddiası taşımaz. Claude model eval durumu NOT_RUN olarak korunur.

## Dağıtım ve lisans

1.3.1, Codex'teki MCP başlatma hatasını giderir: Codex `${CLAUDE_PLUGIN_ROOT}` değişkenini genişletmediğinden `.codex-plugin/plugin.json` sunucuyu artık satır içinde tanımlar, kurulu plugin kökünden (`cwd: "."`) başlatır ve `YULA_DATA_ROOT` değişkenini iletir. Runtime, skill'ler ve veritabanı değişmez. 1.3.0; repo marketplace entegrasyonu, iki dilli belgeler, sınırlandırılmış sıkıştırılmış veritabanı açma, açık CLI veri hedefi ve dağıtım testlerini ekler. Temel veritabanı içeriği değişmez. Kaynak/runtime [GPL-3.0](LICENSE) kapsamındadır; korunan SAP kaynak koşulları ve atıfları `LICENSES/` ve [kaynak geçmişinde](references/provenance.tr.md) bulunur. Public plugin sürüm geçmişi commit'li Git sürümlerinde korunur; tam teslim ZIP'leri repo içinde yinelenen arşivler olarak tutulmaz. İlk public-skills dağıtımı için [değişiklik geçmişine](CHANGELOG.tr.md) ve [kaynak yayın kaydına](PUBLICATION.json) bakın.

Teslimi `python scripts/build_package.py --output-dir /external/artifacts` ile yeniden üretin. Ürettiği `PACKAGE-MANIFEST.json` dosyasını commit öncesi plugin kaynağına kopyalayıp paket doğrulamasını çalıştırın. Paketleyici kaynağı değiştirmez.

## Sınırlı veri okuma ve görev kapsamı

1.4.1 sürümü, kabul edilen yapılandırılmış araştırma özetlerini açık JSON gösterimiyle okur. Büyük yapılandırılmış activity kayıtları kayıpsız `json_record_page` yanıtlarıyla sayfalanır. `textOffset` alanına dönen `nextTextOffset` değerini verin; kayıt `offset` ve `snapshot` değerlerini koruyun. Dönen kayıt `nextOffset` değerini yalnız metin sayfaları tamamlandıktan sonra izleyin. Kayıt offset'ini ilerletirken yeni yanıt `json_record_page` seçeneğini döndürene kadar `textOffset` alanını göndermeyin. Kısmi JSON tam kayıt kanıtı değildir. MCP yanıt sınırını korumak için metin sayfası daha da küçülebilir.

Corpus araması dört salt okunur araçla yapılır; MCP resources veya host dosya sistemi aramaları corpus okuması için yedek yol değildir. Belirtilen argümanı düzeltin veya desteklenen hedefli bir section için bir kez deneyin, ardından kanıt boşluğunu bildirin. Açıkça istenen depolama bakımı CLI teşhis prosedürünü korur.

Teşhis, kanıtla ilgili hipotezleri değerlendirir. Ayrıntılı transport bilgileri istenen transport planı için üretilir. Upgrade analizi saklanan release partition'larını karşılaştırır; kaynak içeriğini yenilemek veya import etmek açıkça istenen bakım görevine bağlıdır. Yerel katalog olguları ve test sonuçları hedef tenant erişimini veya çalıştırmayı kanıtlamaz.
