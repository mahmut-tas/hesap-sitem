import os
from bs4 import BeautifulSoup, Comment
import re
import time 

# --- Global Konfigürasyonlar ---
# Betiğin çalıştığı dizini (HESAP-SİTEM klasörü) temel dizin olarak ayarlar.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# İngilizce çevirilerin bulunduğu dizin
EN_LANG_DIR_NAME = 'en'
EN_LANG_PATH = os.path.join(BASE_DIR, EN_LANG_DIR_NAME)

# --- HTML Dosyalarına Eklenecek Dinamik Yükleme JavaScript Kodu ---
# Bu kod, sayfanın dilini otomatik olarak algılar ve buna göre header/footer'ı yükler.
# Bu kod, her HTML dosyasının <body> sonuna eklenecektir.
# (Dikkat: header.html ve footer.html'in kendileri bu kodu içermemeli, sadece ana HTML sayfaları içermeli)
LOAD_COMPONENTS_JS_CODE = f"""
document.addEventListener('DOMContentLoaded', function() {{
    const isEnglishPage = window.location.pathname.startsWith('/{EN_LANG_DIR_NAME}/');
    const headerPath = isEnglishPage ? '/{EN_LANG_DIR_NAME}/header.html' : '/header.html';
    const footerPath = isEnglishPage ? '/{EN_LANG_DIR_NAME}/footer.html' : '/footer.html';

    // Header Yükleme
    fetch(headerPath)
        .then(response => {{
            if (!response.ok) {{
                throw new Error('Header network response was not ok: ' + response.statusText + ' from ' + headerPath);
            }}
            return response.text();
        }})
        .then(data => {{
            const headerPlaceholder = document.getElementById('header-placeholder');
            if (headerPlaceholder) {{
                headerPlaceholder.innerHTML = data;

                // Yüklenen header HTML'i içindeki scripti bul ve çalıştır
                const scriptElement = headerPlaceholder.querySelector('script');
                if (scriptElement) {{
                    const newScript = document.createElement('script');
                    newScript.textContent = scriptElement.textContent; // innerText yerine textContent daha güvenli
                    document.body.appendChild(newScript);
                    scriptElement.remove(); // Orijinal script etiketini kaldır (DOM'dan)
                }}
            }}
        }})
        .catch(error => console.error('Header yüklenirken hata oluştu:', error));

    // Footer Yükleme
    fetch(footerPath)
        .then(response => {{
            if (!response.ok) {{
                throw new Error('Footer network response was not ok: ' + response.statusText + ' from ' + footerPath);
            }}
            return response.text();
        }})
        .then(data => {{
            const footerPlaceholder = document.getElementById('footer-placeholder');
            if (footerPlaceholder) {{
                footerPlaceholder.innerHTML = data;
                // Placeholder div'ini semantik bir <footer> etiketiyle değiştir
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = data;
                const footerElement = tempDiv.querySelector('footer');
                if (footerElement) {{
                    footerPlaceholder.replaceWith(footerElement);
                }}
            }}
        }})
        .catch(error => console.error('Footer yüklenirken hata oluştu:', error));
}});
"""

# --- Yardımcı Fonksiyonlar ---

def find_and_remove_tag(soup_obj, tag_name, **kwargs):
    """Belirtilen etiketi (veya etiketleri) bulup HTML'den kaldırır."""
    tags = soup_obj.find_all(tag_name, **kwargs)
    removed_count = 0
    for tag in tags:
        tag.decompose()
        removed_count += 1
    return removed_count

def add_css_link_absolute(soup_obj, relative_path_from_root):
    """<head> içine mutlak yollu CSS linki ekler, eğer zaten yoksa."""
    full_href_url = f"/{relative_path_from_root}"
    if not soup_obj.head:
        print(f"  Uyarı: <head> etiketi bulunamadı, CSS linki '{full_href_url}' eklenemedi.")
        return False
    
    # Mevcut linkleri kontrol et, tam mutlak yolu kontrol et
    if not soup_obj.find('link', rel="stylesheet", href=full_href_url):
        new_link = soup_obj.new_tag("link", rel="stylesheet", href=full_href_url)
        title_tag = soup_obj.head.find('title')
        if title_tag:
            title_tag.insert_after(new_link)
        else:
            soup_obj.head.append(new_link) 
        print(f"  CSS linki '{full_href_url}' <head> etiketine eklendi.")
        return True
    print(f"  CSS linki '{full_href_url}' zaten mevcut, atlandı.")
    return False

