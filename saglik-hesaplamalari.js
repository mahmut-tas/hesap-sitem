// js/saglik-hesaplamalari.js

document.addEventListener('DOMContentLoaded', function() {
    // --- BMI Hesaplayıcı ---
    const bmiForm = document.getElementById('bmiForm');
    if (bmiForm) {
        bmiForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const heightCm = parseFloat(document.getElementById('bmi_height').value);
            const weightKg = parseFloat(document.getElementById('bmi_weight').value);
            const bmiResultDiv = document.getElementById('bmiResult');
            const bmiCategoryDiv = document.getElementById('bmiCategory');

            if (isNaN(heightCm) || isNaN(weightKg) || heightCm <= 0 || weightKg <= 0) {
                bmiResultDiv.innerHTML = '<span style="color: red;">Lütfen geçerli boy ve kilo değerleri girin.</span>';
                bmiCategoryDiv.textContent = '';
                return;
            }
            const heightM = heightCm / 100;
            const bmi = weightKg / (heightM * heightM);
            bmiResultDiv.innerHTML = `BMI Değeriniz: <strong>${bmi.toFixed(2)}</strong>`;
            let category = '';
            let categoryColor = '#333';
            if (bmi < 18.5) {
                category = 'Zayıf';
                categoryColor = '#f1c40f'; // Sarı
            } else if (bmi >= 18.5 && bmi < 24.9) {
                category = 'Normal Kilolu';
                categoryColor = '#2ecc71'; // Yeşil
            } else if (bmi >= 25 && bmi < 29.9) {
                category = 'Fazla Kilolu';
                categoryColor = '#e74c3c'; // Kırmızımsı turuncu
            } else if (bmi >= 30 && bmi < 34.9) {
                category = 'Obez (Sınıf I)';
                categoryColor = '#c0392b'; // Kırmızı
            } else if (bmi >= 35 && bmi < 39.9) {
                category = 'Obez (Sınıf II)';
                categoryColor = '#a52a2a'; // Koyu kırmızı
            } else {
                category = 'Aşırı Obez (Sınıf III)';
                categoryColor = '#8b0000'; // Çok koyu kırmızı
            }
            bmiCategoryDiv.textContent = `Durumunuz: ${category}`;
            bmiCategoryDiv.style.color = categoryColor;
        });
    }

    // --- İdeal Kilo Hesaplayıcı ---
    const idealWeightForm = document.getElementById('idealWeightForm');
    if (idealWeightForm) {
        idealWeightForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const heightCm = parseFloat(document.getElementById('iw_height').value);
            const age = parseFloat(document.getElementById('iw_age').value);
            const gender = document.getElementById('iw_gender').value;
            const idealWeightResultDiv = document.getElementById('idealWeightResult');
            const idealWeightCategoryDiv = document.getElementById('idealWeightCategory');

            if (isNaN(heightCm) || isNaN(age) || heightCm <= 0 || age <= 0) {
                idealWeightResultDiv.innerHTML = '<span style="color: red;">Lütfen geçerli boy ve yaş değerleri girin.</span>';
                idealWeightCategoryDiv.textContent = '';
                return;
            }
            let idealWeightMin, idealWeightMax;
            if (gender === 'male') {
                idealWeightMin = (heightCm - 100) * 0.9;
                idealWeightMax = (heightCm - 100) * 1.1;
            } else {
                idealWeightMin = (heightCm - 105) * 0.9;
                idealWeightMax = (heightCm - 105) * 1.1;
            }
            idealWeightResultDiv.innerHTML = `İdeal Kilonuz: <strong>${idealWeightMin.toFixed(1)} kg - ${idealWeightMax.toFixed(1)} kg</strong> arası`;
            idealWeightCategoryDiv.textContent = 'Bu, boyunuza, yaşınıza ve cinsiyetinize göre önerilen ideal kilo aralığıdır.';
            idealWeightCategoryDiv.style.color = '#3498db';
        });
    }

    // --- Günlük Kalori İhtiyacı Hesaplayıcı ---
    const calorieForm = document.getElementById('calorieForm');
    if (calorieForm) {
        calorieForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const age = parseFloat(document.getElementById('cal_age').value);
            const gender = document.getElementById('cal_gender').value;
            const heightCm = parseFloat(document.getElementById('cal_height').value);
            const weightKg = parseFloat(document.getElementById('cal_weight').value);
            const activityLevel = parseFloat(document.getElementById('activity_level').value);
            const calorieResultDiv = document.getElementById('calorieResult');
            const calorieGoalDiv = document.getElementById('calorieGoal');

            if (isNaN(age) || isNaN(heightCm) || isNaN(weightKg) || age <= 0 || heightCm <= 0 || weightKg <= 0) {
                calorieResultDiv.innerHTML = '<span style="color: red;">Lütfen tüm alanları geçerli değerlerle doldurun.</span>';
                calorieGoalDiv.textContent = '';
                return;
            }
            let bmr;
            if (gender === 'male') {
                bmr = (10 * weightKg) + (6.25 * heightCm) - (5 * age) + 5;
            } else {
                bmr = (10 * weightKg) + (6.25 * heightCm) - (5 * age) - 161;
            }
            const tdee = bmr * activityLevel;
            calorieResultDiv.innerHTML = `Günlük Kalori İhtiyacınız: <strong>${tdee.toFixed(0)} kcal</strong>`;
            calorieGoalDiv.textContent = `Bu miktar, mevcut kilonuzu korumanız için gereken tahmini kaloridir.`;
            calorieGoalDiv.style.color = '#3498db';
        });
    }

    // --- Günlük Su İhtiyacı Hesaplayıcı ---
    const waterForm = document.getElementById('waterForm');
    if (waterForm) {
        waterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const weightKg = parseFloat(document.getElementById('water_weight').value);
            const activityLevel = document.getElementById('water_activity').value;
            const waterResultDiv = document.getElementById('waterResult');
            const waterTipDiv = document.getElementById('waterTip');

            if (isNaN(weightKg) || weightKg <= 0) {
                waterResultDiv.innerHTML = '<span style="color: red;">Lütfen geçerli kilonuzu girin.</span>';
                waterTipDiv.textContent = '';
                return;
            }
            let baseWaterMl = weightKg * 30;
            if (activityLevel === 'medium') {
                baseWaterMl = weightKg * 35;
            } else if (activityLevel === 'high') {
                baseWaterMl = weightKg * 40;
            }
            const waterLiters = baseWaterMl / 1000;
            waterResultDiv.innerHTML = `Günlük Su İhtiyacınız: <strong>${waterLiters.toFixed(2)} Litre</strong>`;
            waterTipDiv.textContent = 'Su tüketiminizi gün içine yayarak ve aktivitenize göre artırarak sağlığınızı destekleyin.';
            waterTipDiv.style.color = '#3498db';
        });
    }

    // --- Günlük Karbonhidrat İhtiyacı Hesaplayıcı ---
    const carbForm = document.getElementById('carbForm');
    if (carbForm) {
        carbForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const totalCalories = parseFloat(document.getElementById('carb_calorie').value);
            const carbPercentage = parseFloat(document.getElementById('carb_percentage').value) / 100;
            const carbResultDiv = document.getElementById('carbResult');
            const carbTipDiv = document.getElementById('carbTip');

            if (isNaN(totalCalories) || isNaN(carbPercentage) || totalCalories <= 0 || carbPercentage <= 0) {
                carbResultDiv.innerHTML = '<span style="color: red;">Lütfen geçerli kalori ve yüzde değerleri girin.</span>';
                carbTipDiv.textContent = '';
                return;
            }
            const carbCalories = totalCalories * carbPercentage;
            const carbGrams = carbCalories / 4;
            carbResultDiv.innerHTML = `Günlük Karbonhidrat İhtiyacınız: <strong>${carbGrams.toFixed(0)} Gram</strong>`;
            carbTipDiv.textContent = `Toplam kalori alımınızın yaklaşık %${(carbPercentage * 100).toFixed(0)}'ı karbonhidratlardan gelmelidir.`;
            carbTipDiv.style.color = '#3498db';
        });
    }

    // --- Günlük Protein İhtiyacı Hesaplayıcı ---
    const proteinForm = document.getElementById('proteinForm');
    if (proteinForm) {
        proteinForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const weightKg = parseFloat(document.getElementById('protein_weight').value);
            const activityFactor = parseFloat(document.getElementById('protein_activity').value);
            const proteinResultDiv = document.getElementById('proteinResult');
            const proteinTipDiv = document.getElementById('proteinTip');

            if (isNaN(weightKg) || isNaN(activityFactor) || weightKg <= 0) {
                proteinResultDiv.innerHTML = '<span style="color: red;">Lütfen geçerli kilo ve aktivite seviyesi girin.</span>';
                proteinTipDiv.textContent = '';
                return;
            }
            const proteinGrams = weightKg * activityFactor;
            proteinResultDiv.innerHTML = `Günlük Protein İhtiyacınız: <strong>${proteinGrams.toFixed(0)} Gram</strong>`;
            proteinTipDiv.textContent = `Aktivite seviyenize göre kg başına ${activityFactor} gram protein önerilir.`;
            proteinTipDiv.style.color = '#3498db';
        });
    }

    // --- Adet (Aybaşı) Döngüsü Takibi ---
    const menstrualCycleForm = document.getElementById('menstrualCycleForm');
    if (menstrualCycleForm) {
        menstrualCycleForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const lastPeriodDate = new Date(document.getElementById('lastPeriodDate').value);
            const cycleLength = parseInt(document.getElementById('cycleLength').value);
            const menstrualResultDiv = document.getElementById('menstrualResult');
            const ovulationResultDiv = document.getElementById('ovulationResult');
            const fertileWindowDiv = document.getElementById('fertileWindow');

            if (isNaN(lastPeriodDate.getTime()) || isNaN(cycleLength) || cycleLength < 20 || cycleLength > 45) {
                menstrualResultDiv.innerHTML = '<span style="color: red;">Lütfen geçerli tarih ve döngü uzunluğu girin (20-45 gün arası).</span>';
                ovulationResultDiv.textContent = '';
                fertileWindowDiv.textContent = '';
                return;
            }
            const nextPeriodDate = new Date(lastPeriodDate);
            nextPeriodDate.setDate(lastPeriodDate.getDate() + cycleLength);
            const ovulationDate = new Date(nextPeriodDate);
            ovulationDate.setDate(nextPeriodDate.getDate() - 14);
            const fertileStart = new Date(ovulationDate);
            fertileStart.setDate(ovulationDate.getDate() - 5);
            const fertileEnd = new Date(ovulationDate);
            const options = { year: 'numeric', month: 'long', day: 'numeric' };

            menstrualResultDiv.innerHTML = `Tahmini Bir Sonraki Adet Başlangıcı: <strong>${nextPeriodDate.toLocaleDateString('tr-TR', options)}</strong>`;
            ovulationResultDiv.innerHTML = `Tahmini Yumurtlama Günü: <strong>${ovulationDate.toLocaleDateString('tr-TR', options)}</strong>`;
            fertileWindowDiv.innerHTML = `Tahmini Doğurganlık Penceresi: <strong>${fertileStart.toLocaleDateString('tr-TR', options)} - ${fertileEnd.toLocaleDateString('tr-TR', options)}</strong>`;
            
            menstrualResultDiv.style.color = '#3498db';
            ovulationResultDiv.style.color = '#2ecc71';
            fertileWindowDiv.style.color = '#e74c3c';
        });
    }

    // --- Hedef Nabız Bölgesi Hesaplayıcı ---
    const heartRateForm = document.getElementById('heartRateForm');
    if (heartRateForm) {
        heartRateForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const age = parseInt(document.getElementById('hr_age').value);
            const heartRateResultDiv = document.getElementById('heartRateResult');
            const heartRateCategoryDiv = document.getElementById('heartRateCategory');

            if (isNaN(age) || age < 10 || age > 90) {
                heartRateResultDiv.innerHTML = '<span style="color: red;">Lütfen geçerli bir yaş değeri girin (10-90 arası).</span>';
                heartRateCategoryDiv.textContent = '';
                return;
            }
            const maxHeartRate = 220 - age;
            const fatBurnMin = Math.round(maxHeartRate * 0.50);
            const fatBurnMax = Math.round(maxHeartRate * 0.70);
            const cardioMin = Math.round(maxHeartRate * 0.70);
            const cardioMax = Math.round(maxHeartRate * 0.85);
            heartRateResultDiv.innerHTML = `Maksimum Kalp Atış Hızınız: <strong>${maxHeartRate} bpm</strong>`;
            heartRateCategoryDiv.innerHTML = `
                <br>
                <strong>Yağ Yakım Bölgesi:</strong> ${fatBurnMin} - ${fatBurnMax} bpm <br>
                <strong>Kardiyo Bölgesi:</strong> ${cardioMin} - ${cardioMax} bpm
            `;
            heartRateResultDiv.style.color = '#333';
            heartRateCategoryDiv.style.color = '#3498db';
        });
    }
});