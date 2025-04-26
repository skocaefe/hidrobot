# Hidrobot Başlangıç
import streamlit as st
import pandas as pd
import numpy as np

# Sayfa yapılandırması
st.set_page_config(page_title="Hidrobot", page_icon="🤖", layout="wide")

# Başlık ve açıklama
st.title("🤖 Hidrobot")
st.markdown("""
Hidroponik Besin Çözeltisi Hesaplama Aracı  
Makro ve mikro besin dengesini sağlar, EC ve pH tahmini yapar, sonuçları üretime uygun şekilde verir.
""")

# Sidebar - Proje Bilgisi
with st.sidebar:
    st.header("🔧 Ayarlar")
    st.info("""
    **Hidrobot**:
    - Seçilen gübrelerle tam reçete oluşturur.
    - İyonik dengeyi sağlar.
    - EC ve pH tahmini yapar.
    """)

# Başlangıç Değişkenleri
makro_iyonlar = ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]
mikro_elementler = ["Fe", "B", "Mn", "Zn", "Cu", "Mo"]

# İyon değerlikleri
iyon_degerlikleri = {
    "NO3": -1, "H2PO4": -1, "SO4": -2,
    "NH4": 1, "K": 1, "Ca": 2, "Mg": 2
}

# Element atom ağırlıkları (g/mol)
element_atom_agirlik = {
    "Fe": 55.845, "B": 10.81, "Mn": 54.938, "Zn": 65.38, "Cu": 63.546, "Mo": 95.95
}

# Konsantrasyon ve Tank Hacmi Varsayılan
st.sidebar.subheader("💧 Tank Ayarları")
konsantrasyon_orani = st.sidebar.number_input("Konsantrasyon Oranı (kat)", min_value=10, max_value=500, value=100, step=10)
tank_hacmi = st.sidebar.number_input("Tank Hacmi (litre)", min_value=10, max_value=1000, value=100, step=10)
# --- Reçete Girişi Bölümü ---
st.header("🧪 Reçete Girişi")

st.markdown("""
Makro ve mikro besin hedeflerinizi giriniz.  
**Makro iyonlar (mmol/L)** ve **mikro elementler (µmol/L)** ayrı ayrı belirtilmiştir.
""")

# Makro İyon Girişi
st.subheader("Makro İyon Hedefleri (mmol/L)")
makro_input = {}
cols = st.columns(4)
for i, ion in enumerate(makro_iyonlar):
    with cols[i % 4]:
        makro_input[ion] = st.number_input(
            f"{ion}", min_value=0.0, max_value=30.0, value=5.0, step=0.1, key=f"makro_{ion}"
        )

# Mikro Element Girişi
st.subheader("Mikro Element Hedefleri (µmol/L)")
mikro_input = {}
cols_mikro = st.columns(3)
for i, element in enumerate(mikro_elementler):
    with cols_mikro[i % 3]:
        mikro_input[element] = st.number_input(
            f"{element}", min_value=0.0, max_value=200.0, value=25.0, step=1.0, key=f"mikro_{element}"
        )
# --- Gübre Seçimi Bölümü ---

st.header("🧪 Gübre Seçimi")

# Makro Gübreler Tanımı
makro_gubreler = {
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2.4H2O", "iyonlar": {"Ca": 1, "NO3": 2}, "molar_agirlik": 236.15, "tank": "A"},
    "Potasyum Nitrat": {"formul": "KNO3", "iyonlar": {"K": 1, "NO3": 1}, "molar_agirlik": 101.10, "tank": "A"},
    "Magnezyum Nitrat": {"formul": "Mg(NO3)2.6H2O", "iyonlar": {"Mg": 1, "NO3": 2}, "molar_agirlik": 256.41, "tank": "A"},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "iyonlar": {"K": 1, "H2PO4": 1}, "molar_agirlik": 136.09, "tank": "B"},
    "Magnezyum Sülfat": {"formul": "MgSO4.7H2O", "iyonlar": {"Mg": 1, "SO4": 1}, "molar_agirlik": 246.51, "tank": "B"},
    "Potasyum Sülfat": {"formul": "K2SO4", "iyonlar": {"K": 2, "SO4": 1}, "molar_agirlik": 174.26, "tank": "B"},
    "Amonyum Sülfat": {"formul": "(NH4)2SO4", "iyonlar": {"NH4": 2, "SO4": 1}, "molar_agirlik": 132.14, "tank": "B"},
    "Monoamonyum Fosfat": {"formul": "NH4H2PO4", "iyonlar": {"NH4": 1, "H2PO4": 1}, "molar_agirlik": 115.03, "tank": "B"},
}

# Mikro Gübreler Tanımı
mikro_gubreler = {
    "Demir EDDHA": {"element": "Fe", "yuzde": 6},
    "Demir EDTA": {"element": "Fe", "yuzde": 13},
    "Demir DTPA": {"element": "Fe", "yuzde": 11},
    "Borak": {"element": "B", "yuzde": 11},
    "Borik Asit": {"element": "B", "yuzde": 17.5},
    "Mangan Sülfat": {"element": "Mn", "yuzde": 32},
    "Çinko Sülfat": {"element": "Zn", "yuzde": 23},
    "Bakır Sülfat": {"element": "Cu", "yuzde": 25},
    "Sodyum Molibdat": {"element": "Mo", "yuzde": 40},
}

