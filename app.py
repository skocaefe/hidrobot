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
