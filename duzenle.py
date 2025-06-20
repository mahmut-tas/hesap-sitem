import os
import re
from google.cloud import translate_v2 as translate
from bs4 import BeautifulSoup
import unicodedata
import shutil

# --- Yapılandırma Başlangıcı ---
# Google Cloud servis hesap anahtarınızın tam yolu
# Burayı kendi JSON anahtar dosyanızın yoluna göre güncelleyin.
GOOGLE_APPLICATION_CREDENTIALS_PATH = r"C:\Users\suuser\Desktop\hesapkolik-multilang-d6ca51078a3a.json"

# Web sitesinin kök klasörü (hem Türkçe hem de İngilizce dosyaları içeren ana klasör)
# Burayı web sitenizin ana klasörünün yoluna göre güncelleyin (örn: C:\MyWebsite\hesap-sitem)
SITE_ROOT_PATH = r'C:\Users\suuser\Desktop\hesap-sitem'

# İngilizce dosyalarının bulunduğu alt klasörün adı
EN_SUBFOLDER_NAME = 'en'
# İngilizce klasörünün tam yolu
EN_FOLDER_PATH = os.path.join(SITE_ROOT_PATH, EN_SUBFOLDER_NAME)

# Hedef çeviri dili
TARGET_LANGUAGE = 'en'

