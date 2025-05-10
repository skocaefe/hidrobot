import streamlit as st
import math

# Başlık
st.markdown("<h1 style='text-align: center; color: green;'>🌿 VPD Hesaplayıcı</h1>", unsafe_allow_html=True)
st.write("Bitki seçin, nem ve sıcaklık değerlerini girin, VPD ile birlikte değerlendirme ve çözüm önerilerini görün.")

# VPD hesaplama
def calculate_vpd(temp, rh):
    svp = 0.6108 * math.exp((17.27 * temp) / (temp + 237.3))
    vpd = svp * (1 - rh / 100)
    return round(vpd, 2)

# Marul
def evaluate_vpd_for_lettuce(vpd):
    if vpd < 0.4:
        return "Çok Düşük", (
            "VPD çok düşük. Ortamda aşırı nem olabilir (%80 üzeri). Bu, mantar hastalıkları riskini artırır ve transpirasyonu azaltır. "
            "Havalandırmayı artırın ve sıcaklığı hafifçe yükselterek nemi düşürün."
        )
    elif 0.4 <= vpd < 0.6:
        return "Alt Sınır", (
            "VPD alt sınırda. Marulda tipburn (yaprak ucu yanığı) riski başlar. "
            "Havalandırmayı artırın, sıcaklığı 1-2°C artırabilirsiniz. Kalsiyum nitrat (100-150 ppm) desteği önerilir."
        )
    elif 0.6 <= vpd <= 1.0:
        return "İdeal", (
            "VPD ideal seviyede. Transpirasyon dengeli, kalsiyum taşınımı yeterli. "
            "Mevcut ortam koşulları marul için uygundur, aynı şekilde devam edin."
        )
    elif 1.0 < vpd <= 1.2:
        return "Üst Sınır", (
            "VPD üst sınıra yakın. Ortam nemi düşük olabilir. Marulda su kaybı artar. "
            "Nemlendirici veya sisleme sistemi ile nemi artırın, sıcaklığı düşürün."
        )
    else:
        return "Çok Yüksek", (
            "VPD çok yüksek. Ortamda nem çok düşük veya sıcaklık yüksek. "
            "Marul yapraklarında solgunluk ve gelişim bozukluğu olabilir. "
            "Nem oranını artırın (%60-70 hedeflenmeli), gölgeleme ile sıcaklığı azaltın."
        )

# Domates
def evaluate_vpd_for_tomato(vpd):
    if vpd < 0.4:
        return "Çok Düşük", (
            "VPD çok düşük. Yüksek nem mantar oluşumuna ve düşük transpirasyona neden olur. "
            "Çiçek çürüklüğü gibi problemler görülebilir. Havalandırmayı artırarak nemi düşürün."
        )
    elif 0.4 <= vpd < 0.6:
        return "Alt Sınır", (
            "VPD düşük. Su buharlaşması yetersiz, bu durum kök bölgesinde oksijen azlığına yol açar. "
            "Havalandırmayı iyileştirin, sıcaklığı hafif artırın."
        )
    elif 0.6 <= vpd <= 1.0:
        return "İdeal", (
            "VPD ideal. Domates için iyi bir denge sağlar. Transpirasyon yeterli, gelişim sağlıklı. "
            "Koşulları bu şekilde devam ettirin."
        )
    elif 1.0 < vpd <= 1.2:
        return "Üst Sınır", (
            "VPD yükseliyor. Yapraklardan hızlı su kaybı yaşanabilir. "
            "Nemlendirme yaparak nemi yükseltin, gölgelendirme ile sıcaklığı düşürün."
        )
    else:
        return "Çok Yüksek", (
            "VPD çok yüksek. Bu durum çiçek dökümü, meyve çatlaması ve su stresi yaratabilir. "
            "Ortam nemini artırın ve sıcaklığı düşürmek için gölgelendirme sağlayın."
        )

