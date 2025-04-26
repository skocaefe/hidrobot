import streamlit as st
import pandas as pd
import numpy as np

# Sayfa ayarları
st.set_page_config(page_title="Hidrobot", page_icon="🤖", layout="wide")

# Başlık ve açıklama
st.title("🤖 Hidrobot")
st.markdown("Hidroponik besin çözeltisi hesaplama aracı")

# İyon değerlikleri
iyon_degerlikleri = {
    "NO3": -1, "H2PO4": -1, "SO4": -2,
    "NH4": 1, "K": 1, "Ca": 2, "Mg": 2
}

# Gübre bilgileri
gubreler = {
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2.4H2O", "agirlik": 236.15, "tank": "A", "iyonlar": {"Ca": 1, "NO3": 2}},
    "Potasyum Nitrat": {"formul": "KNO3", "agirlik": 101.10, "tank": "A", "iyonlar": {"K": 1, "NO3": 1}},
    "Magnezyum Nitrat": {"formul": "Mg(NO3)2.6H2O", "agirlik": 256.41, "tank": "A", "iyonlar": {"Mg": 1, "NO3": 2}},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "agirlik": 136.09, "tank": "B", "iyonlar": {"K": 1, "H2PO4": 1}},
    "Magnezyum Sülfat": {"formul": "MgSO4.7H2O", "agirlik": 246.51, "tank": "B", "iyonlar": {"Mg": 1, "SO4": 1}},
    "Potasyum Sülfat": {"formul": "K2SO4", "agirlik": 174.26, "tank": "B", "iyonlar": {"K": 2, "SO4": 1}},
    "Amonyum Sülfat": {"formul": "(NH4)2SO4", "agirlik": 132.14, "tank": "B", "iyonlar": {"NH4": 2, "SO4": 1}},
    "Monoamonyum Fosfat": {"formul": "NH4H2PO4", "agirlik": 115.03, "tank": "B", "iyonlar": {"NH4": 1, "H2PO4": 1}}
}

# Hazır reçeteler
hazir_receteler = {
    "Genel Amaçlı": {
        "NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0,
        "NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0
    }
}

# Session state başlangıcı
if 'recete' not in st.session_state:
    st.session_state.recete = hazir_receteler["Genel Amaçlı"].copy()
if 'konsantrasyon' not in st.session_state:
    st.session_state.konsantrasyon = 100

# --- Fonksiyonlar ---
def hesapla_iyonik_denge(recete):
    anyon_toplam = sum(float(recete[ion]) * abs(iyon_degerlikleri[ion]) for ion in ["NO3", "H2PO4", "SO4"])
    katyon_toplam = sum(float(recete[ion]) * abs(iyon_degerlikleri[ion]) for ion in ["NH4", "K", "Ca", "Mg"])
    return anyon_toplam, katyon_toplam

def otomatik_iyon_duzelt(recete, hedef_fark=0.5):
    anyon_toplam, katyon_toplam = hesapla_iyonik_denge(recete)
    fark = anyon_toplam - katyon_toplam
    if abs(fark) <= hedef_fark:
        return recete, "Zaten dengede."
    if fark > 0:
        recete["K"] += fark
        duzeltme = f"K (potasyum) artırıldı: +{fark:.2f} mmol/L"
    else:
        recete["NO3"] += abs(fark)
        duzeltme = f"NO3 (nitrat) artırıldı: +{abs(fark):.2f} mmol/L"
    return recete, duzeltme

def alternatif_gubre_onerileri(eksik_iyonlar, secilen_gubreler):
    oneriler = {}
    for eksik in eksik_iyonlar:
        alternatifler = []
        for gubre_adi, gubre_bilgi in gubreler.items():
            if gubre_adi not in secilen_gubreler:
                if "iyonlar" in gubre_bilgi and eksik in gubre_bilgi["iyonlar"]:
                    alternatifler.append(f"{gubre_adi} ({gubre_bilgi['formul']})")
        if alternatifler:
            oneriler[eksik] = alternatifler
        else:
            oneriler[eksik] = ["Uygun gübre bulunamadı."]
    return oneriler
# --- Fonksiyonlar Sonu ---

# --- Ana Sayfa ---

st.header("🌱 Reçete Ayarları")
st.selectbox("Hazır Reçete Seçimi", options=list(hazir_receteler.keys()), key="recete_secimi")
if st.button("Reçeteyi Yükle"):
    st.session_state.recete = hazir_receteler[st.session_state.recete_secimi].copy()
    st.success(f"{st.session_state.recete_secimi} reçetesi yüklendi!")

st.number_input("Konsantrasyon Oranı", min_value=10, max_value=300, value=st.session_state.konsantrasyon, step=10, key="konsantrasyon")

st.subheader("🔬 İyon Değerleri (mmol/L)")
cols = st.columns(4)
iyonlar = ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]
for i, ion in enumerate(iyonlar):
    with cols[i % 4]:
        st.session_state.recete[ion] = st.number_input(f"{ion}", min_value=0.0, max_value=20.0, step=0.1, value=float(st.session_state.recete[ion]), key=f"input_{ion}")

# İyonik denge gösterimi
anyon_toplam, katyon_toplam = hesapla_iyonik_denge(st.session_state.recete)
st.subheader("⚖️ İyonik Denge")
col1, col2 = st.columns(2)
col1.metric("Anyon Yükü (me/L)", f"{anyon_toplam:.2f}")
col2.metric("Katyon Yükü (me/L)", f"{katyon_toplam:.2f}")

# Otomatik denge butonu
if st.button("🔧 İyonik Dengeyi Otomatik Düzelt"):
    st.session_state.recete, mesaj = otomatik_iyon_duzelt(st.session_state.recete)
    st.success(f"✅ {mesaj}")

# Gübre seçimi
st.subheader("🧪 Kullanılacak Gübreler")
secilen_gubreler = st.multiselect("Gübreleri Seç", options=list(gubreler.keys()))

# Eksik iyon kontrolü
if secilen_gubreler:
    net_ihtiyac = {ion: float(st.session_state.recete[ion]) for ion in iyonlar}
    for gubre in secilen_gubreler:
        for ion, miktar in gubreler[gubre]["iyonlar"].items():
            if ion in net_ihtiyac:
                net_ihtiyac[ion] -= miktar

    eksik_besinler = [ion for ion, miktar in net_ihtiyac.items() if miktar > 0.1]

    if eksik_besinler:
        st.warning("Bazı besin ihtiyaçları seçilen gübrelerle tam karşılanamıyor.")
        alternatifler = alternatif_gubre_onerileri(eksik_besinler, secilen_gubreler)
        st.subheader("Önerilen Gübreler")
        for eksik, alternatif_listesi in alternatifler.items():
            st.markdown(f"- **{eksik}** için uygun gübreler: {', '.join(alternatif_listesi)}")
    else:
        st.success("✅ Seçilen gübrelerle tüm ihtiyaçlar karşılanabiliyor.")
else:
    st.info("ℹ️ Henüz gübre seçilmedi.")

st.markdown("---")
st.markdown("🤖 **Hidrobot | Hidroponik besin çözeltisi hesaplama aracı**")