def add_js_script(soup_obj, script_code, at_end_of_body=True):
    """Sayfaya JavaScript kodu ekler, eğer zaten aynı kod yoksa."""
    if not soup_obj.body:
        print("  Uyarı: <body> etiketi bulunamadı, JS script eklenemedi.")
        return False

    # Var olan tüm script etiketlerinin stringlerini kontrol ederek mükerrer eklemeyi engelle
    for existing_script in soup_obj.find_all('script'):
        if existing_script.string and script_code.strip() == existing_script.string.strip():
            print("  Dinamik yükleme JS kodu zaten mevcut, atlandı.")
            return False

    new_script = soup_obj.new_tag("script")
    new_script.string = script_code
    
    if at_end_of_body:
        soup_obj.body.append(new_script)
    else:
        soup_obj.head.append(new_script) 

    print(f"  Dinamik yükleme JS kodu <body> sonuna eklendi.")
    return True

# --- HTML Dosyası İşleme Fonksiyonu ---
def process_html_file(file_path):
    print(f"İşleniyor: {file_path}")

    # Bileşen dosyalarını atla (header.html, footer.html)
    if os.path.basename(file_path) in ['header.html', 'footer.html']:
        print(f"  Bileşen dosyası olduğu için '{file_path}' atlanıyor (doğrudan değiştirilmiyor).\n")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, 'html.parser')
    except Exception as e:
        print(f"Hata: '{file_path}' dosyası okunamadı veya ayrıştırılamadı - {e}. Atlanıyor.\n")
        return

    # Temel HTML yapısı kontrolü
    if not soup.html or not soup.head or not soup.body:
        print(f"  Hata: '{file_path}' tam bir HTML belgesi gibi görünmüyor (<html/head/body> eksik). Atlanıyor.\n")
        return

    # --- 1. Temizleme ve Standartlaştırma Adımları ---
    print("  Temizleme ve standartlaştırma yapılıyor...")

    # a. Mevcut tüm <header> etiketlerini kaldır
    removed_headers = find_and_remove_tag(soup, 'header')
    if removed_headers > 0:
        print(f"    {removed_headers} adet mevcut <header> etiketi kaldırıldı.")
    else:
        print(f"    Mevcut <header> etiketi bulunamadı, kaldırma işlemi yapılmadı.")

    # b. Mevcut tüm <footer> etiketlerini kaldır
    removed_footers = find_and_remove_tag(soup, 'footer')
    if removed_footers > 0:
        print(f"    {removed_footers} adet mevcut <footer> etiketi kaldırıldı.")
    else:
        print(f"    Mevcut <footer> etiketi bulunamadı, kaldırma işlemi yapılmadı.")
    
    # c. head veya body dışında yanlış yerleştirilmiş scriptleri <head> içine taşı
    if soup.html:
        for script_tag in list(soup.html.find_all('script', recursive=False)): 
            if script_tag.parent == soup.html and script_tag not in [soup.head, soup.body]:
                soup.head.append(script_tag)
                print(f"    Yanlış yerleştirilmiş bir <script> etiketi <head> içine taşındı.")

    # d. Dinamik yükleme JS'i (LOAD_COMPONENTS_JS_CODE) veya header.js gibi script bağlantılarını kaldır
    removed_custom_js_blocks = find_and_remove_tag(soup, 'script', string=re.compile(r'document\.addEventListener\(\'DOMContentLoaded\'', re.DOTALL))
    if removed_custom_js_blocks > 0:
        print(f"    {removed_custom_js_blocks} adet eski dinamik yükleme JS bloğu kaldırıldı.")
        
    removed_header_js_links = find_and_remove_tag(soup, 'script', src=re.compile(r'/js/header\.js'))
    if removed_header_js_links > 0:
        print(f"    {removed_header_js_links} adet eski header JS bağlantısı kaldırıldı.")


    # --- 2. Yer Tutucuları Ekle ---
    print("  Yer tutucular ekleniyor/güncelleniyor...")

    # a. Header için yer tutucu ekle
    if not soup.find('div', id='header-placeholder'):
        new_header_placeholder = soup.new_tag("div", id="header-placeholder")
        soup.body.insert(0, new_header_placeholder)
        print(f"    <div id='header-placeholder'> eklendi.")
    else:
        print(f"    <div id='header-placeholder'> zaten mevcut.")

    # b. Footer için yer tutucu ekle
    if not soup.find('div', id='footer-placeholder'):
        new_footer_placeholder = soup.new_tag("div", id="footer-placeholder")
        soup.body.append(new_footer_placeholder) # Body'nin en sonuna
        print(f"    <div id='footer-placeholder'> eklendi.")
    else:
        print(f"    <div id='footer-placeholder'> zaten mevcut.")

    # --- 3. CSS Bağlantılarını Ekle/Kontrol Et (Mutlak Yollar) ---
    print("  CSS bağlantıları ekleniyor/güncelleniyor (mutlak yollar)...")

    add_css_link_absolute(soup, "css/header.css")
    add_css_link_absolute(soup, "css/style.css") 
    # add_css_link_absolute(soup, "css/footer.css") # BU SATIR KALDIRILDI, ÇÜNKÜ footer stilleri style.css'te


    # --- 4. Dinamik Yükleme JavaScript'ini Ekle ---
    print("  Dinamik yükleme JS kodu ekleniyor...")
    add_js_script(soup, LOAD_COMPONENTS_JS_CODE) 

    # --- 5. Güncellenmiş HTML'i Kaydet ---
    output_file_path = file_path # Mevcut dosyanın üzerine yaz
    
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify())) # Prettify ile daha düzenli çıktı
    print(f"Başarıyla güncellendi: '{output_file_path}'\n")

