import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import json
import os
import math

# Gübre veritabanını JSON dosyasından yükle
if not os.path.exists("gubreler.json"):
    gubreler = {
        "Potasyum Nitrat": {"formul": "KNO3", "besin": {"K": 0.378, "NO3": 0.135}, "agirlik": 101.10},
        "Potasyum Sülfat": {"formul": "K2SO4", "besin": {"K": 0.45, "SO4": 0.18}, "agirlik": 174.26},
        "Kalsiyum Nitrat": {"formul": "Ca(NO3)2·4H2O", "besin": {"Ca": 0.187, "NO3": 0.144}, "agirlik": 236.15},
        "Kalsiyum Amonyum Nitrat": {"formul": "CAN", "besin": {"Ca": 0.19, "NO3": 0.573, "NH4": 0.722}, "agirlik": 164.00},
        "Calmag": {"formul": "Calmag", "besin": {"Ca": 0.165, "Mg": 0.06}, "agirlik": 1.0},
        "Magnezyum Sülfat": {"formul": "MgSO4·7H2O", "besin": {"Mg": 0.096, "SO4": 0.132}, "agirlik": 246.51},
        "Magnezyum Nitrat": {"formul": "Mg(NO3)2·6H2O", "besin": {"Mg": 0.09, "NO3": 0.10}, "agirlik": 256.41},
        "Mono Potasyum Fosfat": {"formul": "KH2PO4", "besin": {"K": 0.282, "H2PO4": 0.225}, "agirlik": 136.09},
        "Mono Amonyum Fosfat": {"formul": "NH4H2PO4", "besin": {"H2PO4": 0.266, "NH4": 0.17}, "agirlik": 115.03},
        "Üre Fosfat": {"formul": "H3PO4·CO(NH2)2", "besin": {"H2PO4": 0.194, "N": 0.17}, "agirlik": 1.0},
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
st.write("Aşağıdan hedef besin konsantrasyonlarınızı (mmol/L cinsinden) ve su kaynağı değerlerini girin:")

# Kullanıcıdan su kaynağı değerlerini al
st.subheader("Su Kaynağı Değerleri")
water_ec = st.number_input("Su Kaynağı EC (mS/cm)", min_value=0.0, value=0.0, step=0.01)
water_ph = st.number_input("Su Kaynağı pH", min_value=0.0, value=7.0, step=0.01)
water_no3 = st.number_input("Su Kaynağı NO3 (mmol/L)", min_value=0.0, value=0.0, step=0.01)
water_nh4 = st.number_input("Su Kaynağı NH4 (mmol/L)", min_value=0.0, value=0.0, step=0.01)
water_k = st.number_input("Su Kaynağı K (mmol/L)", min_value=0.0, value=0.0, step=0.01)
water_ca = st.number_input("Su Kaynağı Ca (mmol/L)", min_value=0.0, value=0.0, step=0.01)
water_mg = st.number_input("Su Kaynağı Mg (mmol/L)", min_value=0.0, value=0.0, step=0.01)
water_h2po4 = st.number_input("Su Kaynağı H2PO4 (mmol/L)", min_value=0.0, value=0.0, step=0.01)
water_so4 = st.number_input("Su Kaynağı SO4 (mmol/L)", min_value=0.0, value=0.0, step=0.01)

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

# Su kaynağındaki değerleri dikkate alarak hedef konsantrasyonları güncelle
adjusted_recete = {
    "NO3": max(0, NO3 - water_no3),
    "H2PO4": max(0, H2PO4 - water_h2po4),
    "SO4": max(0, SO4 - water_so4),
    "NH4": max(0, NH4 - water_nh4),
    "K": max(0, K - water_k),
    "Ca": max(0, Ca - water_ca),
    "Mg": max(0, Mg - water_mg),
    "Fe": Fe,
    "B": B,
    "Mn": Mn,
    "Zn": Zn,
    "Cu": Cu,
    "Mo": Mo
}

# Orijinal reçete (su değerleri dahil)
original_recete = {
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
    # Anyon-Katyon dengesi hesaplama (orijinal reçete ile)
    anyon_me = original_recete["NO3"] + original_recete["H2PO4"] + (original_recete["SO4"] * 2)
    katyon_me = original_recete["NH4"] + original_recete["K"] + (original_recete["Ca"] * 2) + (original_recete["Mg"] * 2)
    anyon_mmol = original_recete["NO3"] + original_recete["H2PO4"] + original_recete["SO4"]
    katyon_mmol = original_recete["NH4"] + original_recete["K"] + original_recete["Ca"] + original_recete["Mg"]

    st.write("**Anyon-Katyon Dengesi (Makro Besinler):**")
    tablo_denge = {
        "Anyon": ["NO3", "H2PO4", "SO4", "", "Toplam"],
        "mmol/L (Anyon)": [original_recete["NO3"], original_recete["H2PO4"], original_recete["SO4"], "", anyon_mmol],
        "me/L (Anyon)": [original_recete["NO3"], original_recete["H2PO4"], original_recete["SO4"] * 2, "", anyon_me],
        "Katyon": ["NH4", "K", "Ca", "Mg", "Toplam"],
        "mmol/L (Katyon)": [original_recete["NH4"], original_recete["K"], original_recete["Ca"], original_recete["Mg"], katyon_mmol],
        "me/L (Katyon)": [original_recete["NH4"], original_recete["K"], original_recete["Ca"] * 2, original_recete["Mg"] * 2, katyon_me]
    }
    df_denge = pd.DataFrame(tablo_denge)
    st.table(df_denge)

    # Gelişmiş EC ve pH hesaplama
    # EC hesaplama (iyon etkileşim faktörü ile)
    ec_ion = (original_recete["NO3"] * 0.075) + (original_recete["H2PO4"] * 0.090) + (original_recete["SO4"] * 0.120) + \
             (original_recete["NH4"] * 0.073) + (original_recete["K"] * 0.074) + (original_recete["Ca"] * 0.120) + (original_recete["Mg"] * 0.106)
    ec = (ec_ion + water_ec) * (1 - 0.1)  # Etkileşim faktörü: 0.1

    # pH hesaplama (tamponlama kapasitesi ile)
    h2po4_ratio = original_recete["H2PO4"] / (original_recete["H2PO4"] + 0.01)  # HPO₄²⁻/H₂PO₄⁻ oranı (basitleştirilmiş)
    pka_h2po4 = 7.2
    ph_base = pka_h2po4 + math.log10(h2po4_ratio) if h2po4_ratio > 0 else 7.0
    ph_adjust = -(original_recete["NH4"] * 0.1) + (original_recete["Ca"] * 0.05 + original_recete["Mg"] * 0.03)
    ph = (ph_base + water_ph) / 2 + ph_adjust  # Su pH’sı ile ortalama alınıp düzeltme yapılır

    st.write("**Çözeltinin Tahmini EC ve pH Değerleri:**")
    st.write(f"- **EC**: {ec:.2f} mS/cm")
    st.write(f"- **pH**: {ph:.2f}")

    # Denge kontrolü
    if round(anyon_me, 2) != round(katyon_me, 2):
        st.error("Anyon ve katyon me/L eşit değil! Çözelti dengesiz.")
    else:
        # Makro besinler için gübre miktarları (mmol/L) (su kaynağına göre ayarlanmış reçete ile)
        gubre_miktarlari_mmol = {
            "Kalsiyum Amonyum Nitrat": {"NO3": 0.0, "NH4": 0.0, "Ca": 0.0},
            "Kalsiyum Nitrat": {"NO3": 0.0, "Ca": 0.0},
            "Magnezyum Nitrat": {"Mg": 0.0, "NO3": 0.0},
            "Mono Amonyum Fosfat": {"NH4": 0.0, "H2PO4": 0.0},
            "Mono Potasyum Fosfat": {"H2PO4": 0.0, "K": 0.0},
            "Potasyum Nitrat": {"K": 0.0, "NO3": 0.0},
            "Potasyum Sülfat": {"K": 0.0, "SO4": 0.0}
        }

        # Adım adım hesaplama (HydroBuddy mantığı)
        # 1. Kalsiyum Amonyum Nitrat ile NO₃, NH₄ ve Ca
        total_no3_needed = adjusted_recete["NO3"]
        total_nh4_needed = adjusted_recete["NH4"]
        if total_no3_needed > 0 or total_nh4_needed > 0:
            # Önce NH₄ ihtiyacını karşılayalım
            if total_nh4_needed > 0:
                gubre_miktarlari_mmol["Kalsiyum Amonyum Nitrat"]["NH4"] = total_nh4_needed
                # CAN ile gelen NO₃ ve Ca
                gubre_miktarlari_mmol["Kalsiyum Amonyum Nitrat"]["NO3"] = total_nh4_needed * (0.573 / 0.722)
                gubre_miktarlari_mmol["Kalsiyum Amonyum Nitrat"]["Ca"] = total_nh4_needed * (0.19 / 0.722)
            # Kalan NO₃ ihtiyacını karşılayalım
            remaining_no3 = adjusted_recete["NO3"] - gubre_miktarlari_mmol["Kalsiyum Amonyum Nitrat"]["NO3"]
            if remaining_no3 > 0:
                additional_can = remaining_no3 / 0.573
                gubre_miktarlari_mmol["Kalsiyum Amonyum Nitrat"]["NO3"] += remaining_no3
                gubre_miktarlari_mmol["Kalsiyum Amonyum Nitrat"]["NH4"] += additional_can * (0.722 / 0.573)
                gubre_miktarlari_mmol["Kalsiyum Amonyum Nitrat"]["Ca"] += additional_can * (0.19 / 0.573)

        # 2. Kalan Ca için Kalsiyum Nitrat
        remaining_ca = adjusted_recete["Ca"] - gubre_miktarlari_mmol["Kalsiyum Amonyum Nitrat"]["Ca"]
        if remaining_ca > 0:
            gubre_miktarlari_mmol["Kalsiyum Nitrat"]["Ca"] = remaining_ca
            gubre_miktarlari_mmol["Kalsiyum Nitrat"]["NO3"] = remaining_ca * (0.144 / 0.187) * (62 / 14)

        # 3. Magnezyum Nitrat ile Mg ve NO₃
        if adjusted_recete["Mg"] > 0:
            gubre_miktarlari_mmol["Magnezyum Nitrat"]["Mg"] = adjusted_recete["Mg"]
            gubre_miktarlari_mmol["Magnezyum Nitrat"]["NO3"] = adjusted_recete["Mg"] * (0.10 / 0.09) * (62 / 14)

        # 4. MAP ile NH₄ ve H₂PO₄ (CAN sonrası kalan NH₄ ihtiyacı)
        remaining_nh4 = adjusted_recete["NH4"] - gubre_miktarlari_mmol["Kalsiyum Amonyum Nitrat"]["NH4"]
        if remaining_nh4 > 0:
            gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["NH4"] = remaining_nh4
            gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["H2PO4"] = remaining_nh4 * (0.266 / 0.17) * (31 / 18)

        # 5. MKP ile H₂PO₄ ve K
        remaining_h2po4 = adjusted_recete["H2PO4"] - gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["H2PO4"]
        if remaining_h2po4 > 0:
            gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["H2PO4"] = remaining_h2po4
            gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["K"] = remaining_h2po4 * (0.282 / 0.225)

        # 6. Potasyum Nitrat ile NO₃ ve K
        remaining_no3 = adjusted_recete["NO3"] - (gubre_miktarlari_mmol["Kalsiyum Amonyum Nitrat"]["NO3"] + gubre_miktarlari_mmol["Kalsiyum Nitrat"]["NO3"] + gubre_miktarlari_mmol["Magnezyum Nitrat"]["NO3"])
        if remaining_no3 > 0:
            gubre_miktarlari_mmol["Potasyum Nitrat"]["NO3"] = remaining_no3
            gubre_miktarlari_mmol["Potasyum Nitrat"]["K"] = remaining_no3 * (0.378 / 0.135) * (14 / 62)

        # 7. Potasyum Sülfat ile K ve SO₄
        remaining_k = adjusted_recete["K"] - (gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["K"] + gubre_miktarlari_mmol["Potasyum Nitrat"]["K"])
        if remaining_k > 0:
            gubre_miktarlari_mmol["Potasyum Sülfat"]["K"] = remaining_k
            gubre_miktarlari_mmol["Potasyum Sülfat"]["SO4"] = remaining_k * (0.18 / 0.45)

        # Gram cinsinden hesaplama (1000 litre için) - Makro besinler
        gubre_miktarlari_gram = {}
        for gubre, besinler in gubre_miktarlari_mmol.items():
            if gubre not in gubreler:
                st.error(f"Hata: {gubre} gübresi veritabanında bulunamadı!")
                continue
            gubre_bilgi = gubreler[gubre]
            if gubre == "Kalsiyum Amonyum Nitrat":
                miktar_mmol = besinler["NO3"]
                miktar_gram = (miktar_mmol / 0.573) * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
            elif gubre == "Mono Amonyum Fosfat":
                miktar_mmol = besinler["NH4"]
                miktar_gram = (miktar_mmol / (0.17 / 18)) * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
            elif gubre == "Mono Potasyum Fosfat":
                miktar_mmol = besinler["H2PO4"]
                miktar_gram = (miktar_mmol / (0.225 / 31)) * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
            elif gubre == "Potasyum Sülfat":
                miktar_mmol = besinler["K"]
                miktar_gram = (miktar_mmol / (0.45 / 39)) * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
            elif gubre == "Potasyum Nitrat":
                miktar_mmol = besinler["NO3"]
                miktar_gram = (miktar_mmol / (0.135 / 14 * 62 / 62)) * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
            elif gubre == "Magnezyum Nitrat":
                miktar_mmol = besinler["Mg"]
                miktar_gram = (miktar_mmol / (0.09 / 24)) * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
            elif gubre == "Kalsiyum Nitrat":
                miktar_mmol = besinler["Ca"]
                miktar_gram = (miktar_mmol / (0.187 / 40)) * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
            else:
                miktar_mmol = besinler["Ca"] if "Ca" in besinler else besinler["NO3"]
                miktar_gram = miktar_mmol * gubre_bilgi["agirlik"] if miktar_mmol > 0 else 0.0
            gubre_miktarlari_gram[gubre] = miktar_gram

        # Mikro besinler için gram cinsinden hesaplama (1000 litre için)
        for gubre, info in mikro_besinler.items():
            besin = info["besin"]
            ref_umol_L = info["ref_umol_L"]
            ref_mg_L = info["mg_L"]
            if besin in adjusted_recete and adjusted_recete[besin] > 0:
                gubre_miktarlari_gram[gubre] = (adjusted_recete[besin] / ref_umol_L) * ref_mg_L
            else:
                gubre_miktarlari_gram[gubre] = 0.0

        # Tank stok çözeltileri (kg cinsinden)
        stok_a = {}
        stok_b = {}
        for gubre, miktar in gubre_miktarlari_gram.items():
            stok_miktar_kg = miktar / konsantrasyon
            if gubre in ["Kalsiyum Amonyum Nitrat", "Kalsiyum Nitrat", "Magnezyum Nitrat", "Kalsiyum Hidroksit", "Calmag"]:
                stok_a[gubre] = stok_miktar_kg
            else:
                stok_b[gubre] = stok_miktar_kg

        # Tank hacmi kontrolü
        total_stok_a_kg = sum(stok_a.values())
        total_stok_b_kg = sum(stok_b.values())
        max_kg_per_liter = 1.0  # 1 litre suya yaklaşık 1 kg çözelti sığar (yaklaşık bir değer)
        tank_a_capacity_kg = tank_a_hacim * max_kg_per_liter
        tank_b_capacity_kg = tank_b_hacim * max_kg_per_liter

        if total_stok_a_kg > tank_a_capacity_kg:
            st.warning(f"A tankı hacmi yetersiz! {total_stok_a_kg:.2f} kg stok çözelti gerekiyor, ancak tank sadece {tank_a_capacity_kg:.2f} kg alabilir. Tank hacmini artırın veya konsantrasyon oranını düşürün.")
        if total_stok_b_kg > tank_b_capacity_kg:
            st.warning(f"B tankı hacmi yetersiz! {total_stok_b_kg:.2f} kg stok çözelti gerekiyor, ancak tank sadece {tank_b_capacity_kg:.2f} kg alabilir. Tank hacmini artırın veya konsantrasyon oranını düşürün.")

        # Gübre tablosu (makro ve mikro besinler)
        st.write("**Gübre Miktarları:**")
        tablo_gubre = {
            "Kimyasal Bileşik": ["Kalsiyum Amonyum Nitrat", "Kalsiyum Nitrat", "Magnezyum Nitrat", "Mono Amonyum Fosfat", "Mono Potasyum Fosfat", "Potasyum Nitrat", "Potasyum Sülfat", "Demir-EDDHA", "Boraks", "Mangan Sülfat", "Çinko Sülfat", "Bakır Sülfat", "Sodyum Molibdat", "TOPLAM"],
            "mmol/L": [
                gubre_miktarlari_mmol["Kalsiyum Amonyum Nitrat"]["Ca"],
                gubre_miktarlari_mmol["Kalsiyum Nitrat"]["Ca"],
                gubre_miktarlari_mmol["Magnezyum Nitrat"]["Mg"],
                gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["NH4"],
                gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["H2PO4"],
                gubre_miktarlari_mmol["Potasyum Nitrat"]["K"],
                gubre_miktarlari_mmol["Potasyum Sülfat"]["K"],
                "", "", "", "", "", "", ""
            ],
            "NO3": [
                gubre_miktarlari_mmol["Kalsiyum Amonyum Nitrat"]["NO3"],
                gubre_miktarlari_mmol["Kalsiyum Nitrat"]["NO3"],
                gubre_miktarlari_mmol["Magnezyum Nitrat"]["NO3"],
                "-", "-", gubre_miktarlari_mmol["Potasyum Nitrat"]["NO3"], "-",
                "-", "-", "-", "-", "-", "-",
                original_recete["NO3"]
            ],
            "H2PO4": [
                "-", "-",
                "-",
                gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["H2PO4"],
                gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["H2PO4"],
                "-", "-",
                "-", "-", "-", "-", "-", "-",
                original_recete["H2PO4"]
            ],
            "SO4": [
                "-", "-", "-", "-",
                "-", "-",
                gubre_miktarlari_mmol["Potasyum Sülfat"]["SO4"],
                "-", "-", "-", "-", "-", "-",
                original_recete["SO4"]
            ],
            "NH4": [
                gubre_miktarlari_mmol["Kalsiyum Amonyum Nitrat"]["NH4"],
                "-", "-",
                gubre_miktarlari_mmol["Mono Amonyum Fosfat"]["NH4"],
                "-", "-", "-",
                "-", "-", "-", "-", "-", "-",
                original_recete["NH4"]
            ],
            "K": [
                "-", "-", "-",
                "-",
                gubre_miktarlari_mmol["Mono Potasyum Fosfat"]["K"],
                gubre_miktarlari_mmol["Potasyum Nitrat"]["K"],
                gubre_miktarlari_mmol["Potasyum Sülfat"]["K"],
                "-", "-", "-", "-", "-", "-",
                original_recete["K"]
            ],
            "Ca": [
                gubre_miktarlari_mmol["Kalsiyum Amonyum Nitrat"]["Ca"],
                gubre_miktarlari_mmol["Kalsiyum Nitrat"]["Ca"],
                "-", "-", "-", "-",
                "-", "-", "-", "-", "-", "-", "-",
                original_recete["Ca"]
            ],
            "Mg": [
                "-", "-",
                gubre_miktarlari_mmol["Magnezyum Nitrat"]["Mg"],
                "-", "-", "-", "-",
                "-", "-", "-", "-", "-", "-",
                original_recete["Mg"]
            ],
            "Fe (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", original_recete["Fe"], "-", "-", "-", "-", "-", ""],
            "B (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", "-", original_recete["B"], "-", "-", "-", "-", ""],
            "Mn (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", "-", "-", original_recete["Mn"], "-", "-", "-", ""],
            "Zn (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", original_recete["Zn"], "-", "-", ""],
            "Cu (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", original_recete["Cu"], "-", ""],
            "Mo (µmol/L)": ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", original_recete["Mo"], ""],
            "Gram (1000 L)": [
                f"{gubre_miktarlari_gram.get('Kalsiyum Amonyum Nitrat', 0.0):.2f}",
                f"{gubre_miktarlari_gram.get('Kalsiyum Nitrat', 0.0):.2f}",
                f"{gubre_miktarlari_gram.get('Magnezyum Nitrat', 0.0):.2f}",
                f"{gubre_miktarlari_gram.get('Mono Amonyum Fosfat', 0.0):.2f}",
                f"{gubre_miktarlari_gram.get('Mono Potasyum Fosfat', 0.0):.2f}",
                f"{gubre_miktarlari_gram.get('Potasyum Nitrat', 0.0):.2f}",
                f"{gubre_miktarlari_gram.get('Potasyum Sülfat', 0.0):.2f}",
                f"{gubre_miktarlari_gram.get('Demir-EDDHA', 0.0):.2f}",
                f"{gubre_miktarlari_gram.get('Boraks', 0.0):.2f}",
                f"{gubre_miktarlari_gram.get('Mangan Sülfat', 0.0):.2f}",
                f"{gubre_miktarlari_gram.get('Çinko Sülfat', 0.0):.2f}",
                f"{gubre_miktarlari_gram.get('Bakır Sülfat', 0.0):.2f}",
                f"{gubre_miktarlari_gram.get('Sodyum Molibdat', 0.0):.2f}",
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

        # Reçeteyi kaydetme
        st.subheader("Reçeteyi Kaydet")
        recipe_name = st.text_input("Reçete Adı Girin:")
        if st.button("Reçeteyi Kaydet"):
            if recipe_name:
                saved_recipe = {
                    "name": recipe_name,
                    "original_recete": original_recete,
                    "gubre_miktarlari_gram": gubre_miktarlari_gram,
                    "konsantrasyon": konsantrasyon,
                    "ec": ec,
                    "ph": ph,
                    "stok_a": stok_a,
                    "stok_b": stok_b
                }
                if not os.path.exists("recipes.json"):
                    with open("recipes.json", "w") as f:
                        json.dump([], f)
                with open("recipes.json", "r") as f:
                    recipes = json.load(f)
                recipes.append(saved_recipe)
                with open("recipes.json", "w") as f:
                    json.dump(recipes, f)
                st.success(f"Reçete '{recipe_name}' başarıyla kaydedildi!")
            else:
                st.error("Lütfen bir reçete adı girin!")

        # Kaydedilmiş reçeteleri göster
        st.subheader("Kaydedilmiş Reçeteler")
        if os.path.exists("recipes.json"):
            with open("recipes.json", "r") as f:
                recipes = json.load(f)
            if recipes:
                for recipe in recipes:
                    st.write(f"**Reçete Adı:** {recipe['name']}")
                    st.write("**Hedef Konsantrasyonlar (mmol/L ve µmol/L):**")
                    st.write(recipe['original_recete'])
                    st.write("**Gübre Miktarları (gram, 1000 L için):**")
                    st.write(recipe['gubre_miktarlari_gram'])
                    st.write(f"**Konsantrasyon Oranı:** {recipe['konsantrasyon']}x")
                    st.write(f"**EC:** {recipe['ec']:.2f} mS/cm")
                    st.write(f"**pH:** {recipe['ph']:.2f}")
                    st.write("**A Tankı Stok Çözelti (kg):**")
                    st.write(recipe['stok_a'])
                    st.write("**B Tankı Stok Çözelti (kg):**")
                    st.write(recipe['stok_b'])
                    st.write("---")
            else:
                st.write("Henüz kaydedilmiş reçete yok.")
        else:
            st.write("Henüz kaydedilmiş reçete yok.")

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