# Makro Gübre Seçimi
st.subheader("Makro Gübre Seçimi (Tank A ve B)")
secilen_makro_gubreler = []
for gubre in makro_gubreler:
    if st.checkbox(f"{gubre} ({makro_gubreler[gubre]['formul']})", key=f"makro_sec_{gubre}"):
        secilen_makro_gubreler.append(gubre)

# Mikro Gübre Seçimi
st.subheader("Mikro Gübre Seçimi")
secilen_mikro_gubreler = {}
for element in mikro_elementler:
    uygun_gubreler = [gubre for gubre, bilgi in mikro_gubreler.items() if bilgi["element"] == element]
    secim = st.radio(f"{element} için kullanılacak gübre:", ["Seçilmedi"] + uygun_gubreler, horizontal=True, key=f"mikro_sec_{element}")
    if secim != "Seçilmedi":
        secilen_mikro_gubreler[element] = secim
# --- Hesaplama Bölümü ---

st.header("🧮 Hesaplama ve Sonuçlar")

if st.button("🚀 HESAPLA"):
    if not secilen_makro_gubreler:
        st.error("Lütfen en az bir makro gübre seçin!")
    else:
        try:
            # --- 1. Makro Hesaplama ---
            # Matrisleri oluştur
            hedef_iyonlar = np.array([makro_input[ion] for ion in makro_iyonlar])

            A = []
            for gubre in secilen_makro_gubreler:
                sutun = []
                for ion in makro_iyonlar:
                    sutun.append(makro_gubreler[gubre]["iyonlar"].get(ion, 0))
                A.append(sutun)
            A = np.array(A).T  # İyonlar satırda, gübreler sütunda olacak

            # Denklem çözümü
            sonuc, residuals, rank, s = np.linalg.lstsq(A, hedef_iyonlar, rcond=None)

            # Sonuçları toplama
            gubre_sonuc = {}
            for idx, gubre in enumerate(secilen_makro_gubreler):
                mmol_per_l = sonuc[idx]
                mg_per_l = mmol_per_l * makro_gubreler[gubre]["molar_agirlik"]
                toplam_gram = mg_per_l * konsantrasyon_orani * tank_hacmi / 1000  # gram cinsinden
                gubre_sonuc[gubre] = toplam_gram / 1000  # kg cinsinden

            # --- 2. Mikro Hesaplama ---
            mikro_sonuc = {}
            for element in mikro_elementler:
                hedef_umol = mikro_input[element]
                if element in secilen_mikro_gubreler:
                    secilen = secilen_mikro_gubreler[element]
                    yuzde = mikro_gubreler[secilen]["yuzde"]
                    element_agirlik = element_atom_agirlik[element]
                    mg_per_l = (hedef_umol / 1000) * element_agirlik
                    toplam_mg = mg_per_l * konsantrasyon_orani * tank_hacmi
                    gerekli_gubre_mg = toplam_mg * 100 / yuzde
                    mikro_sonuc[secilen] = gerekli_gubre_mg / 1000  # gram cinsinden

            # --- 3. EC ve pH Tahmini ---
            toplam_mmol = sum(makro_input[ion] for ion in makro_iyonlar)
            tahmini_ec = toplam_mmol * 0.64  # Basit hidroponik çarpan

            nh4_orani = makro_input["NH4"] / (makro_input["NO3"] + 0.0001)
            if nh4_orani < 0.1:
                ph_yorum = "Tahmini pH: Nötr veya hafif alkali (6.5-7.0)"
            elif nh4_orani < 0.25:
                ph_yorum = "Tahmini pH: Hafif asidik (6.0-6.5)"
            else:
                ph_yorum = "Tahmini pH: Asidik (5.5-6.0)"

            # --- 4. Sonuçları Göster ---
            with st.expander("📦 Makro Gübre Sonuçları"):
                st.subheader("A ve B Tankı Gübreleri (kg)")
                makro_df = pd.DataFrame(gubre_sonuc.items(), columns=["Gübre", "Kg (Tank Başına)"])
                st.dataframe(makro_df.style.format({"Kg (Tank Başına)": "{:.3f}"}))

            with st.expander("🌱 Mikro Gübre Sonuçları"):
                st.subheader("Mikro Elementler (gram)")
                if mikro_sonuc:
                    mikro_df = pd.DataFrame(mikro_sonuc.items(), columns=["Mikro Gübre", "Gram (Tank Başına)"])
                    st.dataframe(mikro_df.style.format({"Gram (Tank Başına)": "{:.1f}"}))
                else:
                    st.info("Seçilen mikro gübre bulunamadı.")

            with st.expander("⚡ EC ve pH Tahmini"):
                st.metric("Tahmini EC", f"{tahmini_ec:.2f} dS/m")
                st.success(ph_yorum)

            st.success("✅ Hesaplama tamamlandı. Yukarıdaki miktarları kullanabilirsiniz.")

        except Exception as e:
            st.error(f"Hesaplama yapılamadı: {str(e)}")
            st.warning("Seçtiğiniz gübrelerle tam reçete oluşturulamıyor olabilir. Lütfen gübre seçiminizi kontrol edin.")
