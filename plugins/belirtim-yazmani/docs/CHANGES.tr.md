# Sürüm değişiklikleri

[English](CHANGES.md) · Türkçe

## 3.2.2 — 2026-10-09

Tam okuyucu kaynaklarını dosya hash başına havuzla, hafif referansları pointer üzerinden bağla, decode sonucunu önbellekle ve paket çıktısından önce serileştirme sınırını uygula. Private inceleme protocol 3.2 ve açık tarihsel salt okunur uyumluluk mevcut public belirtimi, profilleri ve final kapıları korur.

## 3.2.1 — 2026-10-08
Codex 0.160.0 sondalarında bulunan native Codex manifest seçimi ve Windows hook başlatma uyumluluğunu düzeltir. `.codex-plugin/plugin.json` etkin Codex giriş noktası olarak kalır; taşınabilir agent-plugin metadata'sı `metadata/agent-plugin.json` içinde korunur. Windows hook komutları PowerShell kabuğu varsaymadan runtime'ın `${PLUGIN_ROOT}` yer değiştirmesini ve tırnaklı yolları kullanır. Beş çalışma profili, 22 kuralın kimliği/içeriği, A-F kapıları, tüm kapsamı okuyan üç okuyucu ve iki temiz final turu korunur. Tarihsel kalifikasyon kayıtları kendi sürüm kapsamlarında kalır; sağlayıcı maliyeti ve tam native yürütme ayrı kanıt gerektirir.

## 3.2.0 — 2026-10-08
Beş özel çalışma profili, açık kullanıcı seçimi, kanıtı gözeten puan aralıkları/risk tabanları, tam-okuyucu kapasite kontrolü, kalıcı alt ajan deneme sınırları ve native host çalışma talimatları eklenir. Kapsamlı command hook adaptörleri ve salt okunur leaf-agent tanımları eklenir. Başarısız/revizyonlu/devam ettirilen iş episode maliyetini korur; model önerileri özel kayıtta ve mevcut sağlayıcı ailesinde kalır. Mevcut belge profilleri, public 3.0 belirtim şeması, 3.1 okuyucu protokolü, A-F kapıları, tüm kapsamı okuyan üç okuyucu ve iki temiz final turu korunur. R-BYW-01..17 kimlik ve içerikleri değişmez; R-BYW-18..22 ek protokolü yönetir. Sentetik/yerel kontroller sağlayıcı maliyeti, yönlendirme, native hook yürütmesi, model erişimi veya SAP runtime kanıtı değildir.

## 3.1.0 — 2026-10-08
Ortak fiziksel dosya çözümleme, salt okunur preflight/status, okuyuculara yerel referans içeriği, gereksinim/plan/yanıt bağlaması ve beklenen cevabı gizleyen senaryo türetme. Gerçek dosya/doğrulayıcı parmak izleri ve kayıt kontrolleri eski kanıtı ve ilgisiz tekrarları azaltır. Toplu codec işlemleri katı ayrıştırma ve tam round-trip denetimini korur. Public 3.0 handoff şeması ile bütün onay/üç okuyucu/iki tur kapıları korunur; eski özel okuyucu paketleri protokol 3.1 ile yeniden yürütülmelidir. Keşif açıklaması açık FS/TS ve Türkçe görev tetikleyicilerini içerir; danışman soruları gerçek önkoşulları destekler.

## 3.0.0 — 2026-10-02
Danışman soru sahipliği ve sınırları belli developer kararları; kısa-ad önekli kendi bağlamını içeren dosya rolleri; ayrı atomik toplu ZIP teslimi; baseline/bağlı sözleşme içeriği; sıkı referans kapanışı ve hash bağlı ara kontrol planı. Public sözleşme değişir: 2.0 salt okunur import/baseline, 3.0 export biçimidir. Tarafsız/kodsuz politika ve gerçek son bağımsız inceleme korunur.

## 2.0.1 — 2026-10-01
Değerlendirilen keşif açıklaması düzeltmesini uygular: belgeleme tetikleyicisini tanımlar; tasarım/tahmin/kod/tenant işlerinde skill'i atlar; verilen skill yolunu workspace cwd'ye göre çözüp mutlak yoldan okumayı ister. 17 kural, TOON sözleşmeleri ve runtime davranışı korunur. Üç manifest, skill metadata, katalog ve dokümanlar eş sürüme alınır. Codex adayı üç tekrarlı 120 karşılaştırma koşusunu geçti; kapsam ve sınırlar [doğrulama](VERIFICATION.tr.md) ve `TOKEN-EVAL.toon` içindedir.

## 2.0.0 — 2026-09-30
Özgün model/checker, kaynak commit'i ve lisanslar korunur. TOON dönüşümü,
tipli sıfır açık kapıları, private/public projeksiyon, baseline/delta, beş eval katmanı,
tohumlanmış regresyon, değişmez teslim ve developer feedback eklendi. Runtime iki host'ta ortaktır.
Repo uyarlaması iki dilli doküman, kalıcı R-BYW kimlikleri, eş kataloglar ve CI ekler.
Private standalone çift 1.1.0'da arşivlenip 2.0.0'da emekli edilir; public yayınlar değişmez.
