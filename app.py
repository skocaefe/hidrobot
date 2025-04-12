import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Gübre listesi
gubreler = {
    "Nitrik Asit": {"formul": "HNO3", "besin": {"N": 0.22}, "agirlik": 63.01},
    "Fosforik Asit": {"formul": "H3PO4", "besin": {"P": 0.32}, "agirlik": 97.99},
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2·4H2O", "besin": {"Ca": 0.169, "N": 0.119}, "agirlik": 236.15},
    "Potasyum Nitrat": {"formul": "KNO3", "besin": {"K": 0.38, "N": 0.13}, "agirlik": 101.10},
    "Amonyum Sülfat": {"formul": "(NH4)2SO4", "besin": {"N": 0.212}, "agirlik": 132.14},
    "Amonyum Nitrat": {"formul": "NH4NO3", "besin": {"N": 0.35, "NH4": 0.35}, "agirlik": 80.04},
    "Magnezyum Nitrat": {"formul": "Mg(NO3)2·6H2O", "besin": {"Mg": 0.09, "N": 0.11}, "agirlik": 256.41},
    "Mono Potasyum Fosfat": {"formul": "KH2PO4", "besin": {"K": 0.28, "P": 0.23}, "agirlik": 136.09},
    "Mono Amonyum Fosfat": {"formul": "NH4H2PO4", "besin": {"P": 0.27, "N": 0.12}, "agirlik": 115.03},
    "Potasyum Sülfat": {"formul": "K2SO4", "besin": {"K": 0.45, "S": 0.18}, "agirlik": 174.26},
    "Magnezyum Sülfat": {"formul": "MgSO4·7H2O", "besin": {"Mg": 0.10, "S": 0.13}, "agirlik": 246.51},
    "Mangan Sülfat": {"formul": "MnSO4·H2O", "besin": {"Mn": 0.32}, "agirlik": 169.02},
    "Çinko Sülfat": {"formul": "ZnSO4·7H2O", "besin": {"Zn": 0.23}, "agirlik": 287.56},
    "Boraks": {"formul": "Na2B4O7·10H2O", "besin": {"B": 0.11}, "agirlik": 381.37},
    "Sodyum Molibdat": {"formul": "Na2MoO4·2H2O", "besin": {"Mo": 0.40}, "agirlik": 241.95},
    "Demir-EDTA %13": {"formul": "Fe-EDTA %13", "besin": {"Fe": 0.13}, "agirlik": 367},
    "Demir-DTPA %6": {"formul": "Fe-DTPA %6", "besin": {"Fe": 0.06}, "agirlik": 468},
    "Demir-EDDHA %5": {"formul": "Fe-EDDHA %5", "besin": {"Fe": 0.05}, "agirlik": 435},
    "Potasyum Bikarbonat": {"formul": "KHCO3", "besin": {"K": 0.39}, "agirlik": 100.12},
    "Kalsiyum Hidroksit": {"formul": "Ca(OH)2", "besin": {"Ca": 0.54}, "agirlik": 74.09}
}

# Reçete (anyon-katyon dengesi)
recete = {
    "NO3": 11.75,
    "H2PO4": 1.25,
    "SO4": 1.00,
    "NH4": 1.00,
    "K": 5.50,
    "Ca": 3.25,
    "Mg": 1.00,
    "EC": 1.6,
    "pH": 5.8
}

