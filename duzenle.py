import os
import re

def fix_calculator_js(js_code):
    """
    Verilen JavaScript kodundaki hesaplayıcı sonuç div'lerini görünür yapma satırlarını ekler.
    Bu fonksiyon, 'result-display' ve 'category-display' id'lerine sahip div'leri hedefler.
    """
    updated_js_code = js_code

    # 1. Her hesaplama başlangıcında veya hata durumunda div'leri gizle
    calculate_func_pattern = re.compile(r'(function\s+(?:calculate\w+|showCalculator)\s*\([^)]*\)\s*\{[^}]*?)(let\s+\w+\s*=\s*parseFloat\s*\(.+?\)\s*;|\/\/ --- Input Validation ---)', re.DOTALL)
    
    match = calculate_func_pattern.search(updated_js_code)
    if match:
        func_start_code = match.group(1)
        # Regex'teki ikinci grup, insert_point için daha doğru bir referans verir.
        # Bu kısım kodun başlangıçtan itibaren doğru yere eklenmesini sağlar.
        insert_point = match.end(1) if match.group(2) else match.start(1) + len(match.group(1)) - 1 # Fonksiyon süslü parantezinin hemen içi
        
        # Temizleme ve gizleme kodunu eklemek için DOM elementlerini bulalım
        result_div_var_matches = re.findall(r'(const|let)\s+(\w+)\s*=\s*document\.getElementById\(\s*[\'"](\w*Result)[\'"]\s*\);', func_start_code)
        category_div_var_matches = re.findall(r'(const|let)\s+(\w+)\s*=\s*document\.getElementById\(\s*[\'"](\w*Category)[\'"]\s*\);', func_start_code)

        hide_lines = []
        for _, var_name, _ in result_div_var_matches:
            hide_lines.append(f"{var_name}.style.display = 'none';")
        for _, var_name, _ in category_div_var_matches:
            hide_lines.append(f"{var_name}.style.display = 'none';")
        
        if hide_lines:
            # Gizleme kodunu, fonksiyonun başladığı yerden sonraki ilk anlamsız boşluğun altına eklemek için
            # indentation'ı korumak adına biraz daha akıllıca bir yerleşim.
            # İlk anlamlı kod satırının indentini yakalayıp ona göre eklemek daha iyi olurdu ama şimdilik sabit indentation ile gidelim.
            
            # Fonksiyon gövdesinin açıldığı parantezi bulup hemen sonrasına ekleyelim.
            brace_index = func_start_code.rfind('{')
            if brace_index != -1:
                initial_indent = " " * 8 # Varsayılan olarak 8 boşluk indent
                hide_code_formatted = "\n" + initial_indent + "        " + "\n" + initial_indent + "        ".join(hide_lines) + "\n" + initial_indent + "    " # Ekstra boşluklar düzeltildi.
                
                # Sadece bir kez eklemek için kontrol edelim
                if f"{result_div_var_matches[0][1]}.style.display = 'none';" not in updated_js_code[brace_index:insert_point]:
                     updated_js_code = updated_js_code[:brace_index + 1] + hide_code_formatted + updated_js_code[brace_index + 1:]


    # 2. Sonuç atamalarından sonra div'leri görünür yap
    # 'someDiv.innerHTML = ...' veya 'someDiv.textContent = ...' satırlarını bulur
    # ve altına 'someDiv.style.display = "block";' ekler.
    patterns_to_fix = [
        # Normal sonuç atamaları
        (r'(\s*(\w+)\.innerHTML\s*=\s*`.*?`\s*;)', r'\1\n        \\2.style.display = \'block\';'), # Buradaki \s düzeltildi -> \\s ve indent artırıldı
        (r'(\s*(\w+)\.innerHTML\s*=\s*[\'"].*?[\'"]\s*;)', r'\1\n        \\2.style.display = \'block\';'), # Buradaki \s düzeltildi -> \\s ve indent artırıldı
        # Hata mesajı atamaları (resultDiv için)
        (r'(\s*(\w+ResultDiv)\.innerHTML\s*=\s*`<p class="error">.*?<\/p>`\s*;)', r'\1\n        \\2.style.display = \'block\';'), # Buradaki \s düzeltildi -> \\s ve indent artırıldı
    ]

    for old_pattern, new_replacement in patterns_to_fix:
        updated_js_code = re.sub(old_pattern, new_replacement, updated_js_code, flags=re.DOTALL)
    
    return updated_js_code