# --- Tüm HTML Dosyalarını Tarama ve İşleme için Ana Fonksiyon ---
def run_component_fixer():
    print("--- Web Sitesi Bileşenleri Düzeltme Betiği Başlatılıyor ---")
    print(f"Hedeflenecek Dizin: {BASE_DIR}")
    print(f"İngilizce Dizin Adı: {EN_LANG_DIR_NAME}")

    required_dirs = [os.path.join(BASE_DIR, 'css'), os.path.join(BASE_DIR, 'js')]
    for d in required_dirs:
        if not os.path.exists(d):
            print(f"Hata: Gerekli dizin bulunamadı: {d}. Lütfen klasör yapınızı kontrol edin.")
            return

    required_component_htmls = [os.path.join(BASE_DIR, 'header.html'), os.path.join(BASE_DIR, 'footer.html')]
    for h_file in required_component_htmls:
        if not os.path.exists(h_file):
            print(f"Hata: Gerekli bileşen HTML dosyası bulunamadı: {h_file}. Lütfen kontrol edin.")
            return
    # İngilizce versiyonlarının da varlığını kontrol edin (bu betik onları oluşturmuyor)
    required_en_component_htmls = [os.path.join(EN_LANG_PATH, 'header.html'), os.path.join(EN_LANG_PATH, 'footer.html')]
    for h_file in required_en_component_htmls:
        if not os.path.exists(h_file):
            print(f"Hata: İngilizce bileşen HTML dosyası bulunamadı: {h_file}. Lütfen manuel olarak oluşturun ve çevirin (Header'ınızdaki dil seçici çalışmayacaktır).")

    print("\n!!! ÖNEMLİ UYARI: Bu betik HTML dosyalarını DEĞİŞTİRECEKTİR. !!!")
    print("Mevcut tüm <header> ve <footer> etiketleri kaldırılacak, yanlış yerleştirilmiş scriptler taşınacak ve dinamik yükleme JS'i eklenecektir.")
    print("Lütfen devam etmeden önce TÜM WEB SİTESİ DOSYALARINIZIN GÜNCEL BİR YEDEKLEMESİNİ aldığınızdan emin olun.")
    
    user_input = input("Devam etmek için 'evet' yazıp Enter tuşuna basın: ").lower()

    if user_input != 'evet':
        print("İşlem iptal edildi.")
        return

    for root, _, files in os.walk(BASE_DIR):
        if root.startswith(os.path.join(BASE_DIR, 'css')) or \
           root.startswith(os.path.join(BASE_DIR, 'js')) or \
           root == BASE_DIR: # Betiğin kendisini içeren klasörü de atlama (BASE_DIR'in içindeki HTML'leri işlemek için)
            pass # Bu koşulu değiştirdim, ana dizindeki HTML'leri işlemesi için.

        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                
                # Eğer dosya kök dizinindeyse (BASE_DIR) veya 'en' dizininin altındaysa işle
                # Yani statik varlık klasörlerini (css, js) atlamış oluyoruz
                if os.path.commonpath([file_path, BASE_DIR]) == BASE_DIR and not (
                   file_path.startswith(os.path.join(BASE_DIR, 'css')) or
                   file_path.startswith(os.path.join(BASE_DIR, 'js'))
                ):
                    process_html_file(file_path)

    print("\n--- Tüm HTML dosyaları başarıyla düzenlendi. ---")

# --- Betiği Çalıştır ---
if __name__ == "__main__":
    run_component_fixer()