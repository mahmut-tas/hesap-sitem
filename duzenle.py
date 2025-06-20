import os
import re
from google.cloud import translate_v2 as translate
from bs4 import BeautifulSoup
import unicodedata

# --- Yapılandırma Başlangıcı ---
# Google Cloud servis hesap anahtarınızın tam yolu
GOOGLE_APPLICATION_CREDENTIALS_PATH = r"C:\Users\suuser\Desktop\hesapkolik-multilang-d6ca51078a3a.json"

# İngilizce klasörünün mutlak veya göreceli yolu
# Bu betiği çalıştırdığınız yere göre bu yolu ayarlayın.
# Örnek: Eğer betik ana proje klasörünüzdeyse ve /en klasörü altındaysa:
# EN_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'en')
# Eğer /en klasörünün tam yolunu vermeniz gerekiyorsa:
EN_FOLDER_PATH = r'C:\Users\suuser\Desktop\hesap-sitem\en' # Lütfen KENDİ SİTE KÖK DİZİNİNİZİ BURAYA YAZIN!

# Hedef çeviri dili
TARGET_LANGUAGE = 'en'

# --- MANUEL ÇEVİRİ HARİTASI ---
# Google Translate API'nin yanlış çevirdiği veya özel olarak kalmasını istediğiniz Türkçe terimlerin
# URL dostu (slugified) İngilizce karşılıklarını buraya ekleyin.
# Bu sözlük, Google API'den gelen çeviriye öncelik verir.
# 'türkçe-slug': 'english-slug' formatında olmalıdır.
MANUAL_TRANSLATION_MAP = {
    # Kök Dizinler ve Genel Sayfalar (Zaten İngilizce olanlar veya özel isimler)
    'en': 'en',
    'index': 'index',
    'about-us': 'about-us',
    'hakkimizda': 'about-us', # Türkçe dosya adından eşleme için
    'contact': 'contact',
    'iletisim': 'contact', # Türkçe dosya adından eşleme için
    'privacy-policy': 'privacy-policy',
    'gizlilik-politikasi': 'privacy-policy', # Türkçe dosya adından eşleme için
    'terms-of-use': 'terms-of-use',
    'kullanim-sartlari': 'terms-of-use', # Türkçe dosya adından eşleme için
    'age-calculator': 'age-calculator', # Zaten İngilizce olan bir dosya adından eşleme için
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
    'kimya': 'chemical', # Önceki çıktıdaki 'silence' hatası için KRİTİK düzeltme!


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
    'seri-paralel-direnc': 'series-parallel-resistance', # Düzeltildi
    'elektrik-gucu': 'electric-power',
    'kapasitor-sarj-desarj': 'capacitor-charge-discharge',
    'rc-rl-zaman-sabiti': 'rc-rl-time-constant',
    'frekans-periyot': 'frequency-period',
    'filtre-kesim-frekansi': 'filter-cutoff-frequency',
    'direnc-renk-kodu': 'resistor-color-code',
    'led-direnc': 'led-resistor', # Düzeltildi
    'voltaj-bolucu': 'voltage-divider', # Düzeltildi
    'gerilim-dusumu': 'voltage-drop',
    'guc-faktoru': 'power-factor',
    'beton-hacmi-malzeme': 'concrete-volume-materials',
    'tugla-blok-duvar': 'brick-block-wall',
    'boya-miktari-hesaplayici': 'paint-quantity-calculator',
    'fayans-seramik': 'tile-ceramic',
    'kiris-egilme-kesme': 'beam-bending-shear',
    'kiris-sehim': 'beam-deflection', # Düzeltildi
    'atalet-momenti': 'moment-of-inertia',
    'kisa-kolon-kapasitesi': 'short-column-capacity',
    'zemin-tasima-kapasitesi': 'soil-bearing-capacity',
    'zemin-oturmasi': 'soil-settlement',
    'boru-basinc-dususu': 'pipe-pressure-drop', # Düzeltildi
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
    'burulma-gerilmesi': 'torsional-stress', # önceki çıktıdaki 'torsionstress' yerine
    'emniyet-faktoru': 'safety-factor',
    'burkulma-yuku': 'buckling-load',
    'isi-esanjörü-lmtd': 'heat-exchanger-lmtd',
    'sogutma-yuku': 'cooling-load',
    'pompa-gucu': 'pump-power',
    'reynolds-sayisi': 'reynolds-number',
    'sertlik-donusumu': 'hardness-conversion',
    'iplik-numarasi': 'yarn-count',
    'boya-recetesi': 'dye-recipe', # Düzeltildi
    'dokuma-verimlilik': 'weaving-efficiency',
    'elyaf-karisim': 'fiber-blend', # Düzeltildi
    'cozgu-atki-miktari': 'warp-weft-amount', # Düzeltildi
    'iplik-uzunlugu': 'yarn-length',
    'baski-pati': 'print-paste', # Düzeltildi
    'kumas-fire': 'fabric-waste', # Düzeltildi
    'lab-boyama': 'lab-dyeing', # Yeni eklenen
    'kumas-cekme-orani': 'fabric-shrinkage-rate', # Yeni eklenen
    'kumas-gramaji': 'fabric-weight', # Yeni eklenen
    'kumas-sikiligi': 'fabric-tightness', # Yeni eklenen
    'gpa-hesaplama': 'gpa-calculation',
    'toefl-hesaplama': 'toefl-calculation',
    'yks-hesaplama': 'yks-calculation', # Özel isim olduğu için çevrilmedi
    'ielts-hesaplama': 'ielts-calculation',
    'gre-hesaplama': 'gre-calculation',
    'gmat-hesaplama': 'gmat-calculation',
    'yuzde-basari-orani': 'success-rate-percentage',
    'yakit-tuketimi-hesaplayici': 'fuel-consumption-calculator',
    'elektrikli-arac-sarj-maliyeti': 'electric-vehicle-charging-cost', # Düzeltildi
    'ampul-enerji-hesaplayici': 'bulb-energy-calculator',
    'butce-planlayici': 'budget-planner',
    'yemek-porsiyon-hesaplayici': 'food-portion-calculator',
    'fatura-gider-takibi': 'invoice-expense-tracker', # Düzeltildi
    'klima-enerji-tuketimi': 'air-conditioner-energy-consumption', # Düzeltildi
    'indirim-hesaplayici': 'discount-calculator',
    'adet-dongusu-takibi': 'menstrual-cycle-tracker',
    'target-pulse-zone': 'target-heart-rate-zone',
    'daily-calorie-requirement-calculator': 'daily-calorie-needs-calculator',
    'daily-water-requirement': 'daily-water-intake',
    'daily-carbohydrate-requirement': 'daily-carbohydrate-needs',
    'daily-protein-requirement': 'daily-protein-needs',
}