# --- MANUEL ÇEVİRİ HARİTASI ---
# Bu harita, Google Translate API'nin yanlış çevirdiği veya özel olarak kalmasını istediğiniz
# Türkçe terimlerin URL dostu (slugified) İngilizce karşılıklarını içerir.
# Ayrıca HTML başlıkları için de kullanılabilir.
# Format: 'türkçe-slug': 'english-slug' veya 'türkçe-orijinal-başlık': 'english-başlık-metni'
# Buradaki terimler, dosya/dizin adlarının veya başlıkların SLUGIFIED halleri olmalı!
# Örneğin, "Hakkımızda" başlıklı bir sayfanız varsa ve slugify hali "hakkimizda" ise,
# karşılığı "about-us" olabilir.
MANUAL_TRANSLATION_MAP = {
    # Kök Dizinler ve Genel Sayfalar (Zaten İngilizce olanlar veya özel isimler)
    'en': 'en',
    'index': 'index',
    'about-us': 'about-us',
    'hakkimizda': 'about-us', # Türkçe dosya/dizin adından eşleme için
    'contact': 'contact',
    'iletisim': 'contact', # Türkçe dosya/dizin adından eşleme için
    'privacy-policy': 'privacy-policy',
    'gizlilik-politikasi': 'privacy-policy', # Türkçe dosya/dizin adından eşleme için
    'terms-of-use': 'terms-of-use',
    'kullanim-sartlari': 'terms-of-use', # Türkçe dosya/dizin adından eşleme için
    'age-calculator': 'age-calculator',
    'yas-hesaplayici': 'age-calculator',
    'percentage-calculator': 'percentage-calculator',
    'yuzde-hesaplayici': 'percentage-calculator',
    'interest-calculator': 'interest-calculator',
    'faiz-hesaplayici': 'interest-calculator',
    'unit-converter': 'unit-converter',
    'birim-cevirici': 'unit-converter',
    'engineering-calculations': 'engineering-calculations',
    'muhendislik-hesaplamalari': 'engineering-calculations',
    'health-calculations': 'health-calculations',
    'saglik-hesaplamalari': 'health-calculations',
    'education-calculations': 'education-calculations',
    'egitim-hesaplamalari': 'education-calculations',
    'daily-life-calculations': 'daily-life-calculations',
    'gunluk-hayat-hesaplamalari': 'daily-life-calculations',

    # Dizin İsimleri için Spesifik Manuel Çeviriler (Slugify edilmiş halleriyle)
    'muhendislik': 'engineering',
    'cevre': 'environmental',
    'insaat': 'civil',
    'makine': 'mechanical',
    'elektrik-elektronik': 'electrical-electronic',
    'tekstil': 'textile',
    'saglik': 'health',
    'egitim': 'education',
    'yapi': 'structure', # İnşaat altındaki 'yapi'
    'geoteknik': 'geotechnical', # İnşaat altındaki 'geoteknik'
    'hidrolik': 'hydraulic', # İnşaat altındaki 'hidrolik'
    'ulastirma': 'transportation', # İnşaat altındaki 'ulastirma'
    'kimya': 'chemical',

    # Dosya İsimleri ve İç Linklerdeki Terimler için Manuel Çeviriler (Slugify edilmiş halleriyle)
    'boi-koi-orani': 'bod-cod-ratio',
    'akm-yuku': 'suspended-solids-load',
    'desarj-standarti-kontrolu': 'discharge-standard-compliance',
    'ph-dengeleme': 'ph-balancing',
    'baca-gazi-emisyonu': 'flue-gas-emission',
    'hava-kalitesi-indeksi': 'air-quality-index',
    'kati-atik-uretim-hizi': 'solid-waste-production-rate',
    'geri-donusum-verimliligi': 'recycling-efficiency',
    'gunes-paneli-verim': 'solar-panel-efficiency',
    'karbon-ayak-izi': 'carbon-footprint',
    'ohm-kanunu': 'ohm-law',
    'seri-paralel-direnc': 'series-parallel-resistance',
    'elektrik-gucu': 'electric-power',
    'kapasitor-sarj-desarj': 'capacitor-charge-discharge',
    'rc-rl-zaman-sabiti': 'rc-rl-time-constant',
    'frekans-periyot': 'frequency-period',
    'filtre-kesim-frekansi': 'filter-cutoff-frequency',
    'direnc-renk-kodu': 'resistor-color-code',
    'led-direnc': 'led-resistor',
    'voltaj-bolucu': 'voltage-divider',
    'gerilim-dusumu': 'voltage-drop',
    'guc-faktoru': 'power-factor',
    'beton-hacmi-malzeme': 'concrete-volume-materials',
    'tugla-blok-duvar': 'brick-block-wall',
    'boya-miktari-hesaplayici': 'paint-quantity-calculator',
    'fayans-seramik': 'tile-ceramic',
    'kiris-egilme-kesme': 'beam-bending-shear',
    'kiris-sehim': 'beam-deflection',
    'atalet-momenti': 'moment-of-inertia',
    'kisa-kolon-kapasitesi': 'short-column-capacity',
    'zemin-tasima-kapasitesi': 'soil-bearing-capacity',
    'zemin-oturmasi': 'soil-settlement',
    'boru-basinc-dususu': 'pipe-pressure-drop',
    'acik-kanal-akisi': 'open-channel-flow',
    'yatay-kurp': 'horizontal-curve',
    'kutle-denkligi': 'mass-balance',
    'enerji-denkligi': 'energy-balance',
    'reaktor-hacmi': 'reactor-volume',
    'molarite-hesaplama': 'molarity-calculation',
    'yogunluk-hesaplama': 'density-calculation',
    'ph-hesaplama': 'ph-calculation',
    'isi-transferi': 'heat-transfer',
    'yuzde-kutle-hesaplama': 'percentage-mass-calculation',
    'gaz-yogunlugu': 'gas-density',
    'normal-gerilme': 'normal-stress',
    'kesme-gerilme': 'shear-stress',
    'egilme-gerilmesi': 'bending-stress',
    'burulma-gerilmesi': 'torsional-stress',
    'emniyet-faktoru': 'safety-factor',
    'burkulma-yuku': 'buckling-load',
    'isi-esanjörü-lmtd': 'heat-exchanger-lmtd',
    'sogutma-yuku': 'cooling-load',
    'pompa-gucu': 'pump-power',
    'reynolds-sayisi': 'reynolds-number',
    'sertlik-donusumu': 'hardness-conversion',
    'iplik-numarasi': 'yarn-count',
    'boya-recetesi': 'dye-recipe',
    'dokuma-verimlilik': 'weaving-efficiency',
    'elyaf-karisim': 'fiber-blend',
    'cozgu-atki-miktari': 'warp-weft-amount',
    'iplik-uzunlugu': 'yarn-length',
    'baski-pati': 'print-paste',
    'kumas-fire': 'fabric-waste',
    'lab-boyama': 'lab-dyeing',
    'kumas-cekme-orani': 'fabric-shrinkage-rate',
    'kumas-gramaji': 'fabric-weight',
    'kumas-sikiligi': 'fabric-tightness',
    'gpa-hesaplama': 'gpa-calculation',
    'toefl-hesaplama': 'toefl-calculation',
    'yks-hesaplama': 'yks-calculation',
    'ielts-hesaplama': 'ielts-calculation',
    'gre-hesaplama': 'gre-calculation',
    'gmat-hesaplama': 'gmat-calculation',
    'yuzde-basari-orani': 'success-rate-percentage',
    'yakit-tuketimi-hesaplayici': 'fuel-consumption-calculator',
    'elektrikli-arac-sarj-maliyeti': 'electric-vehicle-charging-cost',
    'ampul-enerji-hesaplayici': 'bulb-energy-calculator',
    'butce-planlayici': 'budget-planner',
    'yemek-porsiyon-hesaplayici': 'food-portion-calculator',
    'fatura-gider-takibi': 'invoice-expense-tracker',
    'klima-enerji-tuketimi': 'air-conditioner-energy-consumption',
    'indirim-hesaplayici': 'discount-calculator',
    'adet-dongusu-takibi': 'menstrual-cycle-tracker',
    'target-pulse-zone': 'target-heart-rate-zone',
    'daily-calorie-requirement-calculator': 'daily-calorie-needs-calculator',
    'daily-water-requirement': 'daily-water-intake',
    'daily-carbohydrate-requirement': 'daily-carbohydrate-needs',
    'daily-protein-requirement': 'daily-protein-needs',
    # Başlık çevirileri için örnek girdiler (eğer başlık metninin slug'ı ile eşleşirse):
    'muhendislik-hesaplamalari': 'Engineering Calculations',
    'cevre-muhendisligi-hesaplamalari': 'Environmental Engineering Calculations',
    'enerji-denkligi': 'Energy Balance Calculation', # Örnek başlık çevirisi
}

