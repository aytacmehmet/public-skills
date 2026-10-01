# Kaynak ve arayüz geçmişi

[English](provenance.md) · Türkçe

Yula; nesne/kanıt/üye/public içerik şeması ve erişim anlamlarını sağlanan SAP Brain paketinden, sürüme göre bölünmüş uyarlama kataloğunu, XML çalışma kitabı okuyucusunu ve kanıt yaşam döngüsünü sağlanan SAP Configuration Architect skill'inden türetir. `runtime/yula/vendor/sca.py` içinde yalnız erişilen çalışma kitabı/kanonik veri alma çağrıları tutulur; kullanılmayan CLI komutları, host değiştirme yolları ve toplu prompt şablonları dışarıda bırakılır.

Advisor/developer ayrımı korunur. Ortak kurallar koşullu yüklenen tek referanstadır. Uyarlamanın eski zorunlu çoklu referans yüklemesi ve her yanıt sonrasında yazması; göreve özgü erişim ve açık, yararlı kanıt kaydıyla değiştirilmiştir. Çevrimdışı kullanım için VOLTRAN gateway, SAP geliştirme runtime'ı, Node/npm veya canlı kimlik bilgisi gerekmez.

Resmî released katalog otoritesi: [SAP Cloudification Repository](https://github.com/SAP/abap-atc-cr-cv-s4hc), tam [Public Edition JSON](https://raw.githubusercontent.com/SAP/abap-atc-cr-cv-s4hc/main/src/objectReleaseInfoLatest.json). SAP kaynak lisansı ve atfı `LICENSES/` altında korunur.

Dokümantasyon kaynağı: [SAP Help Portal](https://help.sap.com/docs/). Kayıtlı konular kesin belge/konu kimliği, edition/sürüm ve URL'yi korur. Başlangıçta bilinmeyen alınma tarihleri bilinmeyen kalır. Uyarlama çalışma kitabının sürümü ve hash'leri başlangıç manifesti/kaynak kayıtlarında bulunur; hazırlanmış dosyalar ve proje dersleri SAP tarafından yazılmış ifadeler değildir.

Taşıma sözleşmesi: [MCP stdio belirtimi](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports). Yula satır ayrımlı JSON-RPC başlangıcı, ping, araç keşfi ve çağrılarını uygular; yalnız gerçekleştirdiği araçları ilan eder. HTTP taşıması, kaynak aboneliği, prompt, elicitation veya SAP çalıştırma yeteneği ilan etmez.

Eski işlem eşlemesi:

| Eski işlem | Yula arayüzü |
|---|---|
| check_objects_released | yula_check |
| find_released_objects | yula_search: catalog |
| find_objects_by_capability | yula_search: objects; elle eşlenmiş sonuçlar ve sözcüksel adaylar ayrıdır |
| get_object_context / get_object_content | yula_get: object summary/members/declaration/sources |
| search_abap_docs / read_abap_doc_topic | yula_search: docs / yula_get: topic |
| recall_lessons | yula_search: lessons; aday/proje durumu korunur |
| index/object/docs durumu | yula_status |
| kaynak eşitleme | scripts/yula.py check/apply/rollback |
| SCA query / activity | yula_search: configuration / yula_get: activity bölümleri |
| SCA import-catalog / build-index | configuration-workbook / configuration-root bakım adaptörleri |
| araştırma/olay/ders/sürüm kaydı | değiştirilemez revizyonlu knowledge-records bakım adaptörü |

Eski adlar eşzamanlı alias olarak kaydedilmez; eşlenerek yinelenen MCP şemaları önlenir. Tam araç metadatası `tools/list` ile keşfedilir; SQLite içeriğinin tamamı prompt bağlamına aktarılmaz.
