# Yayın doğrulaması

[English](VERIFICATION.md) · Türkçe

## 3.1.0 doğrulaması
8 Ekim 2026'da 104 plugin testi ve 35 repo testi geçti. Paket, beceri, katalog, dil çifti, bağlantı ve kaynak kontrolleri geçti. Yeni regresyonlar source_path ile özgün PNG'yi koruyan inceleme, gerekli referansı erken reddetme, referans içeriğini sağlama, beklenen cevabı gizleyen senaryo girdileri, gerçek dosya/doğrulayıcı cache geçersizleştirme, seçici UI/kayıt yeniden kullanımı, bozuk profil tanısı, işlev/plan/yanıt bağlaması ve soru önkoşullarını kapsar. Özel inceleme protokolü 3.1 eski okuyucu kayıtlarını reddeder; public 3.0 handoff şeması ve son kapılar korunur.

Kullanıcının mevcut gpt-6.1-sol/xhigh ayarıyla gerçek yerel Codex sınaması iki olumlu sahiplik/hazırlık senaryosunu ve bir olumsuz çeviri kontrolünü tamamladı. Yerel beceri envanterinde tek etkin hedef vardı; tam SKILL.md hash'i bağlandı, gerçek yanıtlar incelendi ve runtime araçları kullanılmadı. İlk kabuk aracılı girişim doğru hedefi seçti; profil yürütme politikası nedeniyle dosyayı okuyamadı ve başarılı beceri uygulaması sayılmadı. Bu sınırlandırılmış beceri davranış kanıtıdır; üç okuyucu/iki tur handoff kapısı, Claude yürütmesi veya karşılaştırmalı sağlayıcı maliyeti doğrulaması değildir.

Üç yerel, 15 dosyalık/Excel içermeyen sentetik koşu önceki ZIP'in byte içeriğini aynen korurken codec süreçleri 27'den 6'ya indi. Süre ölçümü bu sentetik koşulara özeldir. Hash'ler, ölçülen medyanlar ve NOT_RUN sınırları `QUALIFICATION-3.1.toon` içindedir. Aşağıdaki TOKEN-EVAL.toon tarihsel 2.0.1 kanıtı olarak korunur. Hosted CI, tam handoff okuyucuları, Claude model yürütmesi, sağlayıcı maliyeti karşılaştırması ve SAP yürütmesi NOT_RUN'dır. Kaynak incelenebilir, commit edilmemiş bir branch'tir; GitHub yayını ima edilmez.

## 3.0.0 qualification
Yayın kabulü danışman/developer ayrımını, sıralı sınırlı seçenekleri, teknik karar readiness ayrımını, tüm dosya adı öneklerini, yerel dosya/belge/pointer kapanışını, ayrı atomik bağlı ZIP’leri ve değişmeyen/eski kontrol planını kapsar. Fonksiyonel/tarafsızlık/baseline/onay ve son okuyucu kapıları zorunludur. 3.0.0 gerçek LLM, görsel ve SAP qualification NOT_RUN; 2.0.1 token sonucu yeni sözleşmeye genellenmez. 2026-10-02 tarihinde 85 testlik tam plugin paketi geçti; son değişiklikler ardından 16 hedefli bağlam/sözleşme kontrolü ve altı etkilenen kayıtlı ZIP kontrolü geçti. Böylece 87 farklı plugin testi kapsandı. Repo yayın araçlarının 31 testi de geçti. Repo/paket/skill doğrulayıcıları, altı bağımsız skill paketi, strict TOON kural eşlemesi ve boşluk kontrolleri geçti. Claude strict manifest doğrulaması geçti; izole Codex plugin/read, kurulum veya model çağrısı olmadan localVersion 3.0.0 sürümünü keşfetti. Tam paketin ardından yalnızca değişen bağlam ve kayıtlı ZIP yolları tekrar test edildi. Son commit için GitHub CI ayrı kanıttır ve merge öncesi geçmelidir.

## 2.0.1 aday kanıtı
Yerel 2.0.1 yayın kontrolleri geçti: repo doğrulayıcıları, altı standalone yayın paketi, 71 plugin testi, 31 yayın/arşiv testi, standart kütüphaneli paket kontrolü ve skill frontmatter doğrulaması. Claude strict manifest kontrolü geçti; izole Codex `plugin/read`, kurulum veya model çağrısı olmadan localVersion 2.0.1 ve güncel ortak skill'i bildirdi. Hosted son commit CI ayrıdır; merge öncesi geçmelidir.

