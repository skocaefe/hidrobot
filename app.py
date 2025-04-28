import streamlit as st
import pandas as pd
import numpy as np

# Sayfa ayarlari
st.set_page_config(page_title="HydroBuddy Turkce", page_icon="🌱", layout="wide")

# Baslik ve aciklama
st.title("🌱 HydroBuddy Turkce")
st.markdown("Hidroponik besin cozeltisi hesaplama araci")

# Iyon degerlikleri
iyon_degerlikleri = {
    "NO3": -1, "H2PO4": -1, "SO4": -2,
    "NH4": 1, "K": 1, "Ca": 2, "Mg": 2
}

# Gubre bilgileri
gubreler = {
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2.4H2O", "agirlik": 236.15, "tank": "A", "iyonlar": {"Ca": 1, "NO3": 2}},
    "Potasyum Nitrat": {"formul": "KNO3", "agirlik": 101.10, "tank": "A", "iyonlar": {"K": 1, "NO3": 1}},
    "Magnezyum Nitrat": {"formul": "Mg(NO3)2.6H2O", "agirlik": 256.41, "tank": "A", "iyonlar": {"Mg": 1, "NO3": 2}},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "agirlik": 136.09, "tank": "B", "iyonlar": {"K": 1, "H2PO4": 1}},
    "Magnezyum Sulfat": {"formul": "MgSO4.7H2O", "agirlik": 246.51, "tank": "B", "iyonlar": {"Mg": 1, "SO4": 1}},
    "Potasyum Sulfat": {"formul": "K2SO4", "agirlik": 174.26, "tank": "B", "iyonlar": {"K": 2, "SO4": 1}},
    "Amonyum Sulfat": {"formul": "(NH4)2SO4", "agirlik": 132.14, "tank": "B", "iyonlar": {"NH4": 2, "SO4": 1}},
    "Monoamonyum Fosfat": {"formul": "NH4H2PO4", "agirlik": 115.03, "tank": "B", "iyonlar": {"NH4": 1, "H2PO4": 1}}
}

# Mikro elementler
mikro_gubreler = {
    "Demir EDDHA": {"formul": "Fe-EDDHA %6", "agirlik": 435.0, "element": "Fe", "yuzde": 6},
    "Demir EDTA": {"formul": "Fe-EDTA %13", "agirlik": 346.0, "element": "Fe", "yuzde": 13},
    "Demir DTPA": {"formul": "Fe-DTPA %11", "agirlik": 468.0, "element": "Fe", "yuzde": 11},
    "Borak": {"formul": "Na2B4O7.10H2O", "agirlik": 381.37, "element": "B", "yuzde": 11},
    "Borik Asit": {"formul": "H3BO3", "agirlik": 61.83, "element": "B", "yuzde": 17.5},
    "Mangan Sulfat": {"formul": "MnSO4.H2O", "agirlik": 169.02, "element": "Mn", "yuzde": 32},
    "Cinko Sulfat": {"formul": "ZnSO4.7H2O", "agirlik": 287.56, "element": "Zn", "yuzde": 23},
    "Bakir Sulfat": {"formul": "CuSO4.5H2O", "agirlik": 249.68, "element": "Cu", "yuzde": 25},
    "Sodyum Molibdat": {"formul": "Na2MoO4.2H2O", "agirlik": 241.95, "element": "Mo", "yuzde": 40}
}

# Hazir receteler
hazir_receteler = {
    "Genel Amacli": {
        "NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0,
        "NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0,
        "Fe": 40.0, "B": 30.0, "Mn": 5.0, "Zn": 4.0, "Cu": 0.75, "Mo": 0.5
    },
    "Domates": {
        "NO3": 14.0, "H2PO4": 1.5, "SO4": 1.5,
        "NH4": 1.2, "K": 7.0, "Ca": 4.0, "Mg": 1.5,
        "Fe": 50.0, "B": 40.0, "Mn": 8.0, "Zn": 4.0, "Cu": 0.8, "Mo": 0.5
    },
    "Salatalik": {
        "NO3": 12.0, "H2PO4": 1.3, "SO4": 1.2,
        "NH4": 1.1, "K": 5.8, "Ca": 3.5, "Mg": 1.2,
        "Fe": 45.0, "B": 35.0, "Mn": 6.0, "Zn": 4.0, "Cu": 0.75, "Mo": 0.5
    },
    "Marul": {
        "NO3": 10.0, "H2PO4": 1.0, "SO4": 0.8,
        "NH4": 0.8, "K": 4.5, "Ca": 3.0, "Mg": 0.8,
        "Fe": 35.0, "B": 25.0, "Mn": 4.0, "Zn": 3.0, "Cu": 0.5, "Mo": 0.4
    }
}

# Elementin atomik kutlesi (g/mol)
element_atomik_kutle = {
    "Fe": 55.845, "B": 10.81, "Mn": 54.938, "Zn": 65.38, "Cu": 63.546, "Mo": 95.95
}

