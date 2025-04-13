import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Sayfa ayarları
st.set_page_config(
    page_title="HydroBuddy İyonik Denge Hesaplayıcı",
    page_icon="🌱",
    layout="wide"
)

# Başlık ve açıklama
st.title("🌱 HydroBuddy İyonik Denge Hesaplayıcı")
st.markdown("Hidroponik besin çözeltilerinde anyon-katyon dengesi ve kimyasal hesaplamalar")

# Gübre bilgilerini içeren veritabanı
gubre_veritabani = {
    "Ca(NO3)2.4H2O": {"formul": "Ca(NO3)2.4H2O", "formul_agirligi": 236.15, 
                      "anyonlar": {"NO3": 2}, "katyonlar": {"Ca": 1}, "a_tank": True},
    "KNO3": {"formul": "KNO3", "formul_agirligi": 101.10, 
             "anyonlar": {"NO3": 1}, "katyonlar": {"K": 1}},
    "NH4NO3": {"formul": "NH4NO3", "formul_agirligi": 80.04, 
               "anyonlar": {"NO3": 1}, "katyonlar": {"NH4": 1}},
    "KH2PO4": {"formul": "KH2PO4", "formul_agirligi": 136.09, 
               "anyonlar": {"H2PO4": 1}, "katyonlar": {"K": 1}, "b_tank": True},
    "K2SO4": {"formul": "K2SO4", "formul_agirligi": 174.26, 
              "anyonlar": {"SO4": 1}, "katyonlar": {"K": 2}},
    "MgSO4.7H2O": {"formul": "MgSO4.7H2O", "formul_agirligi": 246.51, 
                   "anyonlar": {"SO4": 1}, "katyonlar": {"Mg": 1}}
}

# Mikro besin veritabanı
mikro_besin_veritabani = {
    "Fe-EDDHA": {"formul": "Fe-EDDHA", "formul_agirligi": 435, "element": "Fe"},
    "Na2B4O7.10H2O": {"formul": "Na2B4O7.10H2O", "formul_agirligi": 381.37, "element": "B"},
    "MnSO4.H2O": {"formul": "MnSO4.H2O", "formul_agirligi": 169.02, "element": "Mn"},
    "ZnSO4.7H2O": {"formul": "ZnSO4.7H2O", "formul_agirligi": 287.56, "element": "Zn"},
    "CuSO4.5H2O": {"formul": "CuSO4.5H2O", "formul_agirligi": 249.68, "element": "Cu"},
    "Na2MoO4.2H2O": {"formul": "Na2MoO4.2H2O", "formul_agirligi": 241.95, "element": "Mo"}
}

# Hazır reçeteler
hazir_receteler = {
    "Genel Amaçlı": {
        "anyon_katyon": {
            "NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0,
            "NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0
        },
        "mikro": {
            "Fe": 40, "B": 30, "Mn": 5, "Zn": 4, "Cu": 0.75, "Mo": 0.5
        }
    },
    "Domates": {
        "anyon_katyon": {
            "NO3": 14.0, "H2PO4": 1.5, "SO4": 1.5,
            "NH4": 1.2, "K": 7.0, "Ca": 4.0, "Mg": 1.5
        },
        "mikro": {
            "Fe": 50, "B": 40, "Mn": 8, "Zn": 4, "Cu": 0.8, "Mo": 0.5
        }
    },
    "Salatalık": {
        "anyon_katyon": {
            "NO3": 12.0, "H2PO4": 1.3, "SO4": 1.2,
            "NH4": 1.1, "K": 5.8, "Ca": 3.5, "Mg": 1.2
        },
        "mikro": {
            "Fe": 45, "B": 35, "Mn": 6, "Zn": 4, "Cu": 0.75, "Mo": 0.5
        }
    },
    "Marul": {
        "anyon_katyon": {
            "NO3": 10.0, "H2PO4": 1.0, "SO4": 0.8,
            "NH4": 0.8, "K": 4.5, "Ca": 3.0, "Mg": 0.8
        },
        "mikro": {
            "Fe": 35, "B": 25, "Mn": 4, "Zn": 3, "Cu": 0.5, "Mo": 0.4
        }
    },
    "Çilek": {
        "anyon_katyon": {
            "NO3": 11.0, "H2PO4": 1.2, "SO4": 1.0,
            "NH4": 0.9, "K": 5.0, "Ca": 3.2, "Mg": 1.0
        },
        "mikro": {
            "Fe": 40, "B": 30, "Mn": 5, "Zn": 4, "Cu": 0.6, "Mo": 0.4
        }
    }
}

