
# Hidrobot V3 - app.py (Çalışır sürüm)

import streamlit as st
import pandas as pd
import numpy as np

# --- Sayfa Ayarları ---
st.set_page_config(page_title="Hidrobot V3", page_icon="🤖", layout="wide")
st.title("🤖 Hidrobot V3 - Hidroponik Besin Çözeltisi Hesaplayıcı")
st.markdown("""
Bu uygulama:
- Reçete oluşturur
- Gübre seçimi yapar
- Anyon/Katyon dengesini kontrol eder
- EC tahmini yapar
- Çözeltinin nasıl hazırlanacağını adım adım anlatır
**Su sıcaklığı 20°C kabul edilir. Önce su, sonra gübre eklenir.**
""")

# --- Tanımlar ---
makro_iyonlar = ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]
mikro_elementler = ["Fe", "B", "Mn", "Zn", "Cu", "Mo"]

iyon_degerlikleri = {"NO3": -1, "H2PO4": -1, "SO4": -2, "NH4": 1, "K": 1, "Ca": 2, "Mg": 2}
element_atom_agirlik = {"Fe": 55.845, "B": 10.81, "Mn": 54.938, "Zn": 65.38, "Cu": 63.546, "Mo": 95.95}

makro_gubreler = {
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2·4H2O", "iyonlar": {"Ca":1,"NO3":2}, "molar_agirlik":236.15, "tank":"A"},
    "Potasyum Nitrat": {"formul": "KNO3", "iyonlar": {"K":1,"NO3":1}, "molar_agirlik":101.1, "tank":"A"},
    "Magnezyum Nitrat": {"formul": "Mg(NO3)2·6H2O", "iyonlar": {"Mg":1,"NO3":2}, "molar_agirlik":256.41, "tank":"A"},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "iyonlar": {"K":1,"H2PO4":1}, "molar_agirlik":136.09, "tank":"B"},
    "Magnezyum Sülfat": {"formul": "MgSO4·7H2O", "iyonlar": {"Mg":1,"SO4":1}, "molar_agirlik":246.51, "tank":"B"},
    "Potasyum Sülfat": {"formul": "K2SO4", "iyonlar": {"K":2,"SO4":1}, "molar_agirlik":174.26, "tank":"B"},
    "Amonyum Sülfat": {"formul": "(NH4)2SO4", "iyonlar": {"NH4":2,"SO4":1}, "molar_agirlik":132.14, "tank":"B"},
    "Monoamonyum Fosfat": {"formul": "NH4H2PO4", "iyonlar": {"NH4":1,"H2PO4":1}, "molar_agirlik":115.03, "tank":"B"},
}

# --- Tank Ayarları ---
with st.sidebar:
    st.header("🔧 Tank Ayarları")
    konsantrasyon = st.number_input("Konsantrasyon (kat)", min_value=10, max_value=500, value=100, step=10)
    hacim = st.number_input("Tank Hacmi (litre)", min_value=10, max_value=2000, value=100, step=10)

# --- Reçete Girişi ---
st.header("🧪 Reçete Girişi")
makro = {}
mikro = {}

makro_cols = st.columns(4)
for idx, ion in enumerate(makro_iyonlar):
    with makro_cols[idx%4]:
        makro[ion] = st.number_input(f"{ion} (mmol/L)", min_value=0.0, value=5.0, step=0.1)

mikro_cols = st.columns(3)
for idx, el in enumerate(mikro_elementler):
    with mikro_cols[idx%3]:
        mikro[el] = st.number_input(f"{el} (µmol/L)", min_value=0.0, value=25.0, step=1.0)

# --- Gübre Seçimi ---
st.header("🧪 Gübre Seçimi")
secilen_gubreler = []
for gubre in makro_gubreler:
    if st.checkbox(gubre):
        secilen_gubreler.append(gubre)

# --- Hesaplama ---
if st.button("🚀 Hesapla"):
    hedef = np.array([makro[ion] for ion in makro_iyonlar])
    A = []
    for gubre in secilen_gubreler:
        A.append([makro_gubreler[gubre]["iyonlar"].get(ion,0) for ion in makro_iyonlar])
    A = np.array(A).T

    try:
        sonuc, _, _, _ = np.linalg.lstsq(A, hedef, rcond=None)
        mevcut = A @ sonuc
        fark = mevcut - hedef

        st.success("✅ Hesaplama başarılı!")

        # Tank ayırımı
        a_tank = []
        b_tank = []
        for idx, gubre in enumerate(secilen_gubreler):
            mmol = sonuc[idx]
            mg_l = mmol * makro_gubreler[gubre]["molar_agirlik"]
            toplam_g = mg_l * konsantrasyon * hacim / 1000
            if makro_gubreler[gubre]["tank"] == "A":
                a_tank.append((gubre, toplam_g/1000))
            else:
                b_tank.append((gubre, toplam_g/1000))

        st.subheader("📦 A Tankı")
        st.dataframe(pd.DataFrame(a_tank, columns=["Gübre", "Kg"]))

        st.subheader("📦 B Tankı")
        st.dataframe(pd.DataFrame(b_tank, columns=["Gübre", "Kg"]))

        st.subheader("🔎 Anyon/Katyon Dengesi")
        anyon_toplam = sum(makro[ion] * abs(iyon_degerlikleri[ion]) for ion in ["NO3","H2PO4","SO4"])
        katyon_toplam = sum(makro[ion] * abs(iyon_degerlikleri[ion]) for ion in ["NH4","K","Ca","Mg"])
        st.write(f"Anyon: {anyon_toplam:.2f} me/L | Katyon: {katyon_toplam:.2f} me/L")

        fark_denge = abs(anyon_toplam - katyon_toplam)
        if fark_denge <= 0.5:
            st.success("✅ İyonik denge uygun.")
        else:
            st.warning("⚠️ İyon dengesinde sapma var! EC yükselebilir.")

        # EC tahmini
        toplam_mmol = sum(makro.values())
        tahmini_ec = toplam_mmol * 0.64
        st.metric("Tahmini EC", f"{tahmini_ec:.2f} dS/m")

        with st.expander("🧴 Çözelti Nasıl Hazırlanır?"):
            st.markdown("""
            1. Tankı %70 saf suyla doldurun.
            2. Seçilen gübreleri sırayla ekleyin ve iyice çözünene kadar karıştırın.
            3. Gerekirse su ekleyerek tankı tamamlayın.
            4. EC ve pH kontrolü yapın.
            5. Sisteme aktarın.
            """)

    except Exception as e:
        st.error(f"Hesaplama Hatası: {e}")
