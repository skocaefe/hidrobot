import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import json
import os

# Gübre veritabanını JSON dosyasından yükle
if not os.path.exists("gubreler.json"):
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
    with open("gubreler.json", "w") as f:
        json.dump(gubreler, f)
with open("gubreler.json", "r") as f:
    gubreler = json.load(f)

# Mikro besin elementleri için referans değerler (µmol/L cinsinden)
mikro_besinler = {
    "Demir-EDDHA": {"besin": "Fe", "ref_umol_L": 40, "mg_L": 37.280},
    "Boraks": {"besin": "B", "ref_umol_L": 30, "mg_L": 2.858},
    "Mangan Sülfat": {"besin": "Mn", "ref_umol_L": 5, "mg_L": 0.845},
    "Çinko Sülfat": {"besin": "Zn", "ref_umol_L": 4, "mg_L": 1.152},
    "Bakır Sülfat": {"besin": "Cu", "ref_umol_L": 0.75, "mg_L": 0.188},
    "Sodyum Molibdat": {"besin": "Mo", "ref_umol_L": 0.5, "mg_L": 0.120}
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
st.title("Hidroponik Besin Çözeltisi Hesaplama (HydroBuddy Tabanlı)")
st.write("Aşağıdan hedef besin konsantrasyonlarınızı (mmol/L cinsinden) girin:")

# Kullanıcıdan hedef konsantrasyonları al
st.subheader("Makro Besinler (mmol/L)")
NO3 = st.number_input("NO3 (Nitrat Azotu)", min_value=0.0, value=0.0, step=0.01)
H2PO4 = st.number_input("H2PO4 (Fosfat)", min_value=0.0, value=0.0, step=0.01)
SO4 = st.number_input("SO4 (Sülfat)", min_value=0.0, value=0.0, step=0.01)
NH4 = st.number_input("NH4 (Amonyum Azotu)", min_value=0.0, value=0.0, step=0.01)
K = st.number_input("K (Potasyum)", min_value=0.0, value=0.0, step=0.01)
Ca = st.number_input("Ca (Kalsiyum)", min_value=0.0, value=0.0, step=0.01)
Mg = st.number_input("Mg (Magnezyum)", min_value=0.0, value=0.0, step=0.01)

st.subheader("Mikro Besinler (µmol/L)")
Fe = st.number_input("Fe (Demir)", min_value=0.0, value=40.0, step=0.01)
B = st.number_input("B (Bor)", min_value=0.0, value=30.0, step=0.01)
Mn = st.number_input("Mn (Manganez)", min_value=0.0, value=5.0, step=0.01)
Zn = st.number_input("Zn (Çinko)", min_value=0.0, value=4.0, step=0.01)
Cu = st.number_input("Cu (Bakır)", min_value=0.0, value=0.75, step=0.01)
Mo = st.number_input("Mo (Molibden)", min_value=0.0, value=0.5, step=0.01)

# Kullanıcıdan tank hacimleri ve konsantrasyon oranı
st.subheader("Tank ve Konsantrasyon Bilgileri")
tank_a_hacim = st.number_input("A Tankı Hacmi (litre)", min_value=1.0, value=100.0)
tank_b_hacim = st.number_input("B Tankı Hacmi (litre)", min_value=1.0, value=100.0)
konsantrasyon = st.number_input("Stok Konsantrasyon Oranı (örneğin 100x)", min_value=1.0, value=100.0)

# Kullanıcı reçetesini oluştur
recete = {
    "NO3": NO3,
    "H2PO4": H2PO4,
    "SO4": SO4,
    "NH4": NH4,
    "K": K,
    "Ca": Ca,
    "Mg": Mg,
    "Fe": Fe,
    "B": B,
    "Mn": Mn,
    "Zn": Zn,
    "Cu": Cu,
    "Mo": Mo
}

# Reçeteyi hesapla
if st.button("Reçeteyi Hesapla"):
    # Anyon-Katyon dengesi hesaplama
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

    # EC ve pH hesaplama
    ec = (recete["NO3"] * 0.075) + (recete["H2PO4"] * 0.090) + (recete["SO4"] * 0.120) + \
         (recete["NH4"] * 0.073) + (recete["K"] * 0.074) + (recete["Ca"] * 0.120) + (recete["Mg"] * 0.106)
    ph = 7.0 - (recete["H2PO4"] * 0.2 + recete["NH4"] * 0.1) + (recete["Ca"] * 0.05 + recete["Mg"] * 0.03)

    st.write("**Çözeltinin Tahmini EC ve pH Değerleri:**")
    st.write(f"- **EC**: {ec:.2f} mS/cm")
    st.write(f"- **pH**: {ph:.2f}")

    # Denge kontrolü
    if round(anyon_me, 2) != round(katyon_me, 2):
        st.error("Anyon ve katyon me/L eşit değil! Çözelti dengesiz.")
    else:
        # Makro besinler için gübre miktarları (mmol/L)
        gubre_miktarlari_mmol = {
            "Kalsiyum Nitrat": {"NO3": 0.0, "Ca": 0.0},
            "Magnezyum Nitrat": {"Mg": 0.0, "NO3": 0.0},
            "Mono Amonyum Fosfat": {"NH4": 0.0, "H2PO4": 0.0},
            "Mono Potasyum Fosfat": {"H2PO4": 0.0, "K": 0.0},
            "Potasyum Nitrat": {"K": 0.0, "NO3": 0.0},
            "Potasyum Sülfat": {"K": 0.0, "SO4": 0.0}
        }

        # Adım adım hesaplama (HydroBuddy mantığı)
        # 1. Kalsiyum Nitrat ile Ca ve NO₃
        if recete["Ca"] > 0:
            gubre_miktarlari_mmol["Kalsiyum Nitrat"]["Ca"] = recete["Ca"]
            gubre_miktarlari_mmol["Kalsiyum Nitrat"]["NO3"] = recete["Ca"] * (0.144 / 0.187) * (62 / 14)

        # 2. Magnezyum Nitrat ile Mg ve NO₃
        if recete["Mg"] > 0:
            gubre_miktarlari_mmol["Magnezyum Nitrat"]["Mg"] = recete["Mg"]
            gubre_miktarlari_mmol["Magnezyum Nitrat"]["NO3"] = recete["Mg"] * (0.10 / 0.09) * (62 / 14)

        # 3. MAP ile NH₄ ve H₂PO₄
        if recete["NH4"] > 0:
            gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["NH4"] = recete["NH4"]
            gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["H2PO4"] = recete["NH4"] * (0.266 / 0.17) * (31 / 18)

        # 4. MKP ile H₂PO₄ ve K
        remaining_H2PO4 = recete["H2PO4"] - gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["H2PO4"]
        if remaining_H2PO4 > 0:
            gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["H2PO4"] = remaining_H2PO4
            gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["K"] = remaining_H2PO4 * (0.282 / 0.225)

        # 5. Potasyum Nitrat ile NO₃ ve K
        remaining_NO3 = recete["NO3"] - (gubre_miktarlari_mmol["Kalsiyum Nitrat"]["NO3"] + gubre_miktarlari_mmol["Magnezyum Nitrat"]["NO3"])
        if remaining_NO3 > 0:
            gubre_miktarlari_mmol["Potasyum Nitrat"]["NO3"] = remaining_NO3
            gubre_miktarlari_mmol["Potasyum Nitrat"]["K"] = remaining_NO3 * (0.378 / 0.135) * (14 / 62)

        # 6. Potasyum Sülfat ile K ve SO₄
        remaining_K = recete["K"] - (gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["K"] + gubre_miktarlari_mmol["Potasyum Nitrat"]["K"])
        if remaining_K > 0:
            gubre_miktarlari_mmol["Potasyum Sülfat"]["K"] = remaining_K
            gubre_miktarlari_mmol["Potasyum Sülfat"]["SO4"] = remaining_K * (0.18 / 0.45)

        # Gram cinsinden hesaplama (1000 litre için) - Makro besinler
        gubre_miktarlari_gram = {}
        for gubre, besinler in gubre_miktarlari_mmol.items():
            gubre_bilgi = gubreler[gubre]
            if gubre == "Mono Amonyum Fosfat":
                miktar_mmol = besinler["NH4"]
                miktar_gram = (miktar_mmol / (0.17 / 18)) * gubre_bilgi["agirlik"]
            elif gubre == "Mono Potasyum Fosfat":
                miktar_mmol = besinler["H2PO4"]
                miktar_gram = (miktar_mmol / (0.225 / 31)) * gubre_bilgi["agirlik"]
            elif gubre == "Potasyum Sülfat":
                miktar_mmol = besinler["K"]
                miktar_gram = (miktar_mmol / (0.45 / 39)) * gubre_bilgi["agirlik"]
            elif gubre == "Potasyum Nitrat":
                miktar_mmol = besinler["NO3"]
                miktar_gram = (miktar_mmol / (0.135 / 14 * 62 / 62)) * gubre_bilgi["agirlik"]
            elif gubre == "Magnezyum Nitrat":
                miktar_mmol = besinler["Mg"]
                miktar_gram = (miktar_mmol / (0.09 / 24)) * gubre_bilgi["agirlik"]
            elif gubre == "Kalsiyum Nitrat":
                miktar_mmol = besinler["Ca"]
                miktar_gram = (miktar_mmol / (0.187 / 40)) * gubre_bilgi["agirlik"]
            else:
                miktar_mmol = besinler["Ca"] if "Ca" in besinler else besinler["NO3"]
                miktar_gram = miktar_mmol * gubre_bilgi["agirlik"]
            gubre_miktarlari_gram[gubre] = miktar_gram

        # Mikro besinler için gram cinsinden hesaplama (1000 litre için)
        for gubre, info in mikro_besinler.items():
            besin = info["besin"]
            ref_umol_L = info["ref_umol_L"]
            ref_mg_L = info["mg_L"]
            if besin in recete and recete[besin] > 0:
                gubre_miktarlari_gram[gubre] = (recete[besin] / ref_umol_L) * ref_mg_L
            else:
                gubre_miktarlari_gram[gubre] = 0.0

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
            "mmol/L": [
                gubre_miktarlari_mmol["Kalsiyum Nitrat"]["Ca"],
                gubre_miktarlari_mmol["Magnezyum Nitrat"]["Mg"],
                gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["NH4"],
                gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["H2PO4"],
                gubre_miktarlari_mmol["Potasyum Nitrat"]["K"],
                gubre_miktarlari_mmol["Potasyum Sülfat"]["K"],
                "", "", "", "", "", "", ""
            ],
            "NO3": [
                gubre_miktarlari_mmol["Kalsiyum Nitrat"]["NO3"],
                gubre_miktarlari_mmol["Magnezyum Nitrat"]["NO3"],
                "-", "-", gubre_miktarlari_mmol["Potasyum Nitrat"]["NO3"], "-",
                "-", "-", "-", "-", "-", "-",
                recete["NO3"]
            ],
            "H2PO4": [
                "-", "-",
                gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["H2PO4"],
                gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["H2PO4"],
                "-", "-",
                "-", "-", "-", "-", "-", "-",
                recete["H2PO4"]
            ],
            "SO4": [
                "-", "-", "-", "-",
                "-", gubre_miktarlari_mmol["Potasyum Sülfat"]["SO4"],
                "-", "-", "-", "-", "-", "-",
                recete["SO4"]
            ],
            "NH4": [
                "-", "-", gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["NH4"],
                "-", "-", "-",
                "-", "-", "-", "-", "-", "-",
                recete["NH4"]
            ],
            "K": [
                "-", "-", "-",
                gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["K"],
                gubre_miktarlari_mmol["Potasyum Nitrat"]["K"],
                gubre_miktarlari_mmol["Potasyum Sülfat"]["K"],
                "-", "-", "-", "-", "-", "-",
                recete["K"]
            ],
            "Ca": [
                gubre_miktarlari_mmol["Kalsiyum Nitrat"]["Ca"],
                "-", "-", "-", "-", "-",
                "-", "-", "-", "-", "-", "-",
                recete["Ca"]
            ],
            "Mg": [
                "-", gubre_miktarlari_mmol["Magnezyum Nitrat"]["Mg"],
                "-", "-", "-", "-",
                "-", "-", "-", "-", "-", "-",
                recete["Mg"]
            ],
            "Fe (µmol/L)": ["-", "-", "-", "-", "-", "-", recete["Fe"], "-", "-", "-", "-", "-", ""],
            "B (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", recete["B"], "-", "-", "-", "-", ""],
            "Mn (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", "-", recete["Mn"], "-", "-", "-", ""],
            "Zn (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", "-", "-", recete["Zn"], "-", "-", ""],
            "Cu (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", recete["Cu"], "-", ""],
            "Mo (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", recete["Mo"], ""],
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
        c.drawString(100, 750, "Kullanıcı Tanımlı Reçete")
        y = 700
        c.drawString(100, y, f"Tahmini EC: {ec:.2f} mS/cm, Tahmini pH: {ph:.2f}")
        y -= 20
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
            file_name="kullanici_tanimli_recipe.pdf",
            mime="application/pdf",
            key="download_button"
        )
