import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Gübre listesi (makro ve mikro besinler için)
gubreler = {
    "Potasyum Nitrat": {"formul": "KNO3", "besin": {"K": 0.378, "N": 0.135}, "agirlik": 101.10},
    "Potasyum Sülfat": {"formul": "K2SO4", "besin": {"K": 0.45, "S": 0.18}, "agirlik": 174.26},
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2·4H2O", "besin": {"Ca": 0.187, "N": 0.144}, "agirlik": 236.15},
    "Calmag": {"formul": "Calmag", "besin": {"Ca": 0.165, "Mg": 0.06}, "agirlik": 1.0},
    "Magnezyum Sülfat": {"formul": "MgSO4·7H2O", "besin": {"Mg": 0.096, "S": 0.132}, "agirlik": 246.51},
    "Magnezyum Nitrat": {"formul": "Mg(NO3)2·6H2O", "besin": {"Mg": 0.09, "N": 0.10}, "agirlik": 256.41},
    "Mono Potasyum Fosfat": {"formul": "KH2PO4", "besin": {"K": 0.282, "P": 0.225}, "agirlik": 136.09},
    "Mono Amonyum Fosfat": {"formul": "NH4H2PO4", "besin": {"P": 0.266, "N": 0.12, "NH4": 0.17}, "agirlik": 115.03},
    "Üre Fosfat": {"formul": "H3PO4·CO(NH2)2", "besin": {"P": 0.194, "N": 0.17}, "agirlik": 1.0},
    "Foliar Üre": {"formul": "CO(NH2)2", "besin": {"N": 0.46}, "agirlik": 60.06},
    "Kalsiyum Klorür": {"formul": "CaCl2", "besin": {"Ca": 0.38}, "agirlik": 110.98},
    "Potasyum Klorür": {"formul": "KCl", "besin": {"K": 0.524}, "agirlik": 74.55},
    "WS 0-0-60+48 Cl": {"formul": "KCl", "besin": {"K": 0.498}, "agirlik": 74.55},
    "NK 16-0-40": {"formul": "NK 16-0-40", "besin": {"K": 0.332, "N": 0.16}, "agirlik": 1.0},
    "Mangan Sülfat": {"formul": "MnSO4·H2O", "besin": {"Mn": 0.32}, "agirlik": 169.02},
    "Çinko Sülfat": {"formul": "ZnSO4·7H2O", "besin": {"Zn": 0.23}, "agirlik": 287.56},
    "Boraks": {"formul": "Na2B4O7·10H2O", "besin": {"B": 0.11}, "agirlik": 381.37},
    "Sodyum Molibdat": {"formul": "Na2MoO4·2H2O", "besin": {"Mo": 0.40}, "agirlik": 241.95},
    "Demir-EDDHA": {"formul": "Fe-EDDHA", "besin": {"Fe": 0.04}, "agirlik": 932.00},
    "Bakır Sülfat": {"formul": "CuSO4·5H2O", "besin": {"Cu": 0.075}, "agirlik": 250.00}
}

# Mikro besin elementleri (her reçeteye eklenecek)
mikro_besinler = {
    "Demir-EDDHA": {"Fe": 40, "mg_L": 37.280},
    "Boraks": {"B": 30, "mg_L": 2.858},
    "Mangan Sülfat": {"Mn": 5, "mg_L": 0.845},
    "Çinko Sülfat": {"Zn": 4, "mg_L": 1.152},
    "Bakır Sülfat": {"Cu": 0.75, "mg_L": 0.188},
    "Sodyum Molibdat": {"Mo": 0.5, "mg_L": 0.120}
}

