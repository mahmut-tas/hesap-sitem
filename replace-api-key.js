// replace-api-key.js
const fs = require('fs'); // Dosya sistemi işlemleri için Node.js modülü

const htmlFilePath = 'rota-hesaplayici.html'; // HTML dosyanızın yolu
const placeholder = 'YOUR_Maps_API_KEY_PLACEHOLDER'; // HTML'deki yer tutucu metin
const apiKey = process.env.MAPS_API_KEY; // GitHub Actions Secret'tan gelen API anahtarı

if (!apiKey) {
    console.error('HATA: MAPS_API_KEY ortam değişkeni tanımlı değil.');
    process.exit(1); // Hata ile çık
}

fs.readFile(htmlFilePath, 'utf8', (err, data) => {
    if (err) {
        console.error(`HTML dosyasını okurken hata oluştu: ${err}`);
        process.exit(1);
    }

    // Yer tutucuyu API anahtarıyla değiştir
    // 'g' bayrağı tüm eşleşmeleri değiştirmeyi sağlar
    const result = data.replace(new RegExp(placeholder, 'g'), apiKey);

    fs.writeFile(htmlFilePath, result, 'utf8', (err) => {
        if (err) {
            console.error(`HTML dosyasına yazarken hata oluştu: ${err}`);
            process.exit(1);
        }
        console.log('API anahtarı başarıyla HTML dosyasına enjekte edildi!');
    });
});
