# İşlemler

Kurulum, yardımcı araç çalıştırma, güvenli uyarlama veya somut doğrulama sorunu için oku. Komutlar çalışma dizini olarak skill kökünü varsayar; başka bir dizindeysen betiğin gerçek mutlak yolunu kullan. `--project` daima seçilen gerçek proje klasörüdür. Komutlara verilen belge içerikleri İngilizce kalır.

## Çalışma ortamı ve kurulum

Python 3.12+ ve PyYAML 6.x gerekir. Tek dış bağımlılık `scripts/requirements.txt` içinde açıklanır. PyYAML bulunan mevcut ortamı tercih et. Yeni/değişmiş yardımcı araçları önce yalıtılmış çalışma alanında çalıştır.

```powershell
python -X utf8 -B scripts/vault.py --project '<proje-koku>' --dry-run init --key ACME-ERP --install-guidance
python -X utf8 -B scripts/vault.py --project '<proje-koku>' init --key ACME-ERP --install-guidance
```

İkinci komut Vault'u oluşturur ve işaretli dokümantasyon bölümünü kökteki etkin talimat dosyasına birleştirir. İki kök talimat dosyası da varsa AGENTS.override.md kullanılır. Değişiklikten önce mevcut baytlar Vault altında yedeklenir. Global talimatlar veya Obsidian kaydı/ayarları değişmez. Geçerli daha alt talimat dosyalarını incele; gerçek çelişkileri proje kurulumunun parçası olarak çöz.

Obsidian'ın mevcut klasörü açma akışıyla `<proje-koku>/obsidian` alanını Vault olarak aç. İsteğe bağlı olarak ek konumunu `assets`, yeni not konumunu uygun kayıtlı klasör yapabilir, yerleşik Backlinks panelini açabilirsin. Bu UI ayarları Codex dosya yazımlarını denetlemez. Üretilen Vault; topluluk eklentisi, Dataview, dış veri tabanı veya arka plan servisi gerektirmez.

## Ekleme ve ayrıntılandırma

```powershell
python -X utf8 -B scripts/vault.py --project '<proje-koku>' add --kind development --id DEV-001 --slug purchase-extension --title 'Purchase Extension'
python -X utf8 -B scripts/vault.py --project '<proje-koku>' add --kind shared --id SHR-001 --slug validation-service --title 'Validation Service'
python -X utf8 -B scripts/vault.py --project '<proje-koku>' page --id DEV-001 --template design
python -X utf8 -B scripts/vault.py --project '<proje-koku>' page --id DEV-001 --template decision --record-id ADR-001 --title 'Validation contract ownership'
python -X utf8 -B scripts/vault.py --project '<proje-koku>' relate --from-id DEV-001 --to-id SHR-001
```

İsteğe bağlı şablonlar: design, process, objects, ui, verification, sources, handover, decision. Aynı işlemler `ARCH` için de çalışır. Ardından dönen sabit yollarda anlamlı içeriği yaz. Mevcut sayfalar korunur. Farkı incele; frontmatter, gezinme ve yönetilen işaretleri koru. Ekleme, yeniden adlandırma veya bağımlılıkları elle değiştirme sonrasında reindex çalıştır. Her bağımlılığın sözleşmesini ve gerekçesini sahip Overview kaydında açıkla.

Yardımcı araçta herhangi bir çıktı yolu seçtiren genel seçenek veya yıkıcı taşıma komutu bulunmaz. Elle içerik yazarken önce tam hedefin doğrulanmış Vault içinde olduğunu çözümle. Varlık adlarını güvenli ve kayıt klasörü içinde tut. Yazarken symlink/junction izleme. Geçici analiz raporlarını ikinci dokümantasyon ağacına dönüştürme.

## İlerlemeyi kaydetme ve devam

```powershell
python -X utf8 -B scripts/vault.py --project '<proje-koku>' checkpoint --id DEV-001 --event-id EVT-20260908-001 --status active --summary 'Documented the proposed validation contract; approval remains pending.' --next 'Review the contract with its owner.' --evidence 'See the proposed ADR and source references.'
python -X utf8 -B scripts/vault.py --project '<proje-koku>' context --id DEV-001
python -X utf8 -B scripts/vault.py --project '<proje-koku>' impact --id SHR-001
```

`--occurred-at` alanını yalnız kanıttan gelen, desteklenen ISO tarih/zamanıyla ekle. Alan yoksa olayın gerçekleşme zamanı bilinmez; kayıt zamanı gerçek UTC'dir. Aynı olay kimliğini aynı parametrelerle kullanmak işlem yapmaz; farklı parametreler yeni düzeltme kimliği gerektirir. İlgili olduğunda gerekçe, etki ve bağlantıları özet/kanıt alanına ekle. Uzun veya çok satırlı metinde karmaşık kabuk kaçışları yerine yerel UTF-8 dosyası ve sözleşmeyi koruyan doğrudan düzenlemeyi tercih et. Güvenilmeyen metni kabuk koduna yerleştirme.

Checkpoint yalnız Current State'in ilerleme bloğunu ve yaşam döngüsünü günceller, History'ye ekler. Kabul edilmiş kararları çıkarmaz, açık konuları kapatmaz, kanıtları doğrulamaz veya bütün metnin anlamını eşzamanlamaz. Ajan, etkilenen bölümleri aynı mantıksal değişiklikte güncellemelidir. done durumu tenant hazırlığı anlamına gelmez; tam kabul kapsamı ve kalan kapılar belirtilmelidir.