# --- Yapılandırma Sonu ---

# --- Yardımcı Fonksiyonlar ---
def slugify(text):
    """Metni URL dostu bir sluga dönüştürür."""
    text = str(text).lower()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def translate_text(text):
    """Google Translate API kullanarak metni çevirir.
    Manuel haritayı da kontrol eder."""
    if not text or text.strip() == '':
        return ""
    
    # Metnin slug'ını manuel haritada ara (başlıklar veya genel terimler için)
    text_slug = slugify(text)
    if text_slug in MANUAL_TRANSLATION_MAP:
        # Eğer manuel haritada metnin kendisi veya slug'ı için bir çeviri varsa, onu kullan.
        # Burada slugified_text olarak değil, orijinal çevrilmiş metin olarak döndürmeliyiz
        # çünkü bu fonksiyon genel metin çevirisi için kullanılıyor.
        return MANUAL_TRANSLATION_MAP[text_slug]

    # Eğer manuel haritada yoksa, API ile çevir
    if len(text) > 500:
        print(f"Uyarı: Çok uzun metin çevirisi atlanıyor (uzunluk: {len(text)}): {text[:100]}...")
        return text # Çok uzunsa çevirme, orijinalini döndür

    try:
        result = translate_client.translate(text, target_language=TARGET_LANGUAGE)
        return result['translatedText']
    except Exception as e:
        print(f"Hata çevirirken '{text}': {e}")
        return text # Çeviri hatası durumunda orijinal metni döndür

def get_translated_slug_for_path_segment(path_segment_raw):
    """Verilen URL yol segmentini (dosya adı veya dizin adı) çevirir ve slugify yapar.
    Sadece sluglar için manuel haritayı kontrol eder."""
    base_name, ext = os.path.splitext(path_segment_raw)
    
    # Manuel çeviri haritasında slugified base_name olarak varsa, onu kullan
    slugified_base_name = slugify(base_name)
    if slugified_base_name in MANUAL_TRANSLATION_MAP:
        return MANUAL_TRANSLATION_MAP[slugified_base_name] + ext
            
    # Eğer manuel haritada yoksa, API ile çevir ve slugify yap
    # Bu adımda API'ye giden base_name zaten İngilizce ise, API aynı İngilizce terimi döndürebilir.
    # Önemli olan bu terimin Türkçe kökenli olup olmamasıdır. Ancak bu betikte varsayım,
    # 'en' klasöründeki mevcut isimlerin Türkçe orijinalliğini taşıyor olmasıdır.
    translated_name = translate_text(base_name) # translate_text burada aslında metni çeviriyor
    return slugify(translated_name) + ext

def is_internal_link_to_process(href):
    """Bir href'in sitenin kendi HTML dosyasına veya statik dosyalarına işaret eden dahili bir link olup olmadığını kontrol eder."""
    # Harici linkler, çapa linkleri, mailto, tel, javascript linkleri dışarıda bırakılır.
    if not href or href.startswith(('#', 'mailto:', 'tel:', 'javascript:')) or \
       href.startswith(('http://', 'https://', '//')):
        return False
    return True

# --- Google Translate API İstemcisini Başlatma ve Bağlantı Testi ---
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS_PATH
try:
    translate_client = translate.Client()
    test_translation = translate_text("Merhaba")
    print(f"Google Translate API bağlantısı başarılı. Test çevirisi: 'Merhaba' -> '{test_translation}'")
except Exception as e:
    print(f"HATA: Google Translate API bağlantısı veya kimlik doğrulama sorunu: {e}")
    print("Lütfen GOOGLE_APPLICATION_CREDENTIALS_PATH'in doğru olduğundan ve API anahtarınızın geçerli olduğundan emin olun.")
    exit()

