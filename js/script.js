document.addEventListener('DOMContentLoaded', () => {
    console.log("Hesapla Pratik ana sayfası yüklendi!");

    // Örnek: Smooth scroll için
    // Sadece 'smooth-scroll' sınıfına sahip A etiketlerini dinle
    const smoothScrollLinks = document.querySelectorAll('a.smooth-scroll[href^="#"]'); 
    
    for (let link of smoothScrollLinks) {
        link.addEventListener('click', function (e) {
            e.preventDefault(); // Varsayılan link davranışını engelle
            let targetId = this.getAttribute('href');
            
            // Hedef ID'nin varlığını kontrol et ve boş değilse kaydır
            if (targetId.length > 1 && document.querySelector(targetId)) { 
                document.querySelector(targetId).scrollIntoView({
                    behavior: 'smooth' // Yumuşak kaydırma efekti
                });
            }
        });
    }

    // İleride buraya daha fazla JavaScript kodu eklenebilir
    // Örneğin, bir arama çubuğu, dinamik içerik yükleme vb.
});