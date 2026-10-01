# Kurulum ve host güncellemeleri

[English](installation.md) · Türkçe

## Ön koşullar

Host PATH'inde `python` adıyla sunulan Python 3.11+ ve SQLite FTS5 ile plugin destekleyen güncel Claude Code veya Codex CLI kullanın. Repo herkese açıktır; özel GitHub erişimi gerekmez. Plugin dosyalarına kimlik bilgisi yazılmaz. `plugins/yula` klasöründen `python scripts/preflight.py --host both` çalıştırın veya yalnız `claude` / `codex` seçin.

## GitHub marketplace

Claude Code terminal komutları:

```text
claude plugin marketplace add aytacmehmet/public-skills
claude plugin install yula@aytacmehmet-public
claude plugin list
```

Codex terminal komutları:

```text
codex plugin marketplace add aytacmehmet/public-skills --sparse .agents --sparse .claude-plugin --sparse plugins/yula
codex plugin add yula@aytacmehmet-public
codex plugin list --marketplace aytacmehmet-public
```

Sparse yollar hem kök marketplace'i hem plugin'in tamamını korur. İki host aynı runtime, üç skill ve dört okuma aracını kullanır; `.codex-plugin/plugin.json` ve `.claude-plugin/plugin.json` host'a özgü metadatayı sağlar. Claude Code MCP sunucusunu `.mcp.json` ile başlatır; Codex `${CLAUDE_PLUGIN_ROOT}` değişkenini genişletmediğinden Codex manifesti aynı sunucuyu, kurulu plugin köküne çözümlenen `cwd: "."` ile satır içinde tanımlar. `agents/openai.yaml`, Codex arayüz metadatasıdır; Claude alt agent'ı değildir.

## Yerel repo veya teslim ZIP'i

Teslim ZIP'i repo yapısını taşıyan tek bir `yula-marketplace/` klasörü içerir: `.agents/plugins/marketplace.json`, `.claude-plugin/marketplace.json` ve `plugins/yula/`. Sabit bir klasöre açın. `plugins/yula` alt klasörünü veya ZIP dosyasını değil, açılmış **marketplace kökünü** (`yula-marketplace`) kaydedin.

```text
claude plugin marketplace add "/absolute/path/to/marketplace"
claude plugin install yula@aytacmehmet-public
codex plugin marketplace add "/absolute/path/to/marketplace"
codex plugin add yula@aytacmehmet-public
```

ZIP marketplace'i yalnız Yula'yı içerir; repo marketplace'i başka plugin'ler de listeleyebilir. Kaynak klasörü kayıtlı kaldığı sürece saklayın. Marketplace kaynağını değiştirmek için host'un marketplace yönetim komutlarını kullanın; aynı marketplace adı altında iki kaynağı eşzamanlı kaydetmeyin. Claude geliştirme oturumu için `claude --plugin-dir "/absolute/path/to/marketplace/plugins/yula"` Yula'yı doğrudan yükler. Aynı plugin'i iki kez yüklemeyin.

## Etkinleştirme ve veri alanı

Kurulum/güncelleme sonrasında yeni oturum başlatın. Claude komutları `/yula:sap-released-object-advisor`, `/yula:sap-released-object-developer` ve `/yula:sap-configuration-architect` şeklindedir. Codex aynı skill'leri seçicisinde sunar. Otomatik seçim açıktır. Claude `/mcp` ekranında `plugin:yula:yula`; Codex `mcp list` çıktısında kayıtlı sunucu görülmelidir. Kayıtlı olması başarılı araç çağrısı anlamına gelmez.

Manifest `--data-root @user/yula` seçer. Farklı harici veritabanı için host'u başlatmadan önce başlatma ortamında `YULA_DATA_ROOT` ayarlayın (Codex bunu manifestteki `env_vars` ile iletir); yoksa işletim sisteminin kullanıcı veri klasörü kullanılır. İki host varsayılan olarak bunu paylaşır. İlk sorgu paket içindeki ZIP'i çevrimdışı doğrulayıp açar. Plugin güncellemesi çalışan veriyi korur. CLI bakımı `--data-root` veya ortam değişkeni gerektirir; host ile aynı hedefi seçin.

## Güncelleme

Host'un marketplace ve plugin güncelleme akışını kullanın; oturumu yeniden başlatıp kurulu sürümü ve bir araç yanıtını kontrol edin. Güncelleme sözdizimi için kurulu CLI'ın `plugin --help` çıktısını okuyun. Plugin'i yeniden kurmak çalışan veritabanını yenilemez; açık `check` / hash bağlı `apply` kullanın. Depolama revizyonu 2, 1.2.0 ile uyumludur. Daha eski çalışan veritabanları seçilen veri hedefinde `migrate` ile plan hazırlayıp uygulayabilir.

## Biçim kaynakları

[Claude plugin biçimi](https://code.claude.com/docs/en/plugins-reference), [Claude marketplace biçimi](https://code.claude.com/docs/en/plugin-marketplaces), [OpenAI plugin paketleme](https://developers.openai.com/plugins/build/plugins). Kurulu CLI kontrolleri ve repo CI'ı yerel uyumluluk kanıtıdır; model sohbetini veya canlı SAP davranışını doğrulamaz.