# --- Yapılandırma Sonu ---

# --- Yardımcı Fonksiyonlar ---
def slugify(text):
    """
    Metni URL dostu bir sluga dönüştürür.
    Örn: "Türkçe Başlık" -> "turkce-baslik"
    """
    text = str(text).lower()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text) # Alfabetik, sayısal, boşluk ve tire dışındaki karakterleri kaldır
    text = re.sub(r'[\s_-]+', '-', text) # Boşlukları ve birden fazla tireyi tek tireye dönüştür
    text = re.sub(r'^-+|-+$', '', text) # Başlangıç ve sondaki tireleri kaldır
    return text

def translate_text(text):
    """Google Translate API kullanarak metni çevirir."""
    if not text or text.strip() == '': 
        return ""
    
    # Manuel çeviri haritasında slugify yapılmış haliyle varsa, onu kullan
    text_slug = slugify(text)
    if text_slug in MANUAL_TRANSLATION_MAP:
        return MANUAL_TRANSLATION_MAP[text_slug]

    if len(text) > 500: 
        print(f"Uyarı: Çok uzun metin çevirisi atlanıyor veya kısaltılıyor: {text[:100]}...")
        return slugify(text) # Sadece slugify yap
        
    try:
        result = translate_client.translate(text, target_language=TARGET_LANGUAGE)
        return result['translatedText']
    except Exception as e:
        print(f"Hata çeviri yaparken '{text}': {e}")
        return slugify(text) # Çeviri hatası durumunda sadece slugify yapmaya çalış

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