# Reçeteler (dengeli hale getirildi)
receteler = {
    "çilek": {
        "vejetatif": {
            "NO3": 9.00,
            "H2PO4": 1.00,
            "SO4": 1.00,
            "NH4": 1.00,
            "K": 5.00,
            "Ca": 2.00,
            "Mg": 1.00,
            "EC": 1.6,
            "pH": 5.8
        },
        "meyve": {
            "NO3": 11.75,
            "H2PO4": 1.25,
            "SO4": 1.00,
            "NH4": 1.00,
            "K": 5.50,
            "Ca": 3.25,
            "Mg": 1.00,
            "EC": 2.1,
            "pH": 5.8
        }
    },
    "marul": {
        "üretim": {
            "NO3": 10.00,
            "H2PO4": 1.50,
            "SO4": 1.00,
            "NH4": 0.50,
            "K": 5.00,
            "Ca": 3.00,
            "Mg": 1.00,
            "EC": 1.8,
            "pH": 5.8
        }
    },
    "domates": {
        "çiçeklenme": {
            "NO3": 12.00,
            "H2PO4": 1.50,
            "SO4": 1.00,
            "NH4": 0.50,
            "K": 6.00,
            "Ca": 3.50,
            "Mg": 1.00,
            "EC": 2.3,
            "pH": 6.0
        },
        "meyve": {
            "NO3": 14.00,
            "H2PO4": 1.50,
            "SO4": 1.00,
            "NH4": 0.50,
            "K": 7.00,
            "Ca": 4.00,
            "Mg": 1.00,
            "EC": 2.5,
            "pH": 6.0
        }
    },
    "biber": {
        "meyve": {
            "NO3": 10.00,
            "H2PO4": 1.50,
            "SO4": 1.00,
            "NH4": 0.50,
            "K": 5.00,
            "Ca": 3.00,
            "Mg": 1.00,
            "EC": 2.0,
            "pH": 6.0
        }
    }
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
st.write("Aşağıdan tank hacimleri, konsantrasyon oranı, ürün ve gelişme dönemi seçin:")

# Kullanıcı girişleri
tank_a_hacim = st.number_input("A Tankı Hacmi (litre)", min_value=1.0, value=100.0)
tank_b_hacim = st.number_input("B Tankı Hacmi (litre)", min_value=1.0, value=100.0)
konsantrasyon = st.number_input("Stok Konsantrasyon Oranı (örneğin 100x)", min_value=1.0, value=100.0)
bitki = st.selectbox("Ürünü seçin:", list(receteler.keys()))
asama = st.selectbox("Gelişme dönemini seçin:", list(receteler[bitki].keys()))

# Reçeteyi göster
if st.button("Reçeteyi Göster"):
    recete = receteler[bitki][asama]

    # Anyon-Katyon dengesi hesaplama (mikro besinler dahil edilmez)
    anyon_me = recete["NO3"] + recete["H2PO4"] + (recete["SO4"] * 2)
    katyon_me = recete["NH4"] + recete["K"] + (recete["Ca"] * 2) + (recete["Mg"] * 2)
    anyon_mmol = recete["NO3"] + recete["H2PO4"] + recete["SO4"]
    katyon_mmol = recete["NH4"] + recete["K"] + recete["Ca"] + recete["Mg"]

    st.write("**Anyon-Katyon Dengesi (Makro Besinler):**")
    tablo_denge = {
        "Anyon": ["NO3", "H2PO4", "SO4", "", "Toplam"],
        "mmol/L (Anyon)": [recete["NO3"], recete["H2PO4"], recete["SO4"], "", anyon_mmol],
        "me/L (Anyon)": [recete["NO3"], recete["H2PO4"], recete["SO4"] * 2, "", anyon_me],
        "Katyon": ["NH4", "K", "Ca", "Mg", "Toplam"],
        "mmol/L (Katyon)": [recete["NH4"], recete["K"], recete["Ca"], recete["Mg"], katyon_mmol],
        "me/L (Katyon)": [recete["NH4"], recete["K"], recete["Ca"] * 2, recete["Mg"] * 2, katyon_me]
    }
    df_denge = pd.DataFrame(tablo_denge)
    st.table(df_denge)

    # Denge kontrolü
    if round(anyon_me, 2) != round(katyon_me, 2):
        st.error("Anyon ve katyon me/L eşit değil! Çözelti dengesiz.")
    else:
        # Makro besinler için gübre miktarları (mmol/L)
        gubre_miktarlari_mmol = {
            "Kalsiyum Nitrat": {"NO3": recete["Ca"] * 2, "Ca": recete["Ca"]},
            "Magnezyum Nitrat": {"Mg": recete["Mg"], "NO3": 1.90},
            "Mono Amonyum Fosfat": {"NH4": recete["NH4"], "H2PO4": 0.91},
            "Mono Potasyum Fosfat": {"H2PO4": 0.34, "K": 0.34},
            "Potasyum Nitrat": {"K": 2.75, "NO3": 2.73},
            "Potasyum Sülfat": {"K": recete["K"] - 0.34 - 2.75, "SO4": 1.25}
        }

        # Gram cinsinden hesaplama (1000 litre için) - Makro besinler
        gubre_miktarlari_gram = {}
        for gubre, besinler in gubre_miktarlari_mmol.items():
            gubre_bilgi = gubreler[gubre]
            if gubre == "Mono Amonyum Fosfat":
                miktar_mmol = recete["NH4"]
                miktar_gram = (miktar_mmol / (0.17 / 18)) * gubre_bilgi["agirlik"]
            elif gubre == "Mono Potasyum Fosfat":
                miktar_mmol = 0.34
                miktar_gram = (miktar_mmol / (0.225 / 31)) * gubre_bilgi["agirlik"]
            elif gubre == "Potasyum Sülfat":
                miktar_mmol = recete["K"] - 0.34 - 2.75
                miktar_gram = (miktar_mmol / (0.45 / 39)) * gubre_bilgi["agirlik"]
            elif gubre == "Potasyum Nitrat":
                miktar_mmol = 2.75
                miktar_gram = (miktar_mmol / (0.378 / 39)) * gubre_bilgi["agirlik"]
            elif gubre == "Magnezyum Nitrat":
                miktar_mmol = recete["Mg"]
                miktar_gram = (miktar_mmol / (0.09 / 24)) * gubre_bilgi["agirlik"]
            else:
                miktar_mmol = besinler["Ca"] if "Ca" in besinler else besinler["NO3"]
                miktar_gram = miktar_mmol * gubre_bilgi["agirlik"]
            gubre_miktarlari_gram[gubre] = miktar_gram

        # Mikro besinler için gram cinsinden hesaplama (1000 litre için)
        for gubre, besinler in mikro_besinler.items():
            gubre_miktarlari_gram[gubre] = besinler["mg_L"]

        # Tank stok çözeltileri (kg cinsinden)
        stok_a = {}
        stok_b = {}
        for gubre, miktar in gubre_miktarlari_gram.items():
            stok_miktar_kg = miktar / konsantrasyon
            if gubre in ["Kalsiyum Nitrat", "Magnezyum Nitrat", "Kalsiyum Hidroksit", "Calmag"]:
                stok_a[gubre] = stok_miktar_kg
            else:
                stok_b[gubre] = stok_miktar_kg

        # Gübre tablosu (makro ve mikro besinler)
        st.write("**Gübre Miktarları:**")
        tablo_gubre = {
            "Kimyasal Bileşik": ["Kalsiyum Nitrat", "Magnezyum Nitrat", "Mono Amonyum Fosfat", "Mono Potasyum Fosfat", "Potasyum Nitrat", "Potasyum Sülfat", "Demir-EDDHA", "Boraks", "Mangan Sülfat", "Çinko Sülfat", "Bakır Sülfat", "Sodyum Molibdat", "TOPLAM"],
            "mmol/L": [recete["Ca"], recete["Mg"], recete["NH4"], 0.34, 2.75, recete["K"] - 0.34 - 2.75, "", "", "", "", "", "", ""],
            "NO3": [recete["Ca"] * 2, 1.90, "-", "-", 2.73, "-", "-", "-", "-", "-", "-", "-", recete["NO3"]],
            "H2PO4": ["-", "-", 0.91, 0.34, "-", "-", "-", "-", "-", "-", "-", "-", recete["H2PO4"]],
            "SO4": ["-", "-", "-", "-", "-", 1.25, "-", "-", "-", "-", "-", "-", recete["SO4"] + 0.25],
            "NH4": ["-", "-", recete["NH4"], "-", "-", "-", "-", "-", "-", "-", "-", "-", recete["NH4"]],
            "K": ["-", "-", "-", 0.34, 2.75, recete["K"] - 0.34 - 2.75, "-", "-", "-", "-", "-", "-", recete["K"]],
            "Ca": [recete["Ca"], "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", recete["Ca"]],
            "Mg": ["-", recete["Mg"], "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", recete["Mg"]],
            "Fe (µmol/L)": ["-", "-", "-", "-", "-", "-", 40, "-", "-", "-", "-", "-", ""],
            "B (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", 30, "-", "-", "-", "-", ""],
            "Mn (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", "-", 5, "-", "-", "-", ""],
            "Zn (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", "-", "-", 4, "-", "-", ""],
            "Cu (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", 0.75, "-", ""],
            "Mo (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", 0.5, ""],
            "Gram (1000 L)": [
                f"{gubre_miktarlari_gram['Kalsiyum Nitrat']:.2f}",
                f"{gubre_miktarlari_gram['Magnezyum Nitrat']:.2f}",
                f"{gubre_miktarlari_gram['Mono Amonyum Fosfat']:.2f}",
                f"{gubre_miktarlari_gram['Mono Potasyum Fosfat']:.2f}",
                f"{gubre_miktarlari_gram['Potasyum Nitrat']:.2f}",
                f"{gubre_miktarlari_gram['Potasyum Sülfat']:.2f}",
                f"{gubre_miktarlari_gram['Demir-EDDHA']:.2f}",
                f"{gubre_miktarlari_gram['Boraks']:.2f}",
                f"{gubre_miktarlari_gram['Mangan Sülfat']:.2f}",
                f"{gubre_miktarlari_gram['Çinko Sülfat']:.2f}",
                f"{gubre_miktarlari_gram['Bakır Sülfat']:.2f}",
                f"{gubre_miktarlari_gram['Sodyum Molibdat']:.2f}",
                ""
            ]
        }
        df_gubre = pd.DataFrame(tablo_gubre)
        st.table(df_gubre)

        # Stok çözeltileri (daha hassas görüntüleme için .4f)
        st.write("**A Tankı Stok Çözelti (kg):**")
        for gubre, miktar in stok_a.items():
            st.write(f"{gubre}: {miktar:.4f} kg")
        st.write("**B Tankı Stok Çözelti (kg):**")
        for gubre, miktar in stok_b.items():
            st.write(f"{gubre}: {miktar:.4f} kg")

        # PDF oluştur
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, f"{bitki.capitalize()} ({asama}) Reçetesi")
        y = 700
        c.drawString(100, y, "Anyon-Katyon Dengesi (Makro Besinler)")
        y -= 20
        for i, row in df_denge.iterrows():
            c.drawString(100, y, f"{row['Anyon']}: {row['mmol/L (Anyon)']} mmol/L, {row['me/L (Anyon)']} me/L | {row['Katyon']}: {row['mmol/L (Katyon)']} mmol/L, {row['me/L (Katyon)']} me/L")
            y -= 20
        y -= 20
        c.drawString(100, y, "Gübre Miktarları")
        y -= 20
        for i, row in df_gubre.iterrows():
            c.drawString(100, y, f"{row['Kimyasal Bileşik']}: {row['mmol/L']} mmol/L, NO3: {row['NO3']}, H2PO4: {row['H2PO4']}, SO4: {row['SO4']}, NH4: {row['NH4']}, K: {row['K']}, Ca: {row['Ca']}, Mg: {row['Mg']}, Fe: {row['Fe (µmol/L)']}, B: {row['B (µmol/L)']}, Mn: {row['Mn (µmol/L)']}, Zn: {row['Zn (µmol/L)']}, Cu: {row['Cu (µmol/L)']}, Mo: {row['Mo (µmol/L)']}, Gram: {row['Gram (1000 L)']}")
            y -= 20
        y -= 20
        c.drawString(100, y, f"A Tankı ({tank_a_hacim} L):")
        y -= 20
        for gubre, miktar in stok_a.items():
            c.drawString(100, y, f"{gubre}: {miktar:.4f} kg")
            y -= 20
        y -= 20
        c.drawString(100, y, f"B Tankı ({tank_b_hacim} L):")
        y -= 20
        for gubre, miktar in stok_b.items():
            c.drawString(100, y, f"{gubre}: {miktar:.4f} kg")
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
