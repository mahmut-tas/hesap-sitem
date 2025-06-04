document.addEventListener('DOMContentLoaded', () => {
    console.log("Hesapla Pratik ana sayfası yüklendi!");

    // Örnek: Smooth scroll için (navigasyondaki #calculator-list linki için)
    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    for (let link of smoothScrollLinks) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            let targetId = this.getAttribute('href');
            if (targetId.length > 1 && document.querySelector(targetId)) { // Hedefin varlığını kontrol et
                 document.querySelector(targetId).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    }

    // İleride buraya daha fazla JavaScript kodu eklenebilir
    // Örneğin, bir arama çubuğu, dinamik içerik yükleme vb.
});