# --- Diğer Fonksiyonlar ---

def get_new_path_segment(path_segment_raw):
    """Verilen URL yol segmentini (dosya adı veya dizin adı) çevirir ve slugify yapar."""
    
    base_name, ext = os.path.splitext(path_segment_raw)
    
    # Manuel çeviri haritasında tam slug olarak varsa, onu kullan
    slugified_base_name = slugify(base_name)
    if slugified_base_name in MANUAL_TRANSLATION_MAP:
        return MANUAL_TRANSLATION_MAP[slugified_base_name] + ext
            
    # Eğer manuel haritada yoksa, API ile çevir
    translated_name = translate_text(base_name)
    return slugify(translated_name) + ext

def is_internal_html_link(href):
    """Bir href'in sitenin kendi HTML dosyasına işaret eden dahili bir link olup olmadığını kontrol eder."""
    if not href or href.startswith(('#', 'mailto:', 'tel:', 'javascript:')) or \
       href.startswith(('http://', 'https://', '//')) or \
       any(href.lower().endswith(ext) for ext in ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico']):
        return False
    return True

def process_directory(directory_path):
    """Belirtilen dizindeki ve alt dizinlerdeki HTML dosyalarını işler."""
    
    url_mapping = {} # Eski Tam URL -> Yeni Tam URL eşlemeleri (301 yönlendirmeler için)
    file_path_mapping = {} # Eski Mutlak Dosya Yolu -> Yeni Mutlak Dosya Yolu eşlemeleri (yeniden adlandırma için)

    print(f"--- Dizin ve Dosya Adı Çevirileri Başlıyor ---")
    
    # 1. Aşama: Tüm dizin ve dosya adlarının çevrilmiş halini ve eşlemelerini belirle
    # os.walk(topdown=False) ile alt dizinlerden başlayarak gezinti yapılır.
    # Bu, bir dizin yeniden adlandırılmadan önce içindeki öğelerin doğru bir şekilde işlenmesini sağlar.
    all_paths_to_process = [] 
    for root, dirs, files in os.walk(directory_path, topdown=False):
        for d in dirs:
            all_paths_to_process.append((os.path.join(root, d), True)) # True for directory
        for f in files:
            if f.endswith(".html"):
                all_paths_to_process.append((os.path.join(root, f), False)) # False for file
    
    # Tüm yollar için eşlemeyi oluştur
    for original_path, is_dir in all_paths_to_process:
        parent_dir = os.path.dirname(original_path)
        
        # Eğer üst dizin zaten eşleme haritasında (yani yeniden adlandırılacaksa), yeni üst dizin yolunu kullan
        # Bu, FileNotFoundError'u önlemek için kritik.
        current_parent_dir_for_mapping = file_path_mapping.get(parent_dir, parent_dir)
            
        base_name = os.path.basename(original_path)
        new_base_name = get_new_path_segment(base_name)
        
        new_full_path = os.path.join(current_parent_dir_for_mapping, new_base_name)
        
        # Çakışma kontrolü ve benzersiz isim oluşturma
        counter = 1
        temp_new_full_path = new_full_path
        while os.path.exists(temp_new_full_path) and temp_new_full_path != original_path:
            name_without_ext, ext = os.path.splitext(new_base_name)
            temp_new_full_path = os.path.join(current_parent_dir_for_mapping, f"{name_without_ext}-{counter}{ext}")
            counter += 1
        new_full_path = temp_new_full_path

        if original_path != new_full_path:
            file_path_mapping[original_path] = new_full_path
            print(f"Eşleme belirlendi: {original_path} -> {new_full_path}")
        else:
            file_path_mapping[original_path] = original_path # Değişmeyenleri de kaydet

    print("\n--- Dizin ve Dosya Adları Yeniden Adlandırılıyor ---")
    # 2. Aşama: Dosyaları ve Dizinleri Yeniden Adlandır
    # file_path_mapping'deki eşlemeleri kullanarak yeniden adlandırma işlemini gerçekleştir.
    # Yolların uzunluğuna göre ters sıralama, iç içe dizinlerin doğru sırayla yeniden adlandırılmasını sağlar.
    sorted_paths_to_rename = sorted(file_path_mapping.items(), key=lambda item: len(item[0]), reverse=True)

    for original_abs_path, new_abs_path in sorted_paths_to_rename:
        if original_abs_path != new_abs_path:
            try:
                # Sadece mevcut olan dosyaları/dizinleri yeniden adlandır
                if os.path.exists(original_abs_path):
                    os.rename(original_abs_path, new_abs_path)
                    print(f"Yeniden adlandırıldı: {original_abs_path} -> {new_abs_path}")
                else:
                    print(f"UYARI: {original_abs_path} zaten taşınmış veya bulunamadı. Atlanıyor.")
            except Exception as e:
                print(f"HATA oluştu yeniden adlandırılırken {original_abs_path} -> {new_abs_path}: {e}")
        else:
            print(f"Yeniden adlandırma yapılmadı (yol aynı): {original_abs_path}")


    # 3. Aşama: URL Eşleme Haritasını Oluştur (301 Yönlendirmeleri İçin)
    # file_path_mapping'deki nihai durumdan URL eşlemesini oluştur.
    # Bu kısım yeniden adlandırma sonrası oluşacak URL'lerin eşleşmesini sağlar.
    for original_abs_path_before_rename, final_abs_path_after_rename in file_path_mapping.items():
        # Sadece HTML dosyaları için URL eşlemesi oluştur
        if not final_abs_path_after_rename.lower().endswith(".html"): # .lower() ile uzantı kontrolü
            continue

        # EN_FOLDER_PATH'e göre göreceli URL'leri al
        old_relative_url = '/' + os.path.relpath(original_abs_path_before_rename, EN_FOLDER_PATH).replace('\\', '/')
        new_relative_url = '/' + os.path.relpath(final_abs_path_after_rename, EN_FOLDER_PATH).replace('\\', '/')
        
        # Eğer index.html ise sadece / (kök) olarak ele al
        if old_relative_url.lower().endswith('/index.html'):
            old_relative_url = old_relative_url.replace('/index.html', '/')
        if new_relative_url.lower().endswith('/index.html'):
            new_relative_url = new_relative_url.replace('/index.html', '/')

        # /en/ ön ekini ekle (zaten varsa eklememeye dikkat et)
        old_full_url = '/en' + old_relative_url if not old_relative_url.startswith('/en/') else old_relative_url
        new_full_url = '/en' + new_relative_url if not new_relative_url.startswith('/en/') else new_relative_url
        
        # Özellikle tek kalan dizin adları için URL eşlemesi
        # Örnek: /en/muhendislik/cevre/ -> /en/engineering/environmental/
        if os.path.isdir(final_abs_path_after_rename) and not final_abs_path_after_rename.lower().endswith('.html'):
            # Eğer orijinali de dizin gibi bitiyorsa (yani dosya adı yoksa)
            if old_full_url.endswith('/') and new_full_url.endswith('/'):
                 url_mapping[old_full_url] = new_full_url
                 print(f"URL Eşleme Oluşturuldu (Dizin): {old_full_url} -> {new_full_url}")
                 continue # Zaten eklendi, dosyalarla karışmasın

        if old_full_url != new_full_url:
            url_mapping[old_full_url] = new_full_url
            print(f"URL Eşleme Oluşturuldu: {old_full_url} -> {new_full_url}")
        else:
             print(f"URL eşlemesi gereksiz (URL değişmedi): {old_full_url}")


    print("\n--- HTML İçindeki Linkler Güncelleniyor ---")

    # 4. Aşama: HTML İçeriğindeki Linkleri Güncelle
    # Şimdi artık dosyalar ve dizinler doğru yerlerinde. Bu aşamada, sadece HTML dosyalarının içindeki linkleri güncelliyoruz.
    # Bu döngüde, dosya sistemi artık güncel (yeniden adlandırılmış) haliyle geziliyor.
    for root, _, files in os.walk(EN_FOLDER_PATH):
        for file_name in files:
            if file_name.lower().endswith(".html"):
                file_path = os.path.join(root, file_name)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    links_updated_in_file = False

                    for tag in soup.find_all(['a', 'link'], href=True):
                        original_href = tag['href']
                        
                        # Mevcut HTML dosyasının EN_FOLDER_PATH'e göre göreceli dizini
                        # Bu, göreceli linkleri çözerken kullanılacak.
                        current_file_relative_dir = os.path.dirname(os.path.relpath(file_path, EN_FOLDER_PATH)).replace('\\', '/')

                        new_href = original_href # Varsayılan olarak orijinali koru

                        # Eğer link mutlak bir yol ise (örn: /en/...)
                        if original_href.startswith('/'):
                            # Sadece /en/ ile başlayan dahili HTML linklerini hedefle
                            if original_href.startswith('/en/') and is_internal_html_link(original_href):
                                # url_mapping'de doğrudan arama yap
                                if original_href in url_mapping:
                                    new_href = url_mapping[original_href]
                                else:
                                    # Eğer eşlemede yoksa (ki olmamalıdır çünkü tüm html dosyaları için eşleme oluşturduk),
                                    # bu muhtemelen bir sorun. Ancak yine de parçalı çeviri denemesi yapalım.
                                    # VEYA bu kısım, zaten doğru isimli olan ve mapping'e girmeyen linkleri de içerebilir.
                                    path_after_en_prefix = original_href[len('/en/'):]
                                    path_segments = path_after_en_prefix.split('/')
                                    
                                    temp_new_segments = []
                                    for segment in path_segments:
                                        if segment:
                                            # get_new_path_segment'i çağırırken uzantı varsa ayrılıyor, burada tekrar birleştir.
                                            # Eğer segment bir dosya adı ise (.html içeriyorsa)
                                            if '.' in segment: 
                                                base, ext = os.path.splitext(segment)
                                                translated_base = translate_text(base)
                                                temp_new_segments.append(slugify(translated_base) + ext)
                                            else: # Dizin adı ise
                                                translated_segment = translate_text(segment)
                                                temp_new_segments.append(slugify(translated_segment))
                                        else:
                                            temp_new_segments.append(segment) # Boş segmentleri koru
                                    
                                    generated_href = '/en/' + '/'.join(temp_new_segments)
                                    
                                    # Index.html ise düzelt
                                    if generated_href.lower().endswith('/index.html'):
                                        generated_href = generated_href.replace('/index.html', '/')
                                    
                                    if generated_href != original_href:
                                        new_href = generated_href
                                        
                            # Eğer /en/ ile başlayan ama HTML olmayan bir linkse (örn. CSS, JS, resim)
                            elif original_href.startswith('/en/') and not is_internal_html_link(original_href):
                                # Sadece /en/den sonraki yolu al
                                path_after_en = original_href[len('/en/'):]
                                # Bu yolu parçalara ayır ve dizin adlarını kontrol et
                                segments = path_after_en.split('/')
                                new_segments = []
                                changed_static_link_part = False
                                for segment in segments:
                                    if segment:
                                        # Sadece dizin ise (uzantısı yoksa) manuel haritadan çevirmeye çalış
                                        if '.' not in segment: 
                                            segment_slug = slugify(segment)
                                            if segment_slug in MANUAL_TRANSLATION_MAP:
                                                new_segments.append(MANUAL_TRANSLATION_MAP[segment_slug])
                                                changed_static_link_part = True
                                            else: # Manuelde yoksa API ile çevir
                                                translated_segment = translate_text(segment)
                                                new_segments.append(slugify(translated_segment))
                                                if slugify(translated_segment) != segment_slug: # Değişmişse işaretle
                                                    changed_static_link_part = True
                                        else: # Dosya adı ise aynen koru
                                            new_segments.append(segment)
                                    else: # Boş segment ise aynen koru
                                        new_segments.append(segment)
                                
                                generated_href = '/en/' + '/'.join(new_segments)
                                if changed_static_link_part and generated_href != original_href:
                                    new_href = generated_href

                        # Eğer link göreceli bir yol ise (örn: boi-koi-orani.html veya ../dizin/dosya.html)
                        elif is_internal_html_link(original_href):
                            # Mevcut sayfadan mutlak yolu oluştur (en klasörü kökenli)
                            full_relative_path_from_en_folder = os.path.normpath(os.path.join(current_file_relative_dir, original_href)).replace('\\', '/')
                            
                            # Bu tam göreceli yolu /en/ ön ekiyle birleştirerek tam eski URL'yi oluştur
                            old_full_url_for_relative_link = '/en/' + full_relative_path_from_en_folder

                            # Index.html özel durumu
                            if old_full_url_for_relative_link.lower().endswith('/index.html'):
                                old_full_url_for_relative_link = old_full_url_for_relative_link.replace('/index.html', '/')
                            
                            # Eşleme haritasından yeni tam URL'yi ara
                            if old_full_url_for_relative_link in url_mapping:
                                new_full_url_from_map = url_mapping[old_full_url_for_relative_link]
                                
                                # Yeni göreceli yolu hesapla (yeni tam URL'den mevcut dosyanın dizinine göre)
                                path_after_en = new_full_url_from_map[len('/en/'):] # /en/ engineering/environmental/bod-cod-ratio.html -> engineering/environmental/bod-cod-ratio.html
                                new_relative_path_from_current_page = os.path.relpath(path_after_en, current_file_relative_dir).replace('\\', '/')
                                
                                if new_relative_path_from_current_page == '.': # Eğer hedef mevcut dizin ise
                                    new_relative_path_from_current_page = './'
                                    
                                new_href = new_relative_path_from_current_page
                            else:
                                # Eğer eşlemede bulunamadıysa (ki bu nadir olmalıydı), parçaları çevirerek yeni bir href oluşturmaya çalış.
                                print(f"  {file_path} içinde '{original_href}' (göreceli) linki eşlemede bulunamadı, parçalı çeviri deneniyor.")
                                path_segments = original_href.split('/')
                                temp_new_segments = []
                                for segment in path_segments:
                                    if segment:
                                        if '.' in segment: # Eğer dosya adı ise
                                            base, ext = os.path.splitext(segment)
                                            translated_base = translate_text(base)
                                            temp_new_segments.append(slugify(translated_base) + ext)
                                        else: # Dizin adı ise
                                            translated_segment = translate_text(segment)
                                            temp_new_segments.append(slugify(translated_segment))
                                    else:
                                        temp_new_segments.append(segment)
                                generated_href = '/'.join(temp_new_segments)

                                if generated_href != original_href:
                                    new_href = generated_href

                        # Eğer new_href değiştiyse, tag'i güncelle ve bayrağı ayarla
                        if new_href != original_href:
                            tag['href'] = new_href
                            links_updated_in_file = True
                            print(f"  {file_path} içinde link güncellendi: {original_href} -> {tag['href']}")
                        # else:
                        #     print(f"  {file_path} içinde link değişmedi: {original_href}")


                    # Değişiklikler varsa dosyayı kaydet
                    if links_updated_in_file:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(str(soup))
                        print(f"Dosya güncellendi: {file_path}")
                    else:
                        print(f"Dosyada güncellenecek link bulunamadı veya linkler zaten günceldi: {file_path}")

                except Exception as e:
                    print(f"Hata oluştu {file_path} işlenirken: {e}")

    print("\n--- İşlem Tamamlandı ---")
    print("\n--- URL Yönlendirme Haritası (301 Yönlendirmeleri İçin) ---")
    print("Bu haritayı sunucu yapılandırmanıza (örneğin .htaccess veya Nginx config) eklemelisiniz.")
    for old_url, new_url in url_mapping.items():
        print(f"Redirect 301 {old_url} {new_url}")

# Betiği çalıştır
if __name__ == "__main__":
    if not os.path.exists(EN_FOLDER_PATH):
        print(f"HATA: '{EN_FOLDER_PATH}' klasörü bulunamadı. Lütfen 'EN_FOLDER_PATH' değişkenini doğru ayarlayın.")
    else:
        process_directory(EN_FOLDER_PATH)