# Stil ekleme
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    h1 {
        color: #2e7d32;
        text-align: center;
    }
    .stButton>button {
        background-color: #4caf50;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Ana sayfa
st.title("Hidroponik Besin Çözeltisi Chatbot")
st.write("Aşağıdan tank hacimleri ve konsantrasyon oranını girin:")

# Kullanıcı girişleri
tank_a_hacim = st.number_input("A Tankı Hacmi (litre)", min_value=1.0, value=100.0)
tank_b_hacim = st.number_input("B Tankı Hacmi (litre)", min_value=1.0, value=100.0)
konsantrasyon = st.number_input("Stok Konsantrasyon Oranı (örneğin 100x)", min_value=1.0, value=100.0)

# Anyon-Katyon tablosu
st.write("**Anyon-Katyon Dengesi:**")
tablo_denge = {
    "Anyon": ["NO3", "H2PO4", "SO4", "", "Toplam"],
    "mmol/L (Anyon)": [11.75, 1.25, 1.00, "", 14.00],
    "me/L (Anyon)": [11.75, 1.25, 2.00, "", 15.00],
    "Katyon": ["NH4", "K", "Ca", "Mg", "Toplam"],
    "mmol/L (Katyon)": [1.00, 5.50, 3.25, 1.00, 10.75],
    "me/L (Katyon)": [1.00, 5.50, 6.50, 2.00, 15.00]
}
df_denge = pd.DataFrame(tablo_denge)
st.table(df_denge)

# Gübre hesaplama
if st.button("Reçeteyi Göster"):
    # Gübre miktarları (mmol/L)
    gubre_miktarlari_mmol = {
        "KH2PO4": {"H2PO4": 1.25, "K": 1.25},
        "Ca(NO3)2·4H2O": {"NO3": 6.50, "Ca": 3.25},
        "NH4NO3": {"NH4": 1.00, "NO3": 1.00},
        "KNO3": {"K": 4.25, "NO3": 4.25},
        "MgSO4·7H2O": {"Mg": 1.00, "SO4": 1.00}
    }

    # Gram cinsinden hesaplama (1000 litre için)
    gubre_miktarlari_gram = {}
    for gubre, besinler in gubre_miktarlari_mmol.items():
        gubre_bilgi = gubreler[gubre]
        # İlk besini al (örneğin KH2PO4 için H2PO4)
        besin = list(besinler.keys())[0]
        miktar_mmol = besinler[besin]
        miktar_gram = miktar_mmol * gubre_bilgi["agirlik"]
        gubre_miktarlari_gram[gubre] = miktar_gram

    # Tank stok çözeltileri
    stok_a = {}
    stok_b = {}
    for gubre, miktar in gubre_miktarlari_gram.items():
        if gubre in ["Kalsiyum Nitrat", "Magnezyum Nitrat", "Kalsiyum Hidroksit"]:
            stok_a[gubre] = miktar / konsantrasyon / 1000  # kg
        else:
            stok_b[gubre] = miktar / konsantrasyon / 1000  # kg

    # Gübre tablosu
    st.write("**Gübre Miktarları:**")
    tablo_gubre = {
        "Kimyasal Bileşik": ["KH2PO4", "Ca(NO3)2·4H2O", "NH4NO3", "KNO3", "MgSO4·7H2O", "TOPLAM"],
        "mmol/L": [1.25, 3.25, 1.00, 4.25, 1.00, ""],
        "NO3": ["-", 6.50, 1.00, 4.25, "-", 11.75],
        "H2PO4": [1.25, "-", "-", "-", "-", 1.25],
        "SO4": ["-", "-", "-", "-", 1.00, 1.00],
        "NH4": ["-", "-", 1.00, "-", "-", 1.00],
        "K": [1.25, "-", "-", 4.25, "-", 5.50],
        "Ca": ["-", 3.25, "-", "-", "-", 3.25],
        "Mg": ["-", "-", "-", "-", 1.00, 1.00],
        "Gram (1000 L)": [f"{gubre_miktarlari_gram['KH2PO4']:.2f}", f"{gubre_miktarlari_gram['Ca(NO3)2·4H2O']:.2f}", f"{gubre_miktarlari_gram['NH4NO3']:.2f}", f"{gubre_miktarlari_gram['KNO3']:.2f}", f"{gubre_miktarlari_gram['MgSO4·7H2O']:.2f}", ""]
    }
    df_gubre = pd.DataFrame(tablo_gubre)
    st.table(df_gubre)

    # Stok çözeltileri
    st.write("**A Tankı Stok Çözelti (kg):**")
    for gubre, miktar in stok_a.items():
        st.write(f"{gubre}: {miktar:.2f} kg")
    st.write("**B Tankı Stok Çözelti (kg):**")
    for gubre, miktar in stok_b.items():
        st.write(f"{gubre}: {miktar:.2f} kg")

    # PDF oluştur
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "Anyon-Katyon Dengesi")
    y = 700
    for i, row in df_denge.iterrows():
        c.drawString(100, y, f"{row['Anyon']}: {row['mmol/L (Anyon)']} mmol/L, {row['me/L (Anyon)']} me/L | {row['Katyon']}: {row['mmol/L (Katyon)']} mmol/L, {row['me/L (Katyon)']} me/L")
        y -= 20
    y -= 20
    c.drawString(100, y, "Gübre Miktarları")
    y -= 20
    for i, row in df_gubre.iterrows():
        c.drawString(100, y, f"{row['Kimyasal Bileşik']}: {row['mmol/L']} mmol/L, NO3: {row['NO3']}, H2PO4: {row['H2PO4']}, SO4: {row['SO4']}, NH4: {row['NH4']}, K: {row['K']}, Ca: {row['Ca']}, Mg: {row['Mg']}, Gram: {row['Gram (1000 L)']}")
        y -= 20
    y -= 20
    c.drawString(100, y, f"A Tankı ({tank_a_hacim} L):")
    y -= 20
    for gubre, miktar in stok_a.items():
        c.drawString(100, y, f"{gubre}: {miktar:.2f} kg")
        y -= 20
    y -= 20
    c.drawString(100, y, f"B Tankı ({tank_b_hacim} L):")
    y -= 20
    for gubre, miktar in stok_b.items():
        c.drawString(100, y, f"{gubre}: {miktar:.2f} kg")
        y -= 20
    y -= 20
    c.drawString(100, y, f"Konsantrasyon: {konsantrasyon}x")
    c.showPage()
    c.save()
    buffer.seek(0)
    st.download_button(
        label="Reçeteyi PDF Olarak İndir",
        data=buffer,
        file_name="besin_cozeltisi_recipe.pdf",
        mime="application/pdf",
        key="download_button"
    )