# İyon değerlikleri
iyon_degerlikleri = {
    "NO3": -1, "H2PO4": -1, "SO4": -2,
    "NH4": 1, "K": 1, "Ca": 2, "Mg": 2
}

# Session state başlatma
if 'recete_secimleri' not in st.session_state:
    st.session_state.recete_secimleri = {
        "NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0,
        "NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0
    }

if 'mikro_secimleri' not in st.session_state:
    st.session_state.mikro_secimleri = {
        "Fe": 40, "B": 30, "Mn": 5, "Zn": 4, "Cu": 0.75, "Mo": 0.5
    }

if 'a_tank_hacmi' not in st.session_state:
    st.session_state.a_tank_hacmi = 10  # litre

if 'b_tank_hacmi' not in st.session_state:
    st.session_state.b_tank_hacmi = 10  # litre

if 'konsantrasyon_orani' not in st.session_state:
    st.session_state.konsantrasyon_orani = 100  # 100x

# Ana sekmeleri oluştur
tab1, tab2, tab3 = st.tabs(["Reçete Seçimi", "Gübre Hesaplama", "Sonuçlar"])

# Reçete Seçimi Sekmesi
with tab1:
    st.header("Reçete Seçimi")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Hazır Reçete Seç")
        
        secilen_recete = st.selectbox(
            "Hazır reçete seçin:",
            options=list(hazir_receteler.keys()),
            index=0
        )
        
        if st.button("Hazır Reçeteyi Yükle"):
            st.session_state.recete_secimleri = hazir_receteler[secilen_recete]["anyon_katyon"].copy()
            st.session_state.mikro_secimleri = hazir_receteler[secilen_recete]["mikro"].copy()
            st.success(f"{secilen_recete} reçetesi yüklendi!")
    
    with col2:
        st.subheader("Manuel Reçete Ayarla")
        
        st.write("**Anyon Değerleri (mmol/L)**")
        col_anyon1, col_anyon2, col_anyon3 = st.columns(3)
        
        with col_anyon1:
            no3_value = st.number_input("NO3 (Nitrat)", 
                               min_value=0.0, max_value=30.0, 
                               value=float(st.session_state.recete_secimleri["NO3"]), 
                               step=0.1, format="%.2f")
            st.session_state.recete_secimleri["NO3"] = no3_value
        
        with col_anyon2:
            h2po4_value = st.number_input("H2PO4 (Fosfat)", 
                               min_value=0.0, max_value=10.0, 
                               value=float(st.session_state.recete_secimleri["H2PO4"]), 
                               step=0.1, format="%.2f")
            st.session_state.recete_secimleri["H2PO4"] = h2po4_value
        
        with col_anyon3:
            so4_value = st.number_input("SO4 (Sülfat)", 
                               min_value=0.0, max_value=10.0, 
                               value=float(st.session_state.recete_secimleri["SO4"]), 
                               step=0.1, format="%.2f")
            st.session_state.recete_secimleri["SO4"] = so4_value
        
        st.write("**Katyon Değerleri (mmol/L)**")
        col_kat1, col_kat2, col_kat3, col_kat4 = st.columns(4)
        
        with col_kat1:
            nh4_value = st.number_input("NH4 (Amonyum)", 
                               min_value=0.0, max_value=10.0, 
                               value=float(st.session_state.recete_secimleri["NH4"]), 
                               step=0.1, format="%.2f")
            st.session_state.recete_secimleri["NH4"] = nh4_value
        
        with col_kat2:
            k_value = st.number_input("K (Potasyum)", 
                               min_value=0.0, max_value=20.0, 
                               value=float(st.session_state.recete_secimleri["K"]), 
                               step=0.1, format="%.2f")
            st.session_state.recete_secimleri["K"] = k_value
        
        with col_kat3:
            ca_value = st.number_input("Ca (Kalsiyum)", 
                               min_value=0.0, max_value=15.0, 
                               value=float(st.session_state.recete_secimleri["Ca"]), 
                               step=0.1, format="%.2f")
            st.session_state.recete_secimleri["Ca"] = ca_value
        
        with col_kat4:
            mg_value = st.number_input("Mg (Magnezyum)", 
                               min_value=0.0, max_value=10.0, 
                               value=float(st.session_state.recete_secimleri["Mg"]), 
                               step=0.1, format="%.2f")
            st.session_state.recete_secimleri["Mg"] = mg_value
    
    st.subheader("Mikro Besin Elementleri (mikromol/L)")
    col_mikro1, col_mikro2, col_mikro3 = st.columns(3)
    col_mikro4, col_mikro5, col_mikro6 = st.columns(3)
    
    with col_mikro1:
        fe_value = st.number_input("Fe (Demir)", 
                           min_value=0.0, max_value=100.0, 
                           value=float(st.session_state.mikro_secimleri["Fe"]), 
                           step=1.0, format="%.1f")
        st.session_state.mikro_secimleri["Fe"] = fe_value
    
    with col_mikro2:
        b_value = st.number_input("B (Bor)", 
                           min_value=0.0, max_value=100.0, 
                           value=float(st.session_state.mikro_secimleri["B"]), 
                           step=1.0, format="%.1f")
        st.session_state.mikro_secimleri["B"] = b_value
    
    with col_mikro3:
        mn_value = st.number_input("Mn (Mangan)", 
                           min_value=0.0, max_value=50.0, 
                           value=float(st.session_state.mikro_secimleri["Mn"]), 
                           step=0.5, format="%.1f")
        st.session_state.mikro_secimleri["Mn"] = mn_value
    
    with col_mikro4:
        zn_value = st.number_input("Zn (Çinko)", 
                           min_value=0.0, max_value=50.0, 
                           value=float(st.session_state.mikro_secimleri["Zn"]), 
                           step=0.5, format="%.1f")
        st.session_state.mikro_secimleri["Zn"] = zn_value
    
    with col_mikro5:
        cu_value = st.number_input("Cu (Bakır)", 
                           min_value=0.0, max_value=10.0, 
                           value=float(st.session_state.mikro_secimleri["Cu"]), 
                           step=0.05, format="%.2f")
        st.session_state.mikro_secimleri["Cu"] = cu_value
    
    with col_mikro6:
        mo_value = st.number_input("Mo (Molibden)", 
                           min_value=0.0, max_value=10.0, 
                           value=float(st.session_state.mikro_secimleri["Mo"]), 
                           step=0.05, format="%.2f")
        st.session_state.mikro_secimleri["Mo"] = mo_value
    
    # İyonik denge hesaplama fonksiyonu
    def hesapla_iyonik_denge(recete):
        anyon_toplam_me = 0
        katyon_toplam_me = 0
        
        # Anyonlar
        for anyon in ["NO3", "H2PO4", "SO4"]:
            if anyon in recete:
                deger = recete[anyon]
                valens = abs(iyon_degerlikleri[anyon])
                anyon_toplam_me += deger * valens
        
        # Katyonlar
        for katyon in ["NH4", "K", "Ca", "Mg"]:
            if katyon in recete:
                deger = recete[katyon]
                valens = abs(iyon_degerlikleri[katyon])
                katyon_toplam_me += deger * valens
        
        return anyon_toplam_me, katyon_toplam_me
    
    # İyonik denge değerlerini hesapla
    anyon_me, katyon_me = hesapla_iyonik_denge(st.session_state.recete_secimleri)
    
    st.subheader("İyonik Denge Durumu")
    
    col_sonuc1, col_sonuc2 = st.columns(2)
    
    with col_sonuc1:
        st.metric("Toplam Anyon (me/L)", f"{anyon_me:.2f}")
    
    with col_sonuc2:
        st.metric("Toplam Katyon (me/L)", f"{katyon_me:.2f}")
    
    # Denge kontrolü
    fark = abs(anyon_me - katyon_me)
    if fark < 0.5:
        st.success(f"✅ İyonik denge sağlanmış! (Fark: {fark:.2f} me/L)")
    elif fark < 1.0:
        st.warning(f"⚠️ İyonik denge kabul edilebilir sınırda. (Fark: {fark:.2f} me/L)")
    else:
        st.error(f"❌ İyonik denge sağlanamamış. Anyonlar ve katyonlar arasındaki fark çok yüksek. (Fark: {fark:.2f} me/L)")
        
        if anyon_me > katyon_me:
            st.info("Öneri: Katyon değerlerini artırın veya anyon değerlerini azaltın.")
        else:
            st.info("Öneri: Anyon değerlerini artırın veya katyon değerlerini azaltın.")
    
    # Grafikler
    st.subheader("İyonik Denge Grafiği")
    
    # Anyonlar ve katyonlar için grafikler
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Anyon grafiği
    anyon_labels = ["NO3", "H2PO4", "SO4"]
    anyon_values = [st.session_state.recete_secimleri[a] for a in anyon_labels]
    anyon_me_values = [st.session_state.recete_secimleri[a] * abs(iyon_degerlikleri[a]) for a in anyon_labels]
    
    ax1.bar(anyon_labels, anyon_me_values, color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    ax1.set_title('Anyonlar (me/L)')
    ax1.set_ylim(0, max(max(anyon_me_values), 1) * 1.2)
    
    # Katyon grafiği
    katyon_labels = ["NH4", "K", "Ca", "Mg"]
    katyon_values = [st.session_state.recete_secimleri[k] for k in katyon_labels]
    katyon_me_values = [st.session_state.recete_secimleri[k] * abs(iyon_degerlikleri[k]) for k in katyon_labels]
    
    ax2.bar(katyon_labels, katyon_me_values, color=['#d62728', '#9467bd', '#8c564b', '#e377c2'])
    ax2.set_title('Katyonlar (me/L)')
    ax2.set_ylim(0, max(max(katyon_me_values), 1) * 1.2)
    
    fig.tight_layout()
    st.pyplot(fig)

# Gübre Hesaplama Sekmesi
with tab2:
    st.header("Gübre Hesaplama")
    
    # Tank ayarları
    st.subheader("Tank Ayarları")
    
    col_tank1, col_tank2, col_tank3 = st.columns(3)
    
    with col_tank1:
        a_tank_hacmi = st.number_input("A Tankı Hacmi (litre):", 
                                       min_value=1, max_value=1000, 
                                       value=st.session_state.a_tank_hacmi)
        st.session_state.a_tank_hacmi = a_tank_hacmi
    
    with col_tank2:
        b_tank_hacmi = st.number_input("B Tankı Hacmi (litre):", 
                                       min_value=1, max_value=1000, 
                                       value=st.session_state.b_tank_hacmi)
        st.session_state.b_tank_hacmi = b_tank_hacmi
    
    with col_tank3:
        konsantrasyon_orani = st.number_input("Konsantrasyon Oranı:", 
                                             min_value=1, max_value=1000, 
                                             value=st.session_state.konsantrasyon_orani)
        st.session_state.konsantrasyon_orani = konsantrasyon_orani
    
    # Gübre hesaplama fonksiyonu
    def hesapla_gubreler(recete, mikro):
        # Otomatik gübre seçim algoritması
        secilen_gubreler = {}
        
        # A Tankı için (Ca içeren)
        a_tank_gubreler = {}
        
        # B Tankı için (P içeren)
        b_tank_gubreler = {}
        
        # Diğer gübreler
        diger_gubreler = {}
        
        # 1. Kalsiyum Nitrat (A tankı için)
        if recete["Ca"] > 0:
            a_tank_gubreler["Ca(NO3)2.4H2O"] = recete["Ca"]
            kalan_nitrat = recete["NO3"] - (2 * recete["Ca"])
        else:
            kalan_nitrat = recete["NO3"]
        
        # 2. Monopotasyum Fosfat (B tankı için)
        if recete["H2PO4"] > 0:
            b_tank_gubreler["KH2PO4"] = recete["H2PO4"]
            kalan_k = recete["K"] - recete["H2PO4"]
        else:
            kalan_k = recete["K"]
        
        # 3. Magnezyum Sülfat
        if recete["Mg"] > 0:
            diger_gubreler["MgSO4.7H2O"] = recete["Mg"]
            kalan_sulfat = recete["SO4"] - recete["Mg"]
        else:
            kalan_sulfat = recete["SO4"]
        
        # 4. Amonyum Nitrat
        if recete["NH4"] > 0:
            if kalan_nitrat >= recete["NH4"]:
                diger_gubreler["NH4NO3"] = recete["NH4"]
                kalan_nitrat -= recete["NH4"]
                kalan_nh4 = 0
            else:
                diger_gubreler["NH4NO3"] = kalan_nitrat
                kalan_nh4 = recete["NH4"] - kalan_nitrat
                kalan_nitrat = 0
        else:
            kalan_nh4 = 0
        
        # 5. Potasyum Nitrat
        if kalan_k > 0 and kalan_nitrat > 0:
            kullanilacak_kno3 = min(kalan_k, kalan_nitrat)
            diger_gubreler["KNO3"] = kullanilacak_kno3
            kalan_nitrat -= kullanilacak_kno3
            kalan_k -= kullanilacak_kno3
        
        # 6. Potasyum Sülfat (kalan K için)
        if kalan_k > 0 and kalan_sulfat > 0:
            kullanilacak_k2so4 = min(kalan_k / 2, kalan_sulfat)
            diger_gubreler["K2SO4"] = kullanilacak_k2so4
            
        # Mikro besinleri hesapla
        mikro_gubreler = {}
        
        if mikro["Fe"] > 0:
            mikro_gubreler["Fe-EDDHA"] = mikro["Fe"] / 1000  # mikromol/L -> mmol/L
        
        if mikro["B"] > 0:
            mikro_gubreler["Na2B4O7.10H2O"] = mikro["B"] / 1000
        
        if mikro["Mn"] > 0:
            mikro_gubreler["MnSO4.H2O"] = mikro["Mn"] / 1000
        
        if mikro["Zn"] > 0:
            mikro_gubreler["ZnSO4.7H2O"] = mikro["Zn"] / 1000
        
        if mikro["Cu"] > 0:
            mikro_gubreler["CuSO4.5H2O"] = mikro["Cu"] / 1000
        
        if mikro["Mo"] > 0:
            mikro_gubreler["Na2MoO4.2H2O"] = mikro["Mo"] / 1000
        
        return a_tank_gubreler, b_tank_gubreler, diger_gubreler, mikro_gubreler
    
    # mmol/L değerlerini mg/L değerlerine dönüştürme fonksiyonu
    def mmol_to_mg(gubre_adi, mmol_deger):
        return mmol_deger * gubre_veritabani[gubre_adi]["formul_agirligi"]
    
    def mikro_mmol_to_mg(gubre_adi, mmol_deger):
        return mmol_deger * mikro_besin_veritabani[gubre_adi]["formul_agirligi"]
    
    # Gübre hesaplama
    if st.button("Gübre Hesapla"):
        # İyonik dengeyi kontrol et
        anyon_me, katyon_me = hesapla_iyonik_denge(st.session_state.recete_secimleri)
        fark = abs(anyon_me - katyon_me)
        
        if fark > 1.0:
            st.error("⚠️ İyonik denge sağlanmadan gübre hesaplaması yapılması önerilmez. Lütfen önce iyonik dengeyi sağlayın.")
        
        # Gübre hesapla
        a_tank, b_tank, diger, mikro = hesapla_gubreler(st.session_state.recete_secimleri, st.session_state.mikro_secimleri)
        
        # Sonuçları göster
        st.subheader("Hesaplanan Gübreler")
        
        # A Tankı için tablo
        st.write("**A Tankı (Kalsiyum İçeren)**")
        a_tank_data = []
        for gubre, mmol in a_tank.items():
            mg_per_liter = mmol_to_mg(gubre, mmol)
            mg_per_tank = mg_per_liter * st.session_state.konsantrasyon_orani * st.session_state.a_tank_hacmi
            a_tank_data.append([gubre, f"{mmol:.2f}", f"{mg_per_liter:.2f}", f"{mg_per_tank/1000:.2f}"])
        
        a_tank_df = pd.DataFrame(a_tank_data, columns=["Kimyasal Bileşik", "mmol/L", "mg/L", "g/Tank"])
        st.table(a_tank_df)
        
        # B Tankı için tablo
        st.write("**B Tankı (Fosfat İçeren)**")
        b_tank_data = []
        for gubre, mmol in b_tank.items():
            mg_per_liter = mmol_to_mg(gubre, mmol)
            mg_per_tank = mg_per_liter * st.session_state.konsantrasyon_orani * st.session_state.b_tank_hacmi
            b_tank_data.append([gubre, f"{mmol:.2f}", f"{mg_per_liter:.2f}", f"{mg_per_tank/1000:.2f}"])
        
        b_tank_df = pd.DataFrame(b_tank_data, columns=["Kimyasal Bileşik", "mmol/L", "mg/L", "g/Tank"])
        st.table(b_tank_df)
        
        # Diğer gübreler için tablo
        st.write("**Diğer Gübreler**")
        diger_data = []
        for gubre, mmol in diger.items():
            mg_per_liter = mmol_to_mg(gubre, mmol)
            mg_per_tank = mg_per_liter * st.session_state.konsantrasyon_orani * st.session_state.b_tank_hacmi
            diger_data.append([gubre, f"{mmol:.2f}", f"{mg_per_liter:.2f}", f"{mg_per_tank/1000:.2f}"])
        
        diger_df = pd.DataFrame(diger_data, columns=["Kimyasal Bileşik", "mmol/L", "mg/L", "g/Tank"])
        st.table(diger_df)
        
        # Mikro besinler için tablo
        st.write("**Mikro Besinler**")
        mikro_data = []
        for gubre, mmol in mikro.items():
            mg_per_liter = mikro_mmol_to_mg(gubre, mmol)
            mg_per_tank = mg_per_liter * st.session_state.konsantrasyon_orani * st.session_state.b_tank_hacmi
