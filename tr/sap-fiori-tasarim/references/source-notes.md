# Kaynak ve tasarım notları

Kaynak kontrol tarihi: 2026-08-27 (SAP kaynakları), 2026-09-19 (paket yapısı). Bu dosya bakım içindir; çalışma zamanında okunmaz ve her tasarımda web'den yenilenmez. Çalışma zamanında canlı doğrulanacak bağlantılar [official-sources.md](official-sources.md) içindedir.

## Dayanaklar

- [SAP Fiori for Web](https://www.sap.com/design-system/fiori-design-web): floorplan, pattern, görsel sistem ve erişilebilirlik kuralları. Rehber sürümlüdür; skill sabit bir sürümü gerçek kabul etmez, hedefe uygun sürümlü sayfayı açtırır.
- [SAPUI5 Demo Kit](https://ui5.sap.com/): API Reference, developer best practices, Fiori elements ve test rehberleri. Örneğin çalışması pattern'in Fiori uyumlu olduğunu kanıtlamaz.
- [ABAP RAP](https://help.sap.com/docs/abap-cloud/abap-rap): business service, behavior definition, draft, side effects ve backend-driven UI özellikleri.
- [SAP AI Skills Library — sap-fiori-guidelines](https://github.com/SAP/ai-skills-library/tree/main/skills/sap-fiori-guidelines): SAP'nin deneysel Fiori AI skill'i; yararlı taban, insan doğrulaması gerektirir.
- [OpenAI — Build skills](https://learn.chatgpt.com/docs/build-skills): ayırt edici açıklama, gerektiğinde yüklenen yönerge ve isteğe bağlı referanslar.

## Yapı tercihleri

- **Yönerge biçimi (1.1.0):** `SKILL.md` emir kipinde, XML bölümleriyle (`<invariants>`, `<references>`, `<scope>`, `<evidence>`, `<contract>`, `<architecture>`, `<prototype>`, `<production>`, `<verification>`, `<self_check>`, `<delivery>`, `<resources>`), karar tablolarıyla ve iki iyi/kötü örnekle yazılır. Bölüm adları iş akışının sırasını izler.
- **İki tür referans:** alan referansları (yedi dosya, yaklaşık 75 KB) çalışma zamanında yalnız gerektiğinde okunur; Fiori/UI5/RAP bilgisi tek dosyaya sığdırılamayacak kadar geniştir ve her çağrıda yüklenmesi gereksiz maliyettir. `behavior-checks.md` ile bu dosya yalnız bakım içindir ve `SKILL.md` bunu açıkça söyler.
- **Sözleşme zinciri:** `abap-backend-contract.json` → `design-contract.json` → prototip/PNG/kod. Sözleşmeler SHA-256 ile bağlanır; doğrulayıcı zinciri kontrol eder. Amaç, PNG ile kodun ayrı ayrı "tasarlanıp" birbirinden kaymasını engellemektir.
- **Fail-closed doğrulama:** uyarı da kapıyı kapatır. Yanlış pozitif maliyeti bilinçli kabul edilmiştir; renk ve sabit metin denetimleri bu yüzden dar tutulur.
- **Tahmin yerine boşluk:** inspector lexical bir okuyucudur. Sınıflandıramadığı elementi, birden fazla servis veya entity set adayını seçmez; `gaps` içine yazar. `ready` sonucu yalnız boşluk kalmadığında verilir.
- **İki ayrı sürüm:** scaffold profili tooling ve `minUI5Version` değerini belirler; hedef runtime yalnız gözlenince yazılır. İkisinin aynı alana yazılması, şablon değerinin sistem bulgusu gibi raporlanmasına yol açıyordu.
- **Ortak çalışma zamanı:** betikler, şemalar, şablonlar ve testler iki dil paketinde bayt düzeyinde aynıdır; betik mesajları ve sözleşme anahtarları İngilizcedir. Depo testi bu eşitliği korur.

## Sınırlar

- Inspector ABAP derleyicisi, ADT aktivasyonu, service preview veya çalışma zamanı yetki kanıtı değildir; CDS/BDEF sözdiziminin tamamını kapsamaz. Yeni bir sözdizimi boşluğu bulunduğunda önce test ekle, sonra ayrıştırıcıyı genişlet; emin olunamayan durumda `gaps` üret.
- Tek bir gözden geçirilmiş profil vardır (`assets/version-profiles.json`). Şablon lockfile'ları o profile aittir; yeni profil kendi lockfile'ını gerektirir. Eski LTS runtime'lar için üretim scaffold'u, profil eklenene kadar reddedilir.
- Statik doğrulayıcı build, test, tarayıcı render'ı, Support Assistant ve gözle incelemenin yerini tutmaz.
- Davranış kontrollerinin (FD01–FD32) her ortamda geçtiği iddia edilmez; bunlar bakım senaryolarıdır. Skill bir modelin her oturumda kurala uyacağını garanti edemez.
- `official-sources.md` içindeki sürüm notları araştırma tarihine aittir; sürüm numaralı bağlantılar eskiyebilir.
- Skill SAP sistemine yazmaz; aktivasyon, transport ve deploy kapsam dışıdır.

## Dağıtım ve tek kaynak

- Bu depo (`public-skills`) skill'in tek kaynağıdır. Başka bir host'a (örneğin bir plugin içine) giden kopya elle düzenlenmez; `python .github/scripts/skills.py export tr/sap-fiori-tasarim --dest <klasör> [--name <skill-adı>] [--overlay <ek.md>]` ile üretilir. `--name` frontmatter adını ve hazır çağrıyı değiştirir; `--overlay` host'a özgü bölümü `SKILL.md` sonuna ekler. Export edilen kopya, kaynak sürümünü ve commit'ini `EXPORT-MANIFEST.json` içinde taşır.
- Host'a özgü kurallar (yetki kökü, araç geçidi, yazma izni) overlay dosyasında yaşar; çekirdek yönergeye taşınmaz.
- Şablonlar depo CI'ında ayrı bir iş akışıyla gerçekten kurulur, lint/typecheck/build edilir ve tarayıcıda sınanır; 1.2.0 şablonları bu yolla ve elle Chromium'da doğrulandı (prototipin altı durumu, fragment dialog, freestyle liste → ayrıntı ve not-found yolculukları, Fiori elements smoke testi).
- Ortak `scripts/`, `assets/` ve `tests/` iki dil paketinde bilinçli olarak yinelenir: depo kuralı her skill klasörünün tek başına kurulabilmesini ister. Eşitliği depo testi korur.
