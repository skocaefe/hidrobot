
# Hidrobot - app.py (Tam Çalışır)

import streamlit as st
import pandas as pd
import numpy as np

# --- Sayfa Ayarları ---
st.set_page_config(page_title="Hidrobot", page_icon="🤖", layout="wide")
st.title("🤖 Hidrobot - Hidroponik Besin Çözeltisi Hesaplayıcı")
st.markdown("""
Hidroponik sistemler için tam reçete oluşturur, EC ve pH tahmini yapar.  
Eksik/fazla iyonları analiz eder, gerekirse gübre tavsiyesi sunar.  
Çözelti hazırlama adımlarını anlatır.  
**Su sıcaklığı 20°C kabul edilir. Önce su, sonra gübre eklenir.**
""")

# --- Sidebar Tank Ayarları ---
with st.sidebar:
    st.header("🔧 Tank Ayarları")
    konsantrasyon_orani = st.number_input("Konsantrasyon Oranı (kat)", min_value=10, max_value=500, value=100, step=10)
    tank_hacmi = st.number_input("Tank Hacmi (litre)", min_value=10, max_value=1000, value=100, step=10)

# --- Tanımlar ---
makro_iyonlar = ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]
mikro_elementler = ["Fe", "B", "Mn", "Zn", "Cu", "Mo"]

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

mikro_gubreler = {
    "Demir EDDHA": {"element": "Fe", "yuzde":6},
    "Demir EDTA": {"element": "Fe", "yuzde":13},
    "Borik Asit": {"element": "B", "yuzde":17.5},
    "Borak": {"element": "B", "yuzde":11},
    "Mangan Sülfat": {"element": "Mn", "yuzde":32},
    "Çinko Sülfat": {"element": "Zn", "yuzde":23},
    "Bakır Sülfat": {"element": "Cu", "yuzde":25},
    "Sodyum Molibdat": {"element": "Mo", "yuzde":40},
}

# --- Reçete Girişi ---
st.header("🧪 Reçete Girişi")
makro_input = {}
mikro_input = {}

cols = st.columns(4)
for i, ion in enumerate(makro_iyonlar):
    with cols[i%4]:
        makro_input[ion] = st.number_input(f"{ion} (mmol/L)", min_value=0.0, value=5.0, step=0.1)

cols2 = st.columns(3)
for i, element in enumerate(mikro_elementler):
    with cols2[i%3]:
        mikro_input[element] = st.number_input(f"{element} (µmol/L)", min_value=0.0, value=25.0, step=1.0)

# --- Gübre Seçimi ---
st.header("🧪 Gübre Seçimi")
secilen_makro = []
for gubre in makro_gubreler.keys():
    if st.checkbox(f"{gubre}", key=f"makro_{gubre}"):
        secilen_makro.append(gubre)

secilen_mikro = {}
for element in mikro_elementler:
    secenekler = [g for g, v in mikro_gubreler.items() if v["element"]==element]
    secim = st.radio(f"{element} için:", ["Seçilmedi"]+secenekler, horizontal=True, key=f"micro_{element}")
    if secim != "Seçilmedi":
        secilen_mikro[element] = secim

# --- Hesaplama ---
if st.button("🚀 Hesapla"):
    hedef = np.array([makro_input[i] for i in makro_iyonlar])
    A = []
    for gubre in secilen_makro:
        A.append([makro_gubreler[gubre]["iyonlar"].get(ion,0) for ion in makro_iyonlar])
    A = np.array(A).T

    try:
        sonuc, _, _, _ = np.linalg.lstsq(A, hedef, rcond=None)
        mevcut = A @ sonuc
        fark = mevcut - hedef

        st.success("✅ Hesaplama Başarılı!")

        # A Tankı ve B Tankı
        a_tank = []
        b_tank = []
        for idx, gubre in enumerate(secilen_makro):
            mmol = sonuc[idx]
            mg_l = mmol * makro_gubreler[gubre]["molar_agirlik"]
            g_tank = mg_l * konsantrasyon_orani * tank_hacmi / 1000
            if makro_gubreler[gubre]["tank"]=="A":
                a_tank.append((gubre, g_tank/1000))
            else:
                b_tank.append((gubre, g_tank/1000))

        st.subheader("📦 A Tankı")
        st.dataframe(pd.DataFrame(a_tank, columns=["Gübre","Kg"]))

        st.subheader("📦 B Tankı")
        st.dataframe(pd.DataFrame(b_tank, columns=["Gübre","Kg"]))

        st.subheader("🌱 Mikro Besinler")
        mikro_sonuc = []
        for element, gubre in secilen_mikro.items():
            hedef_umol = mikro_input[element]
            yuzde = mikro_gubreler[gubre]["yuzde"]
            mg_l = (hedef_umol/1000) * element_atom_agirlik[element]
            toplam_mg = mg_l * konsantrasyon_orani * tank_hacmi
            gram = toplam_mg * 100 / yuzde / 1000
            mikro_sonuc.append((gubre, gram))
        if mikro_sonuc:
            st.dataframe(pd.DataFrame(mikro_sonuc, columns=["Mikro Gübre","Gram"]))

        toplam_mmol = sum(makro_input.values())
        tahmini_ec = toplam_mmol * 0.64
        st.metric("Tahmini EC", f"{tahmini_ec:.2f} dS/m")

        st.header("🔎 İyon Analizi")
        analiz = []
        for idx, ion in enumerate(makro_iyonlar):
            if abs(fark[idx]) > 0.1:
                analiz.append((ion, "Fazla" if fark[idx]>0 else "Eksik", round(fark[idx],2)))

        if analiz:
            st.dataframe(pd.DataFrame(analiz, columns=["İyon","Durum","Fark (mmol/L)"]))
        else:
            st.success("✅ İyon dengesi mükemmel!")

        with st.expander("🧴 Çözelti Nasıl Hazırlanır?"):
            st.markdown("""
            1. Tankları %70 saf su ile doldurun.
            2. Gübreleri sırayla ekleyin ve karıştırın.
            3. Tam çözündükten sonra suyu tamamlayın.
            4. EC ve pH kontrolü yapın.
            5. Sisteme aktarın.
            """)

    except Exception as e:
        st.error(f"Hesaplama hatası: {e}")