Context; seçilen Current State'i, bağımlılık kimliklerini, seçilen kayıt ve doğrudan bağımlılıklarının kaynak değişikliklerini ve bağlantıları döndürür. Varsayılan gövde sınırı 5.500 karakterdir; kesilmeyi açıkça bildirir. İşaretlenmişse dışarıda kalan metni oku. Bu, sınırlandırılmış okuma yardımcısıdır; kesin token hesabı değildir. Impact, kayıtlı tüketicileri geçişli olarak izler ve daha önce görülen düğümlerde durur.

## Parmak izleri

```powershell
python -X utf8 -B scripts/vault.py --project '<proje-koku>' source --id DEV-001 --source 'src/contract.json' --source 'specs/approved-requirement.pdf'
```

Yalnız seçilen özgün dosyaları inceledikten sonra çalıştır. Kayıt notlarının yanına gözlenen hash/zamanlarla `source-snapshots.json` yazar. Context/check gerçek dosyaları bu temelle karşılaştırır; değişiklikte veya kaybolmada uyarır. Anlamsal rolü, özgün URI/yolu, gerçek inceleme zamanını, otoriteyi ve desteklenen iddiaları Sources içinde açıkla. Dış URL'ler veya erişilemeyen tenant kanıtı için normal kaynak referansları kullan. Bayt parmak izi bir inceleme makbuzu değildir.

## Kontrol ve kurtarma

```powershell
python -X utf8 -B scripts/vault.py --project '<proje-koku>' reindex
python -X utf8 -B scripts/vault.py --project '<proje-koku>' check
python -X utf8 -B scripts/vault.py --project '<proje-koku>' check --audit-project
python -X utf8 -B scripts/test_vault.py
```

`check`, tüm Vault'u model bağlamına yüklemeden Markdown'ı araçla okur. Yönetilen notları, temel özellikleri, çekirdek sayfaları, kimlikleri, wikilink dosya/başlık/bloklarını, gezinmeyi, kaynak değişikliklerini ve türetilmiş dizinleri kontrol eder. İsteğe bağlı konum denetimi; derleme/çalışma ortamı klasörleri ve yapılandırılmış kaynak istisnaları dışında, Vault dışındaki sınıflandırılmamış Markdown'ı listeler. Dosya silmez veya taşımaz. Ek `allowed_markdown` desenlerini dar kapsamda değerlendir; geniş istisna ileride yanlış yere yazılan belgeleri gizler.

Bu doğrulayıcının her Markdown bağlantısını, doğal dildeki doğruluğu, tam iş kapsamını, Mermaid dilbilgisini/görünümünü, ekran görüntüsü kaynağını veya canlı Obsidian/SAP UI'ını kontrol ettiğini ima etme. Kabul kapsamına girdiklerinde ayrıca incele. Şablonlar bilinçli olarak parametrelidir ve not doğrulamasının dışındadır. Uzun Current State veya değişmiş kanıt uyarısı değerlendirme gerektirir; otomatik anlamsal hata değildir.

Yazımlar önceden kontrol edilir, proje kilidiyle sıraya alınır, okunan içerikle karşılaştırılır ve dosya başına değiştirilir. Yakalanan hatada geri alma, yalnız aracın kendi ve sonradan değişmemiş yazımlarına dokunur. Elektrik kesintisine karşı bir veri tabanı işlemi değildir. Beklenmedik süreç kesintisinden sonra eski kilidi elle temizleyip kontrolü tekrar çalıştırmadan önce `.documentation.lock` dosyasını (PID/zaman), gerçek dosyaları ve sürüm kontrolü farkını incele. Etkin başka yazıcının kilidini kaldırma veya insanın eşzamanlı değişikliklerini ezme.

## Mevcut içeriği uyarlama

1. Geçerli talimatları, hedef Vault yapısını ve dar kapsamlı ilgili kaynak envanterini oku. Otoriteyi belirle ve yol/kimlik eşlemesini hedef Vault'a kaydet. Özgün FS/TS ve depo geçmişini koru.
2. Yönetilmeyen dolu Vault'ta incelenmiş dosya düzenlemeleriyle açık uyarlama yap: yabancı içeriği ezmeden şema 1 `vault.json`, dört kök rehber, kayıtlı geliştirme/bileşen klasörleri ve temel notları ile şablon kopyalarını oluştur. Başlatıcı bu taşımayı otomatik yapmaz. Buradaki şemayı ve assets kaynaklarını kullan; normal doğrulayıcı sonrasında yapısal uyumu kontrol eder. Yönetilen Vault'ta kimlikleri tekrar kullanıp normal biçimde genişlet.
3. Her Markdown kaynağını yetkili özgün belge, araca/pakete ait kaynak dokümantasyonu, geçici analiz veya birleştirilecek geliştirme anlatısı olarak sınıflandır. Yalnız istenen kapsamda kopyala/bağla veya taşı; birleştirmeden önce mevcut hedef içeriğini incele. Özgün otoriteyi koru; geçmiş olay zamanını bu aktarımın kayıt zamanından ayır.
4. Bağlantı ve dizinleri yenile, uyarlanan Vault'u kontrol et, ilgili diyagram/ekran görüntülerini incele ve çözülememiş geçmişi bildir. Çelişki veya erişilemeyen kaynak açık konudur. Başlangıç iskeletini içe aktarılmış proje geçmişi diye sunma.

İncelenmiş uyarlama için en küçük tanımlayıcı (yalnız gerekçeli kaynak istisnaları ekle):

```json
{"schema_version": 1, "project_key": "ACME-ERP", "language": "en", "allowed_markdown": ["AGENTS.md", "AGENTS.override.md", "README.md"]}
```
