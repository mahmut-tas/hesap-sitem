<?php
// Bu kısım, formun sadece POST metodu ile gönderilip gönderilmediğini kontrol eder.
// Direkt olarak bu dosyaya erişilirse, ana sayfaya yönlendirilir.
if ($_SERVER["REQUEST_METHOD"] == "POST") {

    // 1. Formdan Gelen Verileri Al ve Temizle
    // strip_tags: HTML ve PHP etiketlerini kaldırır.
    // trim: Metnin başındaki ve sonundaki boşlukları siler.
    // filter_var: E-posta adresini güvenli hale getirir ve doğrular.
    $name = strip_tags(trim($_POST["name"]));
    $email = filter_var(trim($_POST["email"]), FILTER_SANITIZE_EMAIL);
    $subject = strip_tags(trim($_POST["subject"]));
    $message = trim($_POST["message"]);

    // 2. Zorunlu Alan Kontrolü
    // Bu alanlardan herhangi biri boşsa, hata mesajı göster ve işlemi durdur.
    if (empty($name) || !filter_var($email, FILTER_VALIDATE_EMAIL) || empty($subject) || empty($message)) {
        http_response_code(400); // Bad Request
        echo "Lütfen tüm alanları doldurduğunuzdan ve geçerli bir e-posta adresi girdiğinizden emin olun.";
        exit;
    }

    // 3. E-posta Ayarları
    // Formun gönderileceği e-posta adresi
    $recipient = "mahmut.tas90@gmail.com"; // BURASI SİZİN E-POSTA ADRESİNİZ!

    // Size gelecek e-postanın konusu
    $email_subject = "Hesapla Pratik İletişim Formu: " . $subject;

    // Size gelecek e-postanın içeriği
    $email_body = "Ad Soyad: " . $name . "\n";
    $email_body .= "E-posta: " . $email . "\n\n";
    $email_body .= "Konu: " . $subject . "\n\n";
    $email_body .= "Mesaj:\n" . $message . "\n";

    // E-posta başlıkları
    // "From": E-postanın kimden geldiğini belirtir (genellikle gönderenin adı ve e-postası).
    // "Reply-To": Yanıtladığınızda kime gideceğini belirtir (gönderenin e-postası).
    // "Content-Type": E-postanın içeriğinin UTF-8 karakter setinde düz metin olduğunu belirtir.
    $headers = "From: " . $name . " <" . $email . ">\r\n";
    $headers .= "Reply-To: " . $email . "\r\n";
    $headers .= "MIME-Version: 1.0\r\n";
    $headers .= "Content-Type: text/plain; charset=UTF-8\r\n";

    // 4. E-postayı Gönder ve Kullanıcıyı Yönlendir
    // mail() fonksiyonu e-postayı göndermeyi dener.
    if (mail($recipient, $email_subject, $email_body, $headers)) {
        // E-posta başarıyla gönderilirse, kullanıcıyı bir teşekkür sayfasına yönlendir.
        // Bu sayfayı (tesekkurler.html) oluşturmanız tavsiye edilir.
        header("Location: tesekkurler.html");
        exit; // Yönlendirme sonrası betiğin çalışmasını durdur.
    } else {
        // E-posta gönderiminde bir hata oluşursa, kullanıcıya bilgi ver.
        http_response_code(500); // Internal Server Error
        echo "Mesajınız gönderilirken bir sorun oluştu. Lütfen daha sonra tekrar deneyin.";
    }

} else {
    // Form direkt olarak bu sayfaya erişilirse, izinsiz erişimi engellemek için
    // kullanıcıyı ana sayfaya geri yönlendir.
    header("Location: index.html");
    exit;
}
?>