2026-10-01 tarihinde `tca-20260930-002` token audit'i, `x8` karşılaştırma koşusunda iki varyantın 20 örneğini üçer tekrar ile geçti (120 gerçek Codex koşusu). Bu, 2.0.1'e uygulanan keşif açıklamasının aynısıdır; sürüm ve dokümanlar ardından mekanik güncellendi. Ölçüm ve hash kayıtları `TOKEN-EVAL.toon` içindedir.

Görev kalitesi 1,00 korundu; kullanım/kullanmama doğruluğu 0,70 → 1,00 oldu. Başarılı görev maliyet endeksi 24013,9 → 19491,3 düştü (-%18,8; measured ağırlıklı token endeksi, para/fatura değildir). Araç çağrıları 4,73 → 4,03; başarısız çağrılar 1,80 → 1,20; tekrarlar 1,80 → 1,07 oldu. Açıklama tahmini 74 → 91 token arttı; gövde tahmini 1753 kaldı. Bazı yol hataları sürer. Kontrollü latency veya TOON–JSON benchmark'ı yapılmadı.

Runner: codex-cli 0.153.4; model/effort ayarı: default; served model: unknown. Qualification bu Codex ayarı ve test setiyle sınırlıdır; Claude model yürütmesi NOT_RUN. Auditor 1.5.1-codex.2'nin izole snapshot'ında Windows'a özgü deneme yolları, değişmeyen parent-plugin yardımcıları, native workspace sandbox grader ve aynı sabit resmi TOON 4.1.1 codec'i stdin üzerinden kullanıldı. Doğru/bozuk kontrol örnekleri geçti; ACL, auth ve izolasyon gevşetilmedi. Geçersiz altyapı denemeleri ve netleştirilen iki test çıktı etiketi aday karşılaştırmasından önce ayrıldı. Bu, handoff'un tam okuyucu/görsel/tenant teslim kapısı değildir.

## Özgün 2.0.0 kanıtı
Sürüm 2.0.0; sabit public kaynak `1e7717606641a8dbd0e390142a739acd157bae38`.
Hazırlanan dağıtım 71 yerel runtime/tohumlanmış hata testini ve 49 A-F kural eşlemesini geçti.
Claude Code 2.1.285 strict manifest kontrolünden geçti. Codex 0.153.4 `plugin/read`,
kurulum veya model çağrısı olmadan ortak skill'i izole profilde keşfetti.

Repo yayını İngilizce metadata, iki dilli doküman, kalıcı R-BYW kimlikleri,
katalog, private standalone yönlendirme/arşivleri ve CI bağlantısını uyarlar.
Runtime/checker/codec davranışı değişmez. Repo doğrulayıcıları geçti; 31 release-tooling ve 71 plugin testi yerelde geçti. Son commit CI sonucu ayrıdır ve merge öncesinde yeşil olmalıdır.

## Token sınırı
Özgün 2.0.0 repo girişi tiktoken 0.14.0 ile yerel sayımda 1258 o200k_base token'dı.
Yayın öncesindeki eş kural karşılaştırması, karma/TOON gövdesi yerine kısa Markdown seçti.
FS-TS verisi TOON kalır. Referanslar yalnız ihtiyaç olduğunda yüklenir.
Bu giriş dosyası sayımıdır; toplam maliyet, fatura, hız veya anlam üstünlüğü kanıtı değildir.
Özgün 2.0.0 yayını Claude tokenizer veya gerçek model karşılaştırması çalıştırmadı; sonraki Codex sonucu yukarıda kayıtlıdır.

## Çalıştırılmayan qualification
Gerçek üç okuyuculu semantik yürütme, gerçek görsel okuyucu ve SAP tenant,
aktivasyon, ATC, runtime, UAT NOT_RUN. Fixture'lar mekanik kontrol için güvenilir kayıtları
simüle eder; gerçek model/tenant kanıtı değildir. Gerçek handoff, bağımsız yürütme,
sahip teyidi ve güncel snapshot kapıları tamamlanana kadar engellenir.
Hosted Windows/Linux CI yerel kontrolden ayrıdır; merge öncesi yeşil olmalıdır.