# --- Ana İşlem Fonksiyonu ---
def rename_and_update_en_folder():
    """
    'en' klasörü altındaki dosya ve dizin isimlerini çevirir,
    HTML içerisindeki linkleri ve BAŞLIKLARI günceller ve 301 yönlendirme haritası oluşturur.
    Orijinal Türkçe dosyalar değiştirilmez.
    """
    
    if not os.path.exists(EN_FOLDER_PATH):
        print(f"HATA: '{EN_FOLDER_PATH}' klasörü bulunamadı. Lütfen 'SITE_ROOT_PATH' ve 'EN_SUBFOLDER_NAME' ayarlarını kontrol edin.")
        return

    # Bu harita, eski mutlak EN dosya/dizin yolu -> yeni mutlak EN dosya/dizin yolu eşlemesini tutar.
    # Örn: C:\...\hesap-sitem\en\eski-dizin\eski-dosya.html -> C:\...\hesap-sitem\en\new-directory\new-file.html
    file_path_rename_map = {} 
    
    # Bu harita, eski URL -> yeni URL eşlemesini tutar. Hem ana TR URL'leri hem de eski EN URL'leri için.
    # Örn: /hakkimizda.html -> /en/about-us.html
    # Örn: /en/eski-dizin/eski-dosya.html -> /en/new-directory/new-file.html
    url_redirect_map = {}

    print(f"--- '{EN_FOLDER_PATH}' İçindeki Dizin ve Dosya Adları Belirleniyor ve Çevriliyor ---")

    # 1. Aşama: EN klasörü içindeki tüm mevcut dizin ve dosya adlarının çevrilmiş halini belirle
    # ve rename_map ile redirect_map'i oluştur.
    
    all_paths_in_en = []
    # topdown=False ile dizinleri içten dışa doğru sıralıyoruz, bu yeniden adlandırma için kritik.
    for root, dirs, files in os.walk(EN_FOLDER_PATH, topdown=False):
        for d in dirs:
            all_paths_in_en.append((os.path.join(root, d), True)) # True for directory
        for f in files:
            # Sadece HTML dosyalarını ve statik dosyaları hedefle (statikler için sadece yol eşleşmesi)
            if f.lower().endswith(".html") or any(f.lower().endswith(ext) for ext in ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico']):
                all_paths_in_en.append((os.path.join(root, f), False)) # False for file

    # Yolları, en derin dizinlerden başlayarak ve dosyaları dizinlerden önce işleyecek şekilde sırala
    # shutil.move bir dizini taşıdığında içindekileri de taşır, bu nedenle dosyaların önce yeniden adlandırılması daha güvenlidir.
    # Sıralama anahtarı: (is_dir, -len(path)) -> Önce dosyalar (False < True), sonra uzun yollar (derinlik)
    all_paths_in_en.sort(key=lambda x: (x[1], -len(x[0])))

    # İlk döngüde sadece yeniden adlandırma eşlemelerini ve nihai yeni yolları belirleyeceğiz.
    # Fiziksel yeniden adlandırma ikinci döngüde olacak.
    for original_path_in_en, is_dir in all_paths_in_en:
        
        # 'en' klasöründen sonraki göreceli yolu al (örn: 'muhendislik/kimya/enerji-denkligi.html')
        relative_path_after_en = os.path.relpath(original_path_in_en, EN_FOLDER_PATH).replace('\\', '/')
        
        # Segmentlere ayır
        segments_to_translate = relative_path_after_en.split('/')
        
        translated_segments = []
        for segment in segments_to_translate:
            if segment: # Boş segmentleri atla
                # Her bir segmenti çevir ve slugify yap
                translated_segments.append(get_translated_slug_for_path_segment(segment))
            else:
                translated_segments.append(segment) # Boş kalmalı

        # Yeni İngilizce yolunu oluştur (EN_FOLDER_PATH altında)
        new_abs_path = os.path.join(EN_FOLDER_PATH, *translated_segments)
        
        # --- Çakışma kontrolü ve benzersiz isim oluşturma ---
        counter = 1
        temp_new_abs_path = new_abs_path
        # Eğer yeni yol zaten varsa VE bu yol orijinal yolun kendisi değilse (yani bir çakışma)
        while os.path.exists(temp_new_abs_path) and os.path.normpath(temp_new_abs_path) != os.path.normpath(original_path_in_en):
            name_without_ext, ext = os.path.splitext(os.path.basename(new_abs_path))
            # Eğer dosya ise uzantıyı koru, dizinse uzantısı olmaz
            if is_dir:
                temp_new_abs_path = os.path.join(os.path.dirname(new_abs_path), f"{name_without_ext}-{counter}")
            else:
                temp_new_abs_path = os.path.join(os.path.dirname(new_abs_path), f"{name_without_ext}-{counter}{ext}")
            counter += 1
        new_abs_path = temp_new_abs_path

        # Eğer orijinal yol ile yeni yol farklıysa, eşlemeye ekle
        if os.path.normpath(original_path_in_en) != os.path.normpath(new_abs_path):
            file_path_rename_map[original_path_in_en] = new_abs_path
            print(f"  Eşleme belirlendi: {os.path.relpath(original_path_in_en, SITE_ROOT_PATH)} -> {os.path.relpath(new_abs_path, SITE_ROOT_PATH)}")
        else:
            file_path_rename_map[original_path_in_en] = original_path_in_en # Değişmeyenleri de kaydet
            print(f"  Adı değişmeyecek: {os.path.relpath(original_path_in_en, SITE_ROOT_PATH)}")

    print("\n--- 'en' Klasörü İçindeki Dizin ve Dosya Adları Yeniden Adlandırılıyor ---")
    # 2. Aşama: Belirlenen eşlemeleri kullanarak dosyaları ve dizinleri fiziksel olarak yeniden adlandır.
    # Yolları, en derinlerden başlayarak (ters sıralama) yeniden adlandırmak önemlidir,
    # çünkü bir üst dizin taşınmadan önce altındaki tüm öğelerin güncel ismine sahip olması gerekir.
    # Sıralama anahtarı: (is_dir, len(path)) -> önce dosyalar (False < True), sonra kısa yollar (sığdan derine)
    # Bu sıralama, dosyaları yeniden adlandırdıktan sonra üst dizinleri taşımamızı sağlar.
    
    # file_path_rename_map'teki öğeleri sırala: Önce dosyalar, sonra dizinler, uzun yollardan kısa yollara
    sorted_paths_to_rename = []
    for original_p, new_p in file_path_rename_map.items():
        is_dir = os.path.isdir(original_p) # Orijinal yolun tipini kontrol et
        if os.path.normpath(original_p) != os.path.normpath(new_p):
            sorted_paths_to_rename.append((original_p, new_p, is_dir))
    
    # Sıralama mantığı: Önce dosyalar (is_dir=False), sonra dizinler (is_dir=True).
    # Aynı tipte ise, yolların uzunluğuna göre ters sıra (derin yollar önce).
    sorted_paths_to_rename.sort(key=lambda x: (x[2], -len(x[0])), reverse=True)


    for original_abs_path, new_abs_path, is_dir in sorted_paths_to_rename:
        if os.path.normpath(original_abs_path) != os.path.normpath(new_abs_path):
            try:
                # Sadece mevcut olan dosyaları/dizinleri yeniden adlandır.
                if os.path.exists(original_abs_path):
                    # Hedef dizinin var olduğundan emin ol (yeni dizin oluşacaksa)
                    os.makedirs(os.path.dirname(new_abs_path), exist_ok=True)
                    shutil.move(original_abs_path, new_abs_path)
                    print(f"Yeniden adlandırıldı: {os.path.relpath(original_abs_path, SITE_ROOT_PATH)} -> {os.path.relpath(new_abs_path, SITE_ROOT_PATH)}")
                else:
                    print(f"UYARI: {os.path.relpath(original_abs_path, SITE_ROOT_PATH)} zaten taşınmış veya bulunamadı. Atlanıyor.")
            except Exception as e:
                print(f"HATA oluştu yeniden adlandırılırken {os.path.relpath(original_abs_path, SITE_ROOT_PATH)} -> {os.path.relpath(new_abs_path, SITE_ROOT_PATH)}: {e}")
        else:
            print(f"Yeniden adlandırma yapılmadı (yol aynı): {os.path.relpath(original_abs_path, SITE_ROOT_PATH)}")

    # 3. Aşama: URL Yönlendirme Haritasını Oluştur (301 Yönlendirmeleri İçin)
    # Bu harita hem Türkçe -> İngilizce hem de eski İngilizce -> yeni İngilizce yönlendirmeleri içerecek.
    print("\n--- URL Yönlendirme Haritası Oluşturuluyor (301 Yönlendirmeleri İçin) ---")

    # Mevcut Türkçe URL'lerden yeni İngilizce URL'lere yönlendirme
    for root, dirs, files in os.walk(SITE_ROOT_PATH):
        # 'en' klasörünü ve içindekileri atla, sadece Türkçe kök dizinindeki öğeleri işle
        if os.path.commonpath([root, EN_FOLDER_PATH]) == EN_FOLDER_PATH and root != SITE_ROOT_PATH:
            continue

        # Dizinin kendisi için de yönlendirme oluştur (örneğin /muhendislik/ -> /en/engineering/)
        # SITE_ROOT_PATH'ten itibaren göreceli yol
        relative_dir_from_site_root_tr = os.path.relpath(root, SITE_ROOT_PATH).replace('\\', '/')
        
        # Türkçe dizin adının (slug olarak) karşılığını bul (manuel haritadan veya API'den)
        translated_dir_segments = []
        for segment in relative_dir_from_site_root_tr.split('/'):
            if segment and segment != '.': # Boş segmentleri ve '.' atla
                translated_dir_segments.append(get_translated_slug_for_path_segment(segment).replace('.html', ''))

        # Türkçe dizin URL'si
        old_tr_dir_url = '/' + relative_dir_from_site_root_tr
        if old_tr_dir_url == '/.': old_tr_dir_url = '/' # Kök dizin özel durumu
        if not old_tr_dir_url.endswith('/'): old_tr_dir_url += '/'

        # Yeni İngilizce dizin URL'si
        new_en_dir_url = f'/{EN_SUBFOLDER_NAME}/' + '/'.join(translated_dir_segments)
        if not new_en_dir_url.endswith('/'): new_en_dir_url += '/'
        
        if old_tr_dir_url != new_en_dir_url:
             url_redirect_map[old_tr_dir_url] = new_en_dir_url

        for file_name in files:
            if file_name.lower().endswith(".html"):
                original_turkish_full_path = os.path.join(root, file_name)
                
                # Türkçe dosyanın URL'si (eski URL)
                old_tr_file_url = '/' + os.path.relpath(original_turkish_full_path, SITE_ROOT_PATH).replace('\\', '/')
                
                # Dosya adı segmentini çevir (örn: enerji-denkligi.html -> energy-balance.html)
                translated_file_segment = get_translated_slug_for_path_segment(file_name)
                
                # Yeni İngilizce dosya URL'si için dizin yolunu oluştur
                # Bu, yukarıda oluşturduğumuz translated_dir_segments'i kullanacak.
                if not translated_dir_segments: # Kök dizindeki HTML'ler için
                    new_en_file_url = f'/{EN_SUBFOLDER_NAME}/{translated_file_segment}'
                else:
                    new_en_file_url = f'/{EN_SUBFOLDER_NAME}/' + '/'.join(translated_dir_segments) + '/' + translated_file_segment

                # Index.html özel durumu
                if old_tr_file_url.lower().endswith('/index.html'):
                    old_tr_file_url = old_tr_file_url.replace('/index.html', '/')
                if new_en_file_url.lower().endswith('/index.html'):
                    new_en_file_url = new_en_file_url.replace('/index.html', '/')
                
                # Dosya URL'leri için trailing slash'i kaldır
                old_tr_file_url = old_tr_file_url.rstrip('/')
                new_en_file_url = new_en_file_url.rstrip('/')

                if old_tr_file_url != new_en_file_url:
                    url_redirect_map[old_tr_file_url] = new_en_file_url

    # EN klasörü içindeki eski İngilizce URL'lerden yeni İngilizce URL'lere yönlendirme
    # Bu, dosya yeniden adlandırmaları sonrası oluşan eski EN URL'lerini yeni EN URL'lerine yönlendirir.
    # file_path_rename_map'i kullanırız çünkü o, fiziksel olarak değişen tüm yolları tutar.
    for original_abs_path_before_rename, final_abs_path_after_rename in file_path_rename_map.items():
        # Sadece HTML dosyaları veya dizinler için URL eşlemesi oluştur
        if not final_abs_path_after_rename.lower().endswith(".html") and not os.path.isdir(final_abs_path_after_rename):
            continue

        old_en_relative_url = '/' + os.path.relpath(original_abs_path_before_rename, SITE_ROOT_PATH).replace('\\', '/')
        new_en_relative_url = '/' + os.path.relpath(final_abs_path_after_rename, SITE_ROOT_PATH).replace('\\', '/')

        # Index.html özel durumu
        if old_en_relative_url.lower().endswith('/index.html'):
            old_en_relative_url = old_en_relative_url.replace('/index.html', '/')
        if new_en_relative_url.lower().endswith('/index.html'):
            new_en_relative_url = new_en_relative_url.replace('/index.html', '/')
        
        # Trailing slash yönetimi: Dizinse '/' ekle, dosyaysa '/' kaldır
        if os.path.isdir(final_abs_path_after_rename) and not old_en_relative_url.endswith('/'):
            old_en_relative_url += '/'
        elif not os.path.isdir(final_abs_path_after_rename) and old_en_relative_url.endswith('/'):
            old_en_relative_url = old_en_relative_url.rstrip('/')
        
        if os.path.isdir(final_abs_path_after_rename) and not new_en_relative_url.endswith('/'):
            new_en_relative_url += '/'
        elif not os.path.isdir(final_abs_path_after_rename) and new_en_relative_url.endswith('/'):
            new_en_relative_url = new_en_relative_url.rstrip('/')

        if old_en_relative_url != new_en_relative_url:
            url_redirect_map[old_en_relative_url] = new_en_relative_url

    print("\n--- HTML İçindeki Linkler ve BAŞLIKLAR Güncelleniyor ---")
    # 4. Aşama: HTML İçeriğindeki Linkleri ve BAŞLIKLARI Güncelle
    # Bu döngü, yeniden adlandırılmış ve güncel dosya yollarını kullanarak çalışır.
    # Bu yüzden 'file_path_rename_map'ten değil, doğrudan 'EN_FOLDER_PATH'i tekrar tarayarak yapıyoruz.
    for root, _, files in os.walk(EN_FOLDER_PATH):
        for file_name in files:
            if file_name.lower().endswith(".html"):
                file_path = os.path.join(root, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    soup = BeautifulSoup(content, 'html.parser')
                    changes_made_in_file = False # Genel bir değişiklik bayrağı

                    # HTML lang özelliğini güncelle
                    if soup.html and soup.html.get('lang') != TARGET_LANGUAGE:
                        soup.html['lang'] = TARGET_LANGUAGE
                        changes_made_in_file = True
                        print(f"  '{os.path.relpath(file_path, SITE_ROOT_PATH)}' için HTML lang='{TARGET_LANGUAGE}' olarak güncellendi.")

                    # BAŞLIK (Title) çevirisi
                    if soup.title and soup.title.string:
                        original_title = soup.title.string.strip()
                        if original_title:
                            # Önce manuel haritada başlığın slug'ı var mı bak
                            title_slug = slugify(original_title)
                            translated_title_text = MANUAL_TRANSLATION_MAP.get(title_slug)

                            if not translated_title_text: # Manuelde yoksa API ile çevir
                                translated_title_text = translate_text(original_title)
                            
                            # Eğer çeviri orijinalden farklıysa güncelle
                            if translated_title_text and translated_title_text != original_title:
                                soup.title.string = translated_title_text
                                changes_made_in_file = True
                                print(f"  '{os.path.relpath(file_path, SITE_ROOT_PATH)}' için başlık güncellendi: '{original_title}' -> '{translated_title_text}'")
                            else:
                                print(f"  '{os.path.relpath(file_path, SITE_ROOT_PATH)}' için başlık değişmedi veya zaten çevriliydi: '{original_title}'")
                        else:
                            print(f"  '{os.path.relpath(file_path, SITE_ROOT_PATH)}' için boş başlık. Çevrilmedi.")

                    # Linkleri güncelle
                    for tag in soup.find_all(['a', 'link'], href=True):
                        original_href = tag['href']
                        
                        if is_internal_link_to_process(original_href):
                            full_target_url_from_href = None

                            if original_href.startswith('/'): # Mutlak link (örn: /en/muhendislik/kimya/enerji-denkligi.html)
                                full_target_url_from_href = original_href
                            else: # Göreceli link (örn: ../../enerji-denkligi.html)
                                # Mevcut İngilizce dosyanın SITE_ROOT_PATH'e göre göreceli yolu
                                current_file_relative_path_from_site_root = os.path.relpath(file_path, SITE_ROOT_PATH).replace('\\', '/')
                                # Linkin hedeflediği yolu hesapla (SITE_ROOT_PATH'e göre)
                                target_relative_path_from_site_root = os.path.normpath(os.path.join(os.path.dirname(current_file_relative_path_from_site_root), original_href)).replace('\\', '/')
                                full_target_url_from_href = '/' + target_relative_path_from_site_root

                            if full_target_url_from_href:
                                # Trailing slash normalizasyonu için yardımcı fonksiyon (daha temiz olması için)
                                def normalize_url_for_map_key(url_path):
                                    base, ext = os.path.splitext(os.path.basename(url_path))
                                    if not ext and not url_path.endswith('/'): # Uzantısı yoksa ve / ile bitmiyorsa (dizin olabilir)
                                        return url_path + '/'
                                    elif ext and url_path.endswith('/'): # Uzantısı varsa ve / ile bitiyorsa (dosya)
                                        return url_path.rstrip('/')
                                    return url_path

                                # URL'yi map anahtar formatına normalleştir
                                normalized_original_target_url = normalize_url_for_map_key(full_target_url_from_href)
                                
                                # Yönlendirme haritasından yeni hedef URL'yi bul
                                resolved_new_full_url = url_redirect_map.get(normalized_original_target_url)
                                
                                # Eğer doğrudan map'te yoksa, bu bir sorun veya statik dosya olabilir.
                                if not resolved_new_full_url:
                                    # print(f"  DEBUG: Link için yönlendirme bulunamadı: {normalized_original_target_url} (orijinal: {original_href})")
                                    continue # Bulunamadıysa değiştirme

                                # Şimdi resolved_new_full_url'ı, mevcut dosyanın konumuna göre göreceli hale getir
                                current_file_relative_dir_from_site_root_clean = os.path.dirname(os.path.relpath(file_path, SITE_ROOT_PATH)).replace('\\', '/')
                                
                                # Hedef URL'nin SITE_ROOT_PATH'e göre göreceli yolu (en/path/to/file.html)
                                target_relative_path_for_relpath = resolved_new_full_url.lstrip('/').rstrip('/')
                                
                                # Eğer hedef '/' ise (kök index.html), onu 'en/index.html' olarak kabul et
                                if target_relative_path_for_relpath == EN_SUBFOLDER_NAME:
                                    target_relative_path_for_relpath = os.path.join(EN_SUBFOLDER_NAME, 'index.html')
                                # Eğer hedef sadece 'en/' ise, 'en/index.html' olarak kabul et
                                elif target_relative_path_for_relpath == EN_SUBFOLDER_NAME + '/':
                                    target_relative_path_for_relpath = os.path.join(EN_SUBFOLDER_NAME, 'index.html')


                                new_href_calculated = os.path.relpath(target_relative_path_for_relpath, current_file_relative_dir_from_site_root_clean).replace('\\', '/')

                                # Index.html özel durumu ve trailing slash yönetimi
                                # Eğer hedef URL bir dizin URL'si veya index.html'ye gidiyorsa, './' veya 'dizinadi/' gibi olsun
                                if resolved_new_full_url.endswith('/') or resolved_new_full_url.lower().endswith('/index.html'):
                                    if not new_href_calculated.endswith('/'): # Örneğin '..' olmasın, '../' olsun
                                        new_href_calculated += '/'
                                    if new_href_calculated == '../' and os.path.basename(current_file_relative_dir_from_site_root_clean) == EN_SUBFOLDER_NAME:
                                        # en/alt-dizin/den --> ../ --> en/index.html'e gitmeli
                                        new_href_calculated = './' # Ana 'en' dizinine giden göreceli link
                                # Eğer dosya ve / ile bitiyorsa kaldır
                                elif os.path.splitext(new_href_calculated)[1] and new_href_calculated.endswith('/'):
                                    new_href_calculated = new_href_calculated.rstrip('/')
                                
                                # Eğer aynı dizine işaret ediyorsa './' olmalı
                                if new_href_calculated == '.':
                                    new_href = './'
                                else:
                                    new_href = new_href_calculated

                                if tag['href'] != new_href:
                                    tag['href'] = new_href
                                    changes_made_in_file = True
                                    print(f"  Link güncellendi ({os.path.relpath(file_path, SITE_ROOT_PATH)}): {original_href} -> {tag['href']}")
                        
                    # Değişiklikler varsa dosyayı kaydet
                    if changes_made_in_file:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(str(soup))
                        print(f"Dosya güncellendi: {os.path.relpath(file_path, SITE_ROOT_PATH)}")
                    else:
                        print(f"Dosyada güncellenecek link veya başlık bulunamadı: {os.path.relpath(file_path, SITE_ROOT_PATH)}")

                except Exception as e:
                    print(f"HATA: '{os.path.relpath(file_path, SITE_ROOT_PATH)}' işlenirken hata oluştu: {e}")

    print("\n--- İşlem Tamamlandı ---")
    print("\n--- URL Yönlendirme Haritası (301 Yönlendirmeleri İçin) ---")
    print("Bu haritayı sunucu yapılandırmanıza (örneğin .htaccess veya Nginx config) eklemelisiniz.")
    for old_url, new_url in url_redirect_map.items():
        print(f"Redirect 301 {old_url} {new_url}")

# Betiği çalıştır
if __name__ == "__main__":
    if not os.path.exists(SITE_ROOT_PATH):
        print(f"HATA: '{SITE_ROOT_PATH}' klasörü bulunamadı. Lütfen 'SITE_ROOT_PATH' değişkenini doğru ayarlayın.")
    else:
        rename_and_update_en_folder()