def process_html_file(filepath):
    """Belirtilen HTML dosyasını okur, JavaScript'i düzeltir ve güncellenmiş içeriği yazar."""
    print(f"'{filepath}' dosyası işleniyor...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # JavaScript <script> etiketlerini bul
    # <script> ile </script> arasındaki içeriği yakalar
    script_pattern = re.compile(r'(<script[^>]*>)(.*?)(<\/script>)', re.DOTALL)
    
    updated_content = content
    
    # Tüm script bloklarını döngüye al
    for match in script_pattern.finditer(content):
        full_script_tag = match.group(0)
        script_open_tag = match.group(1)
        js_code = match.group(2)
        script_close_tag = match.group(3)

        fixed_js_code = fix_calculator_js(js_code)
        
        # Sadece JavaScript kodu gerçekten değiştiyse HTML içeriğini güncelle
        if fixed_js_code != js_code:
            updated_full_script_tag = f"{script_open_tag}{fixed_js_code}{script_close_tag}"
            updated_content = updated_content.replace(full_script_tag, updated_full_script_tag)
            print(f"  - Script bloğu güncellendi.")
        else:
            print(f"  - Script bloğunda değişiklik yapılmadı.")
    
    # HTML içinde kalan ekstra veya yinelenen CSS linklerini temizle (manuel kontrol için)
    # <link href="../css/style.css" rel="stylesheet"/> gibi durumlar için.
    
    # Bu kısmı regex ile daha sağlam hale getirelim.
    # header.css veya footer.css dışındaki "../css/" ile başlayan style.css linklerini kaldırır.
    redundant_css_pattern = re.compile(r'<link\s+href="(?:\.\./)css/style\.css"\s+rel="stylesheet"\s*\/>')
    updated_content = redundant_css_pattern.sub('', updated_content)
    if redundant_css_pattern.search(content): # Orjinal içerikte var mıydı kontrolü
        print("  - Yinelenen '../css/style.css' linki kaldırıldı.")

    # Dahili <style> etiketini kaldırma (eğer varsa, daha önce uyarmıştık)
    if '<style>' in updated_content and '</style>' in updated_content:
        updated_content = re.sub(r'<style[^>]*>.*?</style>', '', updated_content, flags=re.DOTALL)
        print("  - Dahili <style> bloğu kaldırıldı. (İçeriği style.css'e taşındığından emin olun!)")


    # Güncellenmiş içeriği orijinal dosyaya yaz
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print(f"'{filepath}' başarıyla güncellendi.")

def main():
    """Ana fonksiyon: Scriptin çalıştığı klasördeki tüm HTML dosyalarını işler."""
    # Scriptin çalıştığı dizini doğrudan kullanır
    html_folder = os.getcwd() 
    print(f"HTML dosyaları şu klasörde aranıyor: '{html_folder}'")

    if not os.path.isdir(html_folder):
        print(f"Hata: '{html_folder}' geçerli bir klasör değil. Programdan çıkılıyor.")
        return

    html_files = [f for f in os.listdir(html_folder) if f.endswith('.html') or f.endswith('.htm')]

    if not html_files:
        print(f"'{html_folder}' klasöründe HTML dosyası bulunamadı.")
        return

    print(f"'{html_folder}' klasöründeki {len(html_files)} HTML dosyası işlenecek.")
    print("-" * 30)

    for filename in html_files:
        filepath = os.path.join(html_folder, filename)
        process_html_file(filepath)
        print("-" * 30)

    print("Tüm HTML dosyaları işlendi.")

if __name__ == "__main__":
    main()