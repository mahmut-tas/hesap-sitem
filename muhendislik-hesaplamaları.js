document.addEventListener('DOMContentLoaded', function() {
    // --- MÜHENDİSLİK HESAPLAYICILARI ---

    // Kütle Denkliği Hesaplayıcı
    const massBalanceForm = document.getElementById('massBalanceForm');
    if (massBalanceForm) {
        massBalanceForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const input1 = parseFloat(document.getElementById('input1').value);
            const input2 = parseFloat(document.getElementById('input2').value);
            const outputResult = document.getElementById('massBalanceResult');

            if (isNaN(input1) || isNaN(input2)) {
                outputResult.innerHTML = '<span style="color: red;">Lütfen geçerli değerler girin.</span>';
                return;
            }
            const result = input1 + input2; // Basit bir kütle denkliği örneği
            outputResult.innerHTML = `Toplam Çıkış: <strong>${result.toFixed(2)}</strong>`;
            outputResult.style.color = '#3498db';
        });
    }

    // Enerji Denkliği Hesaplayıcı
    const energyBalanceForm = document.getElementById('energyBalanceForm');
    if (energyBalanceForm) {
        energyBalanceForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const enthalpyIn = parseFloat(document.getElementById('enthalpyIn').value);
            const workDone = parseFloat(document.getElementById('workDone').value);
            const energyResult = document.getElementById('energyBalanceResult');

            if (isNaN(enthalpyIn) || isNaN(workDone)) {
                energyResult.innerHTML = '<span style="color: red;">Lütfen geçerli değerler girin.</span>';
                return;
            }
            const netEnergy = enthalpyIn - workDone; // Basit bir enerji denkliği örneği
            energyResult.innerHTML = `Net Enerji Değişimi: <strong>${netEnergy.toFixed(2)}</strong>`;
            energyResult.style.color = '#3498db';
        });
    }

    // Reaktör Hacmi Hesaplayıcı
    const reactorVolumeForm = document.getElementById('reactorVolumeForm');
    if (reactorVolumeForm) {
        reactorVolumeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const reactionRate = parseFloat(document.getElementById('reactionRate').value); // Reaksiyon hızı (mol/L·s)
            const conversion = parseFloat(document.getElementById('conversion').value); // Dönüşüm oranı (0-1 arası)
            const flowRate = parseFloat(document.getElementById('flowRate').value); // Giriş akış hızı (L/s)
            const reactorVolumeResult = document.getElementById('reactorVolumeResult');

            if (isNaN(reactionRate) || isNaN(conversion) || isNaN(flowRate) || reactionRate <= 0 || conversion <= 0 || flowRate <= 0) {
                reactorVolumeResult.innerHTML = '<span style="color: red;">Lütfen tüm alanları geçerli değerlerle doldurun.</span>';
                return;
            }
            // Basit bir CSTR için reaktör hacmi örneği (gerçekte reaksiyon mertebesi, kinetik vb. gerekir)
            const volume = (flowRate * conversion) / reactionRate;
            reactorVolumeResult.innerHTML = `Yaklaşık Reaktör Hacmi: <strong>${volume.toFixed(2)} L</strong>`;
            reactorVolumeResult.style.color = '#3498db';
        });
    }

    // Molarite Hesaplayıcı
    const molarityForm = document.getElementById('molarityForm');
    if (molarityForm) {
        molarityForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const moles = parseFloat(document.getElementById('moles').value);
            const volume = parseFloat(document.getElementById('volume').value);
            const molarityResult = document.getElementById('molarityResult');

            if (isNaN(moles) || isNaN(volume) || volume <= 0) {
                molarityResult.innerHTML = '<span style="color: red;">Lütfen geçerli mol ve hacim değerleri girin (hacim sıfır olamaz).</span>';
                return;
            }
            const molarity = moles / volume;
            molarityResult.innerHTML = `Molarite: <strong>${molarity.toFixed(4)} M</strong>`;
            molarityResult.style.color = '#3498db';
        });
    }

    // Yoğunluk Hesaplayıcı (Kimya Mühendisliği için)
    const densityCalcForm = document.getElementById('densityCalcForm');
    if (densityCalcForm) {
        densityCalcForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const mass = parseFloat(document.getElementById('mass').value);
            const volume_den = parseFloat(document.getElementById('volume_den').value); // ID'yi değiştirdim
            const densityResult = document.getElementById('densityResult');

            if (isNaN(mass) || isNaN(volume_den) || volume_den <= 0) {
                densityResult.innerHTML = '<span style="color: red;">Lütfen geçerli kütle ve hacim değerleri girin (hacim sıfır olamaz).</span>';
                return;
            }
            const density = mass / volume_den;
            densityResult.innerHTML = `Yoğunluk: <strong>${density.toFixed(3)} kg/m³</strong>`;
            densityResult.style.color = '#3498db';
        });
    }

    // pH Hesaplayıcı
    const pHForm = document.getElementById('pHForm');
    if (pHForm) {
        pHForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const hPlusConcentration = parseFloat(document.getElementById('hPlusConcentration').value);
            const phValue = parseFloat(document.getElementById('phValue').value);
            const pHResult = document.getElementById('pHResult');
            const pHCategory = document.getElementById('pHCategory');

            pHResult.textContent = '';
            pHCategory.textContent = '';

            if (!isNaN(hPlusConcentration) && hPlusConcentration > 0) {
                const calculatedpH = -Math.log10(hPlusConcentration);
                pHResult.innerHTML = `Hesaplanan pH: <strong>${calculatedpH.toFixed(2)}</strong>`;
                if (calculatedpH < 7) pHCategory.textContent = 'Durum: Asidik';
                else if (calculatedpH > 7) pHCategory.textContent = 'Durum: Bazik';
                else pHCategory.textContent = 'Durum: Nötr';
                pHResult.style.color = '#3498db';
                pHCategory.style.color = '#666';
            } else if (!isNaN(phValue) && phValue >= 0 && phValue <= 14) {
                const calculatedHPlus = Math.pow(10, -phValue);
                pHResult.innerHTML = `Hesaplanan H+ Konsantrasyonu: <strong>${calculatedHPlus.toExponential(2)} mol/L</strong>`;
                if (phValue < 7) pHCategory.textContent = 'Durum: Asidik';
                else if (phValue > 7) pHCategory.textContent = 'Durum: Bazik';
                else pHCategory.textContent = 'Durum: Nötr';
                pHResult.style.color = '#3498db';
                pHCategory.style.color = '#666';
            } else {
                pHResult.innerHTML = '<span style="color: red;">Lütfen geçerli bir H+ konsantrasyonu veya pH değeri girin.</span>';
            }
        });
    }

    // Isı Transferi Hesaplayıcı (İletim)
    const heatTransferForm = document.getElementById('heatTransferForm');
    if (heatTransferForm) {
        heatTransferForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const k = parseFloat(document.getElementById('thermalConductivity').value);
            const A = parseFloat(document.getElementById('area').value);
            const deltaT = parseFloat(document.getElementById('tempDifference').value);
            const L = parseFloat(document.getElementById('thickness').value);
            const heatTransferResult = document.getElementById('heatTransferResult');

            if (isNaN(k) || isNaN(A) || isNaN(deltaT) || isNaN(L) || A <= 0 || L <= 0) {
                heatTransferResult.innerHTML = '<span style="color: red;">Lütfen tüm alanları geçerli değerlerle doldurun (Alan ve Kalınlık sıfır olamaz).</span>';
                return;
            }
            const Q = (k * A * deltaT) / L;
            heatTransferResult.innerHTML = `Isı Transfer Hızı (Q): <strong>${Q.toFixed(2)} Watt</strong>`;
            heatTransferResult.style.color = '#3498db';
        });
    }

    // Kütle Yüzdesi Konsantrasyonu Hesaplayıcı
    const massPercentForm = document.getElementById('massPercentForm');
    if (massPercentForm) {
        massPercentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const soluteMass = parseFloat(document.getElementById('soluteMass').value);
            const solutionMass = parseFloat(document.getElementById('solutionMass').value);
            const massPercentResult = document.getElementById('massPercentResult');

            if (isNaN(soluteMass) || isNaN(solutionMass) || solutionMass <= 0) {
                massPercentResult.innerHTML = '<span style="color: red;">Lütfen geçerli kütle değerleri girin (çözelti kütlesi sıfır olamaz).</span>';
                return;
            }
            const massPercent = (soluteMass / solutionMass) * 100;
            massPercentResult.innerHTML = `Kütle Yüzdesi: <strong>%${massPercent.toFixed(2)}</strong>`;
            massPercentResult.style.color = '#3498db';
        });
    }

    // Gaz Yoğunluğu Hesaplayıcı (İdeal Gaz)
    const gasDensityForm = document.getElementById('gasDensityForm');
    if (gasDensityForm) {
        gasDensityForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const molarMass = parseFloat(document.getElementById('molarMass').value); // g/mol
            const pressure = parseFloat(document.getElementById('pressure').value); // atm
            const temperature = parseFloat(document.getElementById('temperature').value); // Kelvin
            const gasDensityResult = document.getElementById('gasDensityResult');

            const R = 0.0821; // L·atm/(mol·K)

            if (isNaN(molarMass) || isNaN(pressure) || isNaN(temperature) || temperature <= 0 || pressure <= 0) {
                gasDensityResult.innerHTML = '<span style="color: red;">Lütfen tüm alanları geçerli değerlerle doldurun (Sıcaklık ve Basınç sıfır olamaz).</span>';
                return;
            }
            const density = (pressure * molarMass) / (R * temperature); // g/L
            gasDensityResult.innerHTML = `Gaz Yoğunluğu: <strong>${density.toFixed(3)} g/L</strong>`;
            gasDensityResult.style.color = '#3498db';
        });
    }
});