# Salatalık
def evaluate_vpd_for_cucumber(vpd):
    if vpd < 0.4:
        return "Çok Düşük", (
            "VPD çok düşük. Fazla nem mantar riskini artırır, bitki yüzeyinde su birikir. "
            "Havalandırma ile nemi azaltın, sıcaklığı hafif artırabilirsiniz."
        )
    elif 0.4 <= vpd < 0.6:
        return "Alt Sınır", (
            "VPD düşük. Su buharlaşması yetersiz olabilir, bu da verimi etkileyebilir. "
            "Ortamı dengelemek için nemi hafif düşürün, sıcaklığı yükseltin."
        )
    elif 0.6 <= vpd <= 1.0:
        return "İdeal", (
            "VPD ideal. Salatalık için en verimli aralıktasınız. "
            "Bu koşullar altında meyve kalitesi ve yaprak gelişimi optimaldir."
        )
    elif 1.0 < vpd <= 1.2:
        return "Üst Sınır", (
            "VPD yüksek. Bitki yapraklarında solgunluk ve kuruma riski olabilir. "
            "Sisleme ve nemlendirme sistemlerini devreye alın."
        )
    else:
        return "Çok Yüksek", (
            "VPD çok yüksek. Bu durumda su stresi ve yaprak yanıkları oluşabilir. "
            "Ortam nemini artırın ve sıcaklığı düşürmek için gölgeleme kullanın."
        )

# Çilek
def evaluate_vpd_for_strawberry(vpd):
    if vpd < 0.4:
        return "Çok Düşük", (
            "VPD çok düşük. Nem fazlalığı mantar riskini artırır, meyve çatlaması görülebilir. "
            "Havalandırmayı artırın, sıcaklığı yükselterek nemi azaltın."
        )
    elif 0.4 <= vpd < 0.6:
        return "Alt Sınır", (
            "VPD düşük. Yaprak ve meyvede fazla su birikimi olabilir. "
            "Sıcaklığı artırarak ve havalandırmayı iyileştirerek denge sağlayabilirsiniz."
        )
    elif 0.6 <= vpd <= 1.0:
        return "İdeal", (
            "VPD ideal. Çilek için en uygun ortam. "
            "Meyve kalitesi artar, hastalık riski düşer. Koşulları koruyun."
        )
    elif 1.0 < vpd <= 1.2:
        return "Üst Sınır", (
            "VPD yüksek. Meyve boyutu azalabilir, bitki stres yaşayabilir. "
            "Ortam nemini artırın ve sıcaklığı düşürün."
        )
    else:
        return "Çok Yüksek", (
            "VPD çok yüksek. Kuraklık etkisi başlar, solgunluk ve düşük verim oluşur. "
            "Nemlendirme yapın ve sıcaklığı gölgeleme ile azaltın."
        )

# Kullanıcı arayüzü
plant = st.selectbox("Bitki Seçin", ["Marul", "Domates", "Salatalık", "Çilek"])
rh = st.number_input("Bağıl Nem (%RH)", min_value=10.0, max_value=100.0, value=60.0, step=1.0)
temp = st.number_input("Sıcaklık (°C)", min_value=0.0, max_value=50.0, value=20.0, step=1.0)

if st.button("Hesapla"):
    vpd = calculate_vpd(temp, rh)

    if plant == "Marul":
        evaluation, suggestion = evaluate_vpd_for_lettuce(vpd)
    elif plant == "Domates":
        evaluation, suggestion = evaluate_vpd_for_tomato(vpd)
    elif plant == "Salatalık":
        evaluation, suggestion = evaluate_vpd_for_cucumber(vpd)
    elif plant == "Çilek":
        evaluation, suggestion = evaluate_vpd_for_strawberry(vpd)

    st.success(f"**Hesaplanan VPD:** {vpd} kPa")
    st.info(f"**Değerlendirme:** {evaluation}")
    st.write(f"📌 **Çözüm Önerisi:** {suggestion}")

st.markdown("---")
st.write("🔎 **Not:** VPD hesaplamaları Tetens formülüne dayanır. Daha hassas sonuçlar için yaprak sıcaklığı da dikkate alınmalıdır.")
