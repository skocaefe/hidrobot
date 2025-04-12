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
    "Amonyum Nitrat": {"formul": "NH4NO3", "besin": {"N": 0.35}, "agirlik": 80.04},
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

# Besin-gübre eşleştirmesi
besin_gubreleri = {
    "Azot": ["Kalsiyum Nitrat", "Potasyum Nitrat", "Amonyum Sülfat", "Amonyum Nitrat", "Magnezyum Nitrat", "Mono Amonyum Fosfat", "Nitrik Asit"],
    "Fosfor": ["Fosforik Asit", "Mono Potasyum Fosfat", "Mono Amonyum Fosfat"],
    "Potasyum": ["Potasyum Nitrat", "Mono Potasyum Fosfat", "Potasyum Sülfat", "Potasyum Bikarbonat"],
    "Kalsiyum": ["Kalsiyum Nitrat", "Kalsiyum Hidroksit"],
    "Magnezyum": ["Magnezyum Nitrat", "Magnezyum Sülfat"]
}

# Reçeteler
cilek_vejetatif = {
    "Azot": 9,
    "Fosfor": 1,
    "Potasyum": 5.5,
    "Kalsiyum": 2.5,
    "Magnezyum": 1,
    "EC": 1.6,
    "pH": 5.8
}
cilek_meyve = {
    "Azot": 9,
    "Fosfor": 1.5,
    "Potasyum": 7.5,
    "Kalsiyum": 3.5,
    "Magnezyum": 2,
    "EC": 2.1,
    "pH": 5.8
}
marul_uretim = {
    "Azot": 150,
    "Fosfor": 40,
    "Potasyum": 200,
    "Kalsiyum": 120,
    "Magnezyum": 40,
    "EC": 1.8,
    "pH": 5.8
}
domates_ciceklenme = {
    "Azot": 170,
    "Fosfor": 50,
    "Potasyum": 250,
    "Kalsiyum": 140,
    "Magnezyum": 40,
    "EC": 2.3,
    "pH": 6.0
}
domates_meyve = {
    "Azot": 190,
    "Fosfor": 50,
    "Potasyum": 300,
    "Kalsiyum": 150,
    "Magnezyum": 50,
    "EC": 2.5,
    "pH": 6.0
}
biber_meyve = {
    "Azot": 150,
    "Fosfor": 50,
    "Potasyum": 200,
    "Kalsiyum": 120,
    "Magnezyum": 40,
    "EC": 2.0,
    "pH": 6.0
}
besin_veritabani = {
    "çilek": {"vejetatif": cilek_vejetatif, "meyve": cilek_meyve},
    "marul": {"üretim": marul_uretim},
    "domates": {"çiçeklenme": domates_ciceklenme, "meyve": domates_meyve},
    "biber": {"meyve": biber_meyve}
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
st.write("Aşağıdan bitki, aşama, tank hacimleri ve konsantrasyon oranını girin:")

# Kullanıcı girişleri
bitki = st.selectbox("Bitkiyi seçin:", list(besin_veritabani.keys()))
asama = st.selectbox("Büyüme aşamasını seçin:", list(besin_veritabani[bitki].keys()))
tank_a_hacim = st.number_input("A Tankı Hacmi (litre)", min_value=1.0, value=100.0)
tank_b_hacim = st.number_input("B Tankı Hacmi (litre)", min_value=1.0, value=100.0)
konsantrasyon = st.number_input("Stok Konsantrasyon Oranı (örneğin 100x)", min_value=1.0, value=100.0)

# Reçete tablosu ve gübre seçimi
st.write(f"**{bitki.capitalize()} ({asama}) reçetesi:**")
recete = besin_veritabani[bitki][asama]
birim = "mmol/L" if bitki == "çilek" else "ppm"
tablo_veri = {
    "Besin": ["Azot", "Fosfor", "Potasyum", "Kalsiyum", "Magnezyum", "EC", "pH"],
    "Değer": [
        f"{recete['Azot']} {birim}",
        f"{recete['Fosfor']} {birim}",
        f"{recete['Potasyum']} {birim}",
        f"{recete['Kalsiyum']} {birim}",
        f"{recete['Magnezyum']} {birim}",
        f"{recete['EC']} mS/cm",
        f"{recete['pH']}"
    ],
    "Gübre": [""] * 7
}
gubre_secimleri = {}
for besin in ["Azot", "Fosfor", "Potasyum", "Kalsiyum", "Magnezyum"]:
    if besin == "Kalsiyum":
        gubre_secimleri[besin] = st.selectbox(f"{besin} için gübre:", ["Kalsiyum Nitrat"], key=f"gubre_{besin}")
    else:
        gubre_secimleri[besin] = st.selectbox(f"{besin} için gübre:", besin_gubreleri[besin], key=f"gubre_{besin}")
    if gubre_secimleri[besin]:
        tablo_veri["Gübre"][list(tablo_veri["Besin"]).index(besin)] = gubre_secimleri[besin]

df = pd.DataFrame(tablo_veri)
st.table(df)

# Reçeteyi hesapla
if st.button("Reçeteyi Göster"):
    gubre_miktarlari = {}
    kalan_besinler = recete.copy()

    # Kalsiyum Nitrat ile Kalsiyum ve Azot hesaplama
    kalsiyum_gubre = gubre_secimleri["Kalsiyum"]
    if kalsiyum_gubre == "Kalsiyum Nitrat":
        gubre_bilgi = gubreler[kalsiyum_gubre]
        ca_miktar = kalan_besinler["Kalsiyum"]
        ca_miktar_g = ca_miktar * gubre_bilgi["agirlik"] / gubre_bilgi["besin"]["Ca"] / 1000
        n_miktar = ca_miktar * gubre_bilgi["besin"]["N"] / gubre_bilgi["besin"]["Ca"]
        gubre_miktarlari[kalsiyum_gubre] = ca_miktar_g * 1000  # g/1000 L
        kalan_besinler["Kalsiyum"] = 0
        kalan_besinler["Azot"] -= n_miktar

    # Diğer besinler için hesaplama
    for besin, gubre in gubre_secimleri.items():
        if besin != "Kalsiyum" and gubre and kalan_besinler[besin] > 0:
            gubre_bilgi = gubreler[gubre]
            if besin in gubre_bilgi["besin"]:
                besin_miktar = kalan_besinler[besin]
                if birim == "mmol/L":
                    miktar = besin_miktar * gubre_bilgi["agirlik"] / gubre_bilgi["besin"][besin] / 1000
                else:
                    miktar = besin_miktar / gubre_bilgi["besin"][besin] / 1000
                gubre_miktarlari[gubre] = miktar * 1000  # g/1000 L
                kalan_besinler[besin] = 0

    # Tank stok çözeltileri
    stok_a = {}
    stok_b = {}
    for gubre, miktar in gubre_miktarlari.items():
        if gubre in ["Kalsiyum Nitrat", "Magnezyum Nitrat", "Kalsiyum Hidroksit"]:
            stok_a[gubre] = miktar / konsantrasyon / 1000  # kg
        else:
            stok_b[gubre] = miktar / konsantrasyon / 1000  # kg

    # Gübre miktarları
    st.write("**Gübre Miktarları (g/1000 L):**")
    for gubre, miktar in gubre_miktarlari.items():
        st.write(f"{gubre}: {miktar:.2f} g")

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
    c.drawString(100, 750, f"{bitki.capitalize()} ({asama}) Reçetesi")
    y = 700
    for besin, deger, gubre in zip(tablo_veri["Besin"], tablo_veri["Değer"], tablo_veri["Gübre"]):
        c.drawString(100, y, f"{besin}: {deger} ({gubre})")
        y -= 20
    y -= 20
    c.drawString(100, y, "Gübre Miktarları (g/1000 L):")
    y -= 20
    for gubre, miktar in gubre_miktarlari.items():
        c.drawString(100, y, f"{gubre}: {miktar:.2f} g")
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
        file_name=f"{bitki}_{asama}_recipe.pdf",
        mime="application/pdf",
        key="download_button"
    )