# Baslangic session state ayarlari
def initialize_session_state():
    # Recete
    if 'recete' not in st.session_state:
        st.session_state.recete = {
            "NO3": 9.5, "H2PO4": 1.0, "SO4": 0.5, 
            "NH4": 0.5, "K": 5.0, "Ca": 2.25, "Mg": 0.75
        }

    # Tank ayarlari
    if 'a_tank' not in st.session_state:
        st.session_state.a_tank = 19

    if 'b_tank' not in st.session_state:
        st.session_state.b_tank = 19

    if 'konsantrasyon' not in st.session_state:
        st.session_state.konsantrasyon = 100

    # Kuyu suyu
    if 'kuyu_suyu' not in st.session_state:
        st.session_state.kuyu_suyu = {
            "NO3": 0.0, "H2PO4": 0.0, "SO4": 0.0, 
            "NH4": 0.0, "K": 0.0, "Ca": 0.0, "Mg": 0.0
        }

    # Kullanilabilir gubreler
    if 'kullanilabilir_gubreler' not in st.session_state:
        st.session_state.kullanilabilir_gubreler = {gubre: False for gubre in gubreler.keys()}

    # Kullanilabilir mikro gubreler
    if 'kullanilabilir_mikro_gubreler' not in st.session_state:
        st.session_state.kullanilabilir_mikro_gubreler = {gubre: False for gubre in mikro_gubreler.keys()}

    # Secilen mikro gubreler
    if 'secilen_mikro_gubreler' not in st.session_state:
        st.session_state.secilen_mikro_gubreler = {
            "Fe": None, "B": None, "Mn": None, "Zn": None, "Cu": None, "Mo": None
        }

    # Hesaplama logu
    if 'hesaplama_log' not in st.session_state:
        st.session_state.hesaplama_log = []

    # Hesaplama sonucu
    if 'hesaplama_sonucu' not in st.session_state:
        st.session_state.hesaplama_sonucu = None

# Iyonik denge hesaplama
def hesapla_iyonik_denge(recete):
    anyon_toplam = sum(float(recete[ion]) * abs(iyon_degerlikleri[ion]) for ion in ["NO3", "H2PO4", "SO4"])
    katyon_toplam = sum(float(recete[ion]) * abs(iyon_degerlikleri[ion]) for ion in ["NH4", "K", "Ca", "Mg"])
    return anyon_toplam, katyon_toplam

# Simulasyon ile besinlerin karsilanip karsilanamayacagini kontrol etme
def karsilanabilirlik_kontrolu(recete, secilen_gubreler):
    net_ihtiyac = {ion: max(0, float(recete[ion])) for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]}

    if "Kalsiyum Nitrat" in secilen_gubreler and net_ihtiyac["Ca"] > 0:
        net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Ca"]
        net_ihtiyac["Ca"] = 0

    if "Magnezyum Nitrat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Mg"]
        net_ihtiyac["Mg"] = 0
    elif "Magnezyum Sulfat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        net_ihtiyac["SO4"] -= net_ihtiyac["Mg"]
        net_ihtiyac["Mg"] = 0

    if "Monopotasyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        net_ihtiyac["K"] -= net_ihtiyac["H2PO4"]
        net_ihtiyac["H2PO4"] = 0
    elif "Monoamonyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        net_ihtiyac["NH4"] -= net_ihtiyac["H2PO4"]
        net_ihtiyac["H2PO4"] = 0

    if "Amonyum Sulfat" in secilen_gubreler and net_ihtiyac["NH4"] > 0:
        as_miktar = min(net_ihtiyac["NH4"] / 2, net_ihtiyac["SO4"])
        net_ihtiyac["NH4"] -= 2 * as_miktar
        net_ihtiyac["SO4"] -= as_miktar

    if "Potasyum Nitrat" in secilen_gubreler and net_ihtiyac["K"] > 0 and net_ihtiyac["NO3"] > 0:
        kn_miktar = min(net_ihtiyac["K"], net_ihtiyac["NO3"])
        net_ihtiyac["K"] -= kn_miktar
        net_ihtiyac["NO3"] -= kn_miktar

    if "Potasyum Sulfat" in secilen_gubreler and net_ihtiyac["K"] > 0:
        net_ihtiyac["SO4"] -= net_ihtiyac["K"] / 2
        net_ihtiyac["K"] = 0

    for iyon in net_ihtiyac:
        if net_ihtiyac[iyon] < 0:
            net_ihtiyac[iyon] = 0

    return [iyon for iyon, miktar in net_ihtiyac.items() if miktar > 0.1]

# Gubre hesaplama fonksiyonu
def gubre_hesapla():
    # Secilen gübreleri al
    secilen_gubreler = [gubre for gubre, secildi in st.session_state.kullanilabilir_gubreler.items() if secildi]
    secilen_mikro_gubreler = [gubre for element, gubre in st.session_state.secilen_mikro_gubreler.items() if gubre]

    # Hata ayiklama logu
    st.session_state.hesaplama_log = []
    st.session_state.hesaplama_log.append({
        "adim": "Baslangic", "aciklama": f"Secilen makro gubreler: {secilen_gubreler}", "ihtiyac": {}
    })

    if not secilen_gubreler:
        st.error("Lutfen 'Gubre Secimi' sekmesinden en az bir makro gubre secin!")
        st.warning(f"Hata Ayiklama: Secilen gubreler bos. Tum gubre durumu: {st.session_state.kullanilabilir_gubreler}")
        return None

    # Net ihtiyac hesaplama
    net_ihtiyac = {
        ion: max(0, float(st.session_state.recete[ion]) - float(st.session_state.kuyu_suyu[ion]))
        for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]
    }
    a_tank_gubreler = {}
    b_tank_gubreler = {}
    adim = 1

    st.session_state.hesaplama_log.append({
        "adim": "Kuyu Suyu Sonrasi", "aciklama": "Kuyu suyu sonrasi ihtiyaclar",
        "ihtiyac": {k: round(v, 2) for k, v in
