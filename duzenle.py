import os
from datetime import datetime

def create_sitemap(root_dir, base_url, output_file='sitemap.xml'):
    """
    Belirtilen bir kök dizindeki tüm HTML dosyalarını tarayarak bir XML site haritası oluşturur.

    Args:
        root_dir (str): HTML dosyalarının bulunduğu ana dizin (masaüstünüzdeki site klasörü).
        base_url (str): Sitenizin temel URL'si (örn. "https://hesapkolik.net").
        output_file (str): Oluşturulacak site haritası dosyasının adı.
    """
    urls = []
    
    # Kök dizinin varlığını kontrol et
    if not os.path.isdir(root_dir):
        print(f"Hata: Belirtilen kök dizin bulunamadı: {root_dir}")
        print("Lütfen `root_directory` değişkenini masaüstünüzdeki site klasörünün doğru yoluyla güncellediğinizden emin olun.")
        return

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            # Sadece .html veya .htm uzantılı dosyaları işle
            if filename.endswith(".html") or filename.endswith(".htm"):
                # Dosyanın kök dizine göre göreceli yolunu al
                relative_path = os.path.relpath(os.path.join(dirpath, filename), root_dir)
                
                # URL'yi oluştur. Windows'ta ters eğik çizgileri (\\) internet URL'leri için uygun olan eğik çizgilere (/) dönüştür.
                url_path = relative_path.replace(os.sep, '/')
                
                # Base URL'nin sonunda eğik çizgi yoksa ekle
                if not base_url.endswith('/'):
                    base_url += '/'
                
                # URL'yi oluştur
                full_url = f"{base_url}{url_path}"
                urls.append(full_url)

    # Site haritası XML içeriğini oluştur
    sitemap_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    # Son değiştirme tarihi için geçerli UTC zaman dilimi
    lastmod = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00") 

    for url in urls:
        sitemap_content.append(f'  <url>')
        sitemap_content.append(f'    <loc>{url}</loc>')
        sitemap_content.append(f'    <lastmod>{lastmod}</lastmod>') # Tüm sayfalar için aynı zamanı kullanır
        sitemap_content.append(f'    <changefreq>weekly</changefreq>') # Haftalık değişim sıklığı
        sitemap_content.append(f'    <priority>0.8</priority>') # Öncelik değeri
        sitemap_content.append(f'  </url>')

    sitemap_content.append('</urlset>')

    # Site haritasını dosyaya yaz
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sitemap_content))
        print(f"Site haritası başarıyla oluşturuldu: {output_file}")
    except IOError as e:
        print(f"Hata: Site haritası dosyası yazılamadı: {e}")

# --- KULLANIM ÖRNEĞİ ---
if __name__ == "__main__":
    # Masaüstünüzdeki site klasörünüzün tam yolu buraya girildi.
    root_directory = r"C:\Users\suuser\Desktop\hesap-sitem" 

    # Sitenizin temel URL'si
    base_website_url = "https://hesapkolik.net" 

    # Site haritasını oluştur
    create_sitemap(root_directory, base_website_url)

    print("\n--- ÖNEMLİ BİLGİLER ---")
    print("1. Oluşturulan `sitemap.xml` dosyası, Python kodunu çalıştırdığınız dizinde belirecektir.")
    print("2. Bu dosyayı web sitenizin ana dizinine (genellikle `public_html`, `www` veya `htdocs` klasörü) yüklemelisiniz.")
    print("3. Site haritanızı Google Search Console gibi arama motoru araçlarına göndermeyi unutmayın. Bu, sitenizin arama motorları tarafından daha iyi anlaşılmasına ve dizine eklenmesine yardımcı olur.")