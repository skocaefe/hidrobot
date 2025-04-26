import streamlit as st
import pandas as pd
import numpy as np

# Sayfa ayarları
st.set_page_config(page_title="HydroBuddy Türkçe", page_icon="🌱", layout="wide")

# Başlık ve açıklama
st.title("🌱 HydroBuddy Türkçe")
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
    "Kalsiyum Amonyum Nitrat": {"formul": "5Ca(NO3)2.NH4NO3.10H2O", "agirlik": 1080.0, "tank": "A", "iyonlar": {"Ca": 5, "NH4": 1, "NO3": 11}},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "agirlik": 136.09, "tank": "B", "iyonlar": {"K": 1, "H2PO4": 1}},
    "Magnezyum Sülfat": {"formul": "MgSO4.7H2O", "agirlik": 246.51, "tank": "B", "iyonlar": {"Mg": 1, "SO4": 1}},
    "Potasyum Sülfat": {"formul": "K2SO4", "agirlik": 174.26, "tank": "B", "iyonlar": {"K": 2, "SO4": 1}},
    "Amonyum Sülfat": {"formul": "(NH4)2SO4", "agirlik": 132.14, "tank": "B", "iyonlar": {"NH4": 2, "SO4": 1}},
    "Monoamonyum Fosfat": {"formul": "NH4H2PO4", "agirlik": 115.03, "tank": "B", "iyonlar": {"NH4": 1, "H2PO4": 1}}
}

# Mikro elementler
mikro_gubreler = {
    "Demir EDDHA": {"formul": "Fe-EDDHA %6", "agirlik": 435.0, "element": "Fe", "yuzde": 6},
    "Demir EDTA": {"formul": "Fe-EDTA %13", "agirlik": 346.0, "element": "Fe", "yuzde": 13},
    "Demir DTPA": {"formul": "Fe-DTPA %11", "agirlik": 468.0, "element": "Fe", "yuzde": 11},
    "Borak": {"formul": "Na2B4O7.10H2O", "agirlik": 381.37, "element": "B", "yuzde": 11},
    "Borik Asit": {"formul": "H3BO3", "agirlik": 61.83, "element": "B", "yuzde": 17.5},
    "Mangan Sülfat": {"formul": "MnSO4.H2O", "agirlik": 169.02, "element": "Mn", "yuzde": 32},
    "Çinko Sülfat": {"formul": "ZnSO4.7H2O", "agirlik": 287.56, "element": "Zn", "yuzde": 23},
    "Bakır Sülfat": {"formul": "CuSO4.5H2O", "agirlik": 249.68, "element": "Cu", "yuzde": 25},
    "Sodyum Molibdat": {"formul": "Na2MoO4.2H2O", "agirlik": 241.95, "element": "Mo", "yuzde": 40}
}

# Hazır reçeteler
hazir_receteler = {
    "Genel Amaçlı": {
        "NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0,
        "NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0,
        "Fe": 40.0, "B": 30.0, "Mn": 5.0, "Zn": 4.0, "Cu": 0.75, "Mo": 0.5
    },
    "Domates": {
        "NO3": 14.0, "H2PO4": 1.5, "SO4": 1.5,
        "NH4": 1.2, "K": 7.0, "Ca": 4.0, "Mg": 1.5,
        "Fe": 50.0, "B": 40.0, "Mn": 8.0, "Zn": 4.0, "Cu": 0.8, "Mo": 0.5
    },
    "Salatalık": {
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

# Elementin atomik kütlesi (g/mol)
element_atomik_kutle = {
    "Fe": 55.845, "B": 10.81, "Mn": 54.938, "Zn": 65.38, "Cu": 63.546, "Mo": 95.95
}

# Session state başlatma
if 'recete' not in st.session_state:
    st.session_state.recete = hazir_receteler["Genel Amaçlı"].copy()
    
if 'a_tank' not in st.session_state:
    st.session_state.a_tank = 10
    
if 'b_tank' not in st.session_state:
    st.session_state.b_tank = 10
    
if 'konsantrasyon' not in st.session_state:
    st.session_state.konsantrasyon = 100

if 'kuyu_suyu' not in st.session_state:
    st.session_state.kuyu_suyu = {
        "NO3": 0.0, "H2PO4": 0.0, "SO4": 0.0, "NH4": 0.0, "K": 0.0, "Ca": 0.0, "Mg": 0.0
    }

# Kullanılabilir gübreler için session state
if 'kullanilabilir_gubreler' not in st.session_state:
    st.session_state.kullanilabilir_gubreler = {gubre: False for gubre in gubreler.keys()}
else:
    # Yeni eklenen gübreleri kontrol et
    for gubre in gubreler.keys():
        if gubre not in st.session_state.kullanilabilir_gubreler:
            st.session_state.kullanilabilir_gubreler[gubre] = False

# Kullanılabilir mikro gübreler için session state
if 'kullanilabilir_mikro_gubreler' not in st.session_state:
    st.session_state.kullanilabilir_mikro_gubreler = {gubre: False for gubre in mikro_gubreler.keys()}
else:
    # Yeni eklenen mikro gübreleri kontrol et
    for gubre in mikro_gubreler.keys():
        if gubre not in st.session_state.kullanilabilir_mikro_gubreler:
            st.session_state.kullanilabilir_mikro_gubreler[gubre] = False

# Her mikro element için seçilen gübreyi sakla
if 'secilen_mikro_gubreler' not in st.session_state:
    st.session_state.secilen_mikro_gubreler = {
        "Fe": None, "B": None, "Mn": None, "Zn": None, "Cu": None, "Mo": None
    }

# Hesaplama geçmişi
if 'hesaplama_log' not in st.session_state:
    st.session_state.hesaplama_log = []

# İyonik denge hesaplama
def hesapla_iyonik_denge(recete):
    anyon_toplam = 0
    katyon_toplam = 0
    
    # Anyonlar
    anyon_toplam += recete["NO3"] * abs(iyon_degerlikleri["NO3"])
    anyon_toplam += recete["H2PO4"] * abs(iyon_degerlikleri["H2PO4"])
    anyon_toplam += recete["SO4"] * abs(iyon_degerlikleri["SO4"])
    
    # Katyonlar
    katyon_toplam += recete["NH4"] * abs(iyon_degerlikleri["NH4"])
    katyon_toplam += recete["K"] * abs(iyon_degerlikleri["K"])
    katyon_toplam += recete["Ca"] * abs(iyon_degerlikleri["Ca"])
    katyon_toplam += recete["Mg"] * abs(iyon_degerlikleri["Mg"])
    
    return anyon_toplam, katyon_toplam

# Simulasyon ile besinlerin karşılanıp karşılanamayacağını kontrol etme
def karsilanabilirlik_kontrolu(recete, secilen_gubreler):
    # Başlangıç ihtiyaçları
    net_ihtiyac = {
        "NO3": max(0, recete["NO3"]), "H2PO4": max(0, recete["H2PO4"]), 
        "SO4": max(0, recete["SO4"]), "NH4": max(0, recete["NH4"]),
        "K": max(0, recete["K"]), "Ca": max(0, recete["Ca"]), 
        "Mg": max(0, recete["Mg"])
    }
    
    # Temel katyonları hesapla
    if "Kalsiyum Nitrat" in secilen_gubreler and net_ihtiyac["Ca"] > 0:
        net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Ca"]
        net_ihtiyac["Ca"] = 0
    
    if "Magnezyum Nitrat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Mg"]
        net_ihtiyac["Mg"] = 0
    
    if "Magnezyum Sülfat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        net_ihtiyac["SO4"] -= net_ihtiyac["Mg"]
        net_ihtiyac["Mg"] = 0
    
    # H2PO4 öncelikli hesaplama
    if "Monoamonyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        map_miktar = net_ihtiyac["H2PO4"]
        net_ihtiyac["H2PO4"] = 0
        net_ihtiyac["NH4"] -= map_miktar
    
    if "Monopotasyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        mkp_miktar = net_ihtiyac["H2PO4"]
        net_ihtiyac["H2PO4"] = 0
        net_ihtiyac["K"] -= mkp_miktar
    
    # NH4 ve SO4 hesaplama
    if "Amonyum Sülfat" in secilen_gubreler and net_ihtiyac["NH4"] > 0 and net_ihtiyac["SO4"] > 0:
        as_miktar = min(net_ihtiyac["NH4"] / 2, net_ihtiyac["SO4"])
        net_ihtiyac["NH4"] -= 2 * as_miktar
        net_ihtiyac["SO4"] -= as_miktar
    
    # K ve NO3 hesaplama
    if "Potasyum Nitrat" in secilen_gubreler and net_ihtiyac["K"] > 0 and net_ihtiyac["NO3"] > 0:
        kn_miktar = min(net_ihtiyac["K"], net_ihtiyac["NO3"])
        net_ihtiyac["K"] -= kn_miktar
        net_ihtiyac["NO3"] -= kn_miktar
    
    # K öncelikli K2SO4 hesaplama
    if "Potasyum Sülfat" in secilen_gubreler and net_ihtiyac["K"] > 0:
        ks_miktar = net_ihtiyac["K"] / 2
        net_ihtiyac["K"] = 0
        net_ihtiyac["SO4"] -= ks_miktar
    
    # Negatif değerleri sıfıra çevir
    for iyon in net_ihtiyac:
        if net_ihtiyac[iyon] < 0:
            net_ihtiyac[iyon] = 0
    
    # Karşılanamayan besinleri bul
    eksik_besinler = [iyon for iyon, miktar in net_ihtiyac.items() if miktar > 0.1]
    return eksik_besinler

# Ana düzen
tabs = st.tabs(["Reçete Oluşturma", "Kuyu Suyu", "Gübre Seçimi", "Gübre Hesaplama"])

# Tab 1: Reçete Oluşturma
with tabs[0]:
    col1, col2 = st.columns([1, 2])
    
    # Sol sütun: Reçete seçimi ve tank ayarları
    with col1:
        st.header("Reçete ve Tank Ayarları")
        
        # Hazır reçete seçimi
        secilen_recete = st.selectbox(
            "Hazır Reçete:",
            options=list(hazir_receteler.keys())
        )
        
        if st.button("Reçeteyi Yükle"):
            st.session_state.recete = hazir_receteler[secilen_recete].copy()
            st.success(secilen_recete + " reçetesi yüklendi!")
        
        # Tank ayarları
        st.subheader("Tank Ayarları")
        
        a_tank = st.number_input("A Tankı Hacmi (litre):", 
                              min_value=1, max_value=1000, value=st.session_state.a_tank)
        st.session_state.a_tank = a_tank
        
        b_tank = st.number_input("B Tankı Hacmi (litre):", 
                              min_value=1, max_value=1000, value=st.session_state.b_tank)
        st.session_state.b_tank = b_tank
        
        konsantrasyon = st.number_input("Konsantrasyon Oranı:", 
                                     min_value=1, max_value=1000, value=st.session_state.konsantrasyon)
        st.session_state.konsantrasyon = konsantrasyon
        
        # Bilgi
        st.info("""
        **Tank Ayarları Bilgisi:**
        - **A Tankı**: Kalsiyum içeren gübreler (örn. kalsiyum nitrat) için.
        - **B Tankı**: Fosfat ve sülfat içeren gübreler için.
        - **Konsantrasyon Oranı**: Stok çözeltinin son kullanım konsantrasyonundan kaç kat daha konsantre olduğunu belirtir.
          Örneğin 100x, 100 litre su için 1 litre stok çözelti kullanılacağı anlamına gelir.
        """)
    
    # Sağ sütun: Reçete değerleri
    with col2:
        st.header("Reçete Değerleri")
        
        # Makro elementleri düzenle
        col_a, col_b = st.columns(2)
        
        # Anyon değerleri
        with col_a:
            st.subheader("Anyonlar (mmol/L)")
            
            no3 = st.number_input("NO3 (Nitrat):", 
                              value=float(st.session_state.recete["NO3"]), 
                              min_value=0.0, max_value=30.0, step=0.1, format="%.2f",
                              key="no3_input")
            st.session_state.recete["NO3"] = no3
            
            h2po4 = st.number_input("H2PO4 (Fosfat):", 
                                value=float(st.session_state.recete["H2PO4"]), 
                                min_value=0.0, max_value=10.0, step=0.1, format="%.2f",
                                key="h2po4_input")
            st.session_state.recete["H2PO4"] = h2po4
            
            so4 = st.number_input("SO4 (Sülfat):", 
                              value=float(st.session_state.recete["SO4"]), 
                              min_value=0.0, max_value=10.0, step=0.1, format="%.2f",
                              key="so4_input")
            st.session_state.recete["SO4"] = so4
        
        # Katyon değerleri
        with col_b:
            st.subheader("Katyonlar (mmol/L)")
            
            nh4 = st.number_input("NH4 (Amonyum):", 
                              value=float(st.session_state.recete["NH4"]), 
                              min_value=0.0, max_value=10.0, step=0.1, format="%.2f",
                              key="nh4_input")
            st.session_state.recete["NH4"] = nh4
            
            k = st.number_input("K (Potasyum):", 
                            value=float(st.session_state.recete["K"]), 
                            min_value=0.0, max_value=20.0, step=0.1, format="%.2f",
                            key="k_input")
            st.session_state.recete["K"] = k
            
            ca = st.number_input("Ca (Kalsiyum):", 
                             value=float(st.session_state.recete["Ca"]), 
                             min_value=0.0, max_value=15.0, step=0.1, format="%.2f",
                             key="ca_input")
            st.session_state.recete["Ca"] = ca
            
            mg = st.number_input("Mg (Magnezyum):", 
                             value=float(st.session_state.recete["Mg"]), 
                             min_value=0.0, max_value=10.0, step=0.1, format="%.2f",
                             key="mg_input")
            st.session_state.recete["Mg"] = mg
        
        # Mikro besinler
        st.subheader("Mikro Besinler (mikromol/L)")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            fe = st.number_input("Fe (Demir):", 
                             value=float(st.session_state.recete.get("Fe", 40.0)), 
                             min_value=0.0, max_value=100.0, step=1.0, format="%.1f",
                             key="fe_input")
            st.session_state.recete["Fe"] = fe
            
            mn = st.number_input("Mn (Mangan):", 
                             value=float(st.session_state.recete.get("Mn", 5.0)), 
                             min_value=0.0, max_value=50.0, step=0.5, format="%.1f",
                             key="mn_input")
            st.session_state.recete["Mn"] = mn
        
        with col_m2:
            b = st.number_input("B (Bor):", 
                            value=float(st.session_state.recete.get("B", 30.0)), 
                            min_value=0.0, max_value=100.0, step=1.0, format="%.1f",
                            key="b_input")
            st.session_state.recete["B"] = b
            
            zn = st.number_input("Zn (Çinko):", 
                             value=float(st.session_state.recete.get("Zn", 4.0)), 
                             min_value=0.0, max_value=50.0, step=0.5, format="%.1f",
                             key="zn_input")
            st.session_state.recete["Zn"] = zn
        
        with col_m3:
            cu = st.number_input("Cu (Bakır):", 
                             value=float(st.session_state.recete.get("Cu", 0.75)), 
                             min_value=0.0, max_value=10.0, step=0.05, format="%.2f",
                             key="cu_input")
            st.session_state.recete["Cu"] = cu
            
            mo = st.number_input("Mo (Molibden):", 
                             value=float(st.session_state.recete.get("Mo", 0.5)), 
                             min_value=0.0, max_value=10.0, step=0.05, format="%.2f",
                             key="mo_input")
            st.session_state.recete["Mo"] = mo
        
        # İyonik denge hesaplaması
        st.subheader("İyonik Denge")
        
        anyon_toplam, katyon_toplam = hesapla_iyonik_denge(st.session_state.recete)
        
        col_denge1, col_denge2 = st.columns(2)
        
        # Anyonlar tablosu
        with col_denge1:
            anyon_data = []
            for anyon, deger in [("NO3", st.session_state.recete["NO3"]), 
                                ("H2PO4", st.session_state.recete["H2PO4"]), 
                                ("SO4", st.session_state.recete["SO4"])]:
                me = deger * abs(iyon_degerlikleri[anyon])
                anyon_data.append([anyon, float(deger), float(me)])
            
            anyon_df = pd.DataFrame(anyon_data, columns=["Anyon", "mmol/L", "me/L"])
            st.write("**Anyonlar:**")
            st.dataframe(anyon_df.style.format({"mmol/L": "{:.2f}", "me/L": "{:.2f}"}))
            st.write("**Toplam:** " + str(round(anyon_toplam, 2)) + " me/L")
        
        # Katyonlar tablosu
        with col_denge2:
            katyon_data = []
            for katyon, deger in [("NH4", st.session_state.recete["NH4"]), 
                                ("K", st.session_state.recete["K"]), 
                                ("Ca", st.session_state.recete["Ca"]), 
                                ("Mg", st.session_state.recete["Mg"])]:
                me = deger * abs(iyon_degerlikleri[katyon])
                katyon_data.append([katyon, float(deger), float(me)])
            
            katyon_df = pd.DataFrame(katyon_data, columns=["Katyon", "mmol/L", "me/L"])
            st.write("**Katyonlar:**")
            st.dataframe(katyon_df.style.format({"mmol/L": "{:.2f}", "me/L": "{:.2f}"}))
            st.write("**Toplam:** " + str(round(katyon_toplam, 2)) + " me/L")
        
        # Denge kontrolü
        fark = abs(anyon_toplam - katyon_toplam)
        if fark < 0.5:
            st.success("✅ İyonik denge iyi durumda! (Fark: " + str(round(fark, 2)) + " me/L)")
        elif fark < 1.0:
            st.warning("⚠️ İyonik denge kabul edilebilir sınırda. (Fark: " + str(round(fark, 2)) + " me/L)")
        else:
            st.error("❌ İyonik denge bozuk! (Fark: " + str(round(fark, 2)) + " me/L)")
            
            if anyon_toplam > katyon_toplam:
                st.markdown("**İyileştirme Önerisi:** Anyon fazlası var. Daha fazla katyon (K, Ca, Mg, NH4) ekleyebilirsiniz.")
            else:
                st.markdown("**İyileştirme Önerisi:** Katyon fazlası var. Daha fazla anyon (NO3, H2PO4, SO4) ekleyebilirsiniz.")

# Tab 2: Kuyu Suyu
with tabs[1]:
    st.header("Kuyu Suyu Analizi")
    
    st.info("Kuyu suyu kullanıyorsanız, içindeki iyonları buraya girerek hesaplamada dikkate alınmasını sağlayabilirsiniz.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Anyonlar (mmol/L)")
        
        kuyu_no3 = st.number_input("NO3 (Nitrat):", 
                                value=float(st.session_state.kuyu_suyu.get("NO3", 0.0)), 
                                min_value=0.0, max_value=10.0, step=0.1, format="%.2f",
                                key="kuyu_no3_input")
        st.session_state.kuyu_suyu["NO3"] = kuyu_no3
        
        kuyu_h2po4 = st.number_input("H2PO4 (Fosfat):", 
                                  value=float(st.session_state.kuyu_suyu.get("H2PO4", 0.0)), 
                                  min_value=0.0, max_value=5.0, step=0.05, format="%.2f",
                                  key="kuyu_h2po4_input")
        st.session_state.kuyu_suyu["H2PO4"] = kuyu_h2po4
        
        kuyu_so4 = st.number_input("SO4 (Sülfat):", 
                               value=float(st.session_state.kuyu_suyu.get("SO4", 0.0)), 
                               min_value=0.0, max_value=5.0, step=0.05, format="%.2f",
                               key="kuyu_so4_input")
        st.session_state.kuyu_suyu["SO4"] = kuyu_so4
    
    with col2:
        st.subheader("Katyonlar (mmol/L)")
        
        kuyu_nh4 = st.number_input("NH4 (Amonyum):", 
                               value=float(st.session_state.kuyu_suyu.get("NH4", 0.0)), 
                               min_value=0.0, max_value=5.0, step=0.05, format="%.2f",
                               key="kuyu_nh4_input")
        st.session_state.kuyu_suyu["NH4"] = kuyu_nh4
        
        kuyu_k = st.number_input("K (Potasyum):", 
                             value=float(st.session_state.kuyu_suyu.get("K", 0.0)), 
                             min_value=0.0, max_value=5.0, step=0.05, format="%.2f",
                             key="kuyu_k_input")
        st.session_state.kuyu_suyu["K"] = kuyu_k
        
        kuyu_ca = st.number_input("Ca (Kalsiyum):", 
                              value=float(st.session_state.kuyu_suyu.get("Ca", 0.0)), 
                              min_value=0.0, max_value=10.0, step=0.1, format="%.2f",
                              key="kuyu_ca_input")
        st.session_state.kuyu_suyu["Ca"] = kuyu_ca
        
        kuyu_mg = st.number_input("Mg (Magnezyum):", 
                              value=float(st.session_state.kuyu_suyu.get("Mg", 0.0)), 
                              min_value=0.0, max_value=5.0, step=0.05, format="%.2f",
                              key="kuyu_mg_input")
        st.session_state.kuyu_suyu["Mg"] = kuyu_mg
    
    if sum(st.session_state.kuyu_suyu.values()) > 0:
        st.success("✅ Kuyu suyu değerleri kaydedildi ve gübre hesaplamalarında dikkate alınacak.")
    else:
        st.info("ℹ️ Şu anda herhangi bir kuyu suyu değeri girilmemiş. Saf su kullanıldığı varsayılacak.")

# Tab 3: Gübre Seçimi
with tabs[2]:
    st.header("Elimdeki Gübreler")
    st.info("Elinizde bulunan gübreleri seçiniz. Hesaplamalar sadece seçtiğiniz gübreler kullanılarak yapılacaktır.")
    
    col1, col2 = st.columns(2)
    
    # Makro gübreler seçimi
    with col1:
        st.subheader("Makro Gübreler")
        
        a_tank_gubreler = []
        b_tank_gubreler = []
        
        for gubre, bilgi in gubreler.items():
            if bilgi["tank"] == "A":
                a_tank_gubreler.append(gubre)
            else:
                b_tank_gubreler.append(gubre)
        
        st.markdown("**A Tankı Gübreleri**")
        for gubre in a_tank_gubreler:
            st.session_state.kullanilabilir_gubreler[gubre] = st.checkbox(
                "☐ " + gubre + " (" + gubreler[gubre]['formul'] + ")",
                value=st.session_state.kullanilabilir_gubreler[gubre],
                key="checkbox_" + gubre
            )
        
        st.markdown("**B Tankı Gübreleri**")
        for gubre in b_tank_gubreler:
            st.session_state.kullanilabilir_gubreler[gubre] = st.checkbox(
                "☐ " + gubre + " (" + gubreler[gubre]['formul'] + ")",
                value=st.session_state.kullanilabilir_gubreler[gubre],
                key="checkbox_b_" + gubre
            )
    
    # Mikro gübreler seçimi
    with col2:
        st.subheader("Mikro Gübreler")
        
        # Mikro element grupları
        mikro_element_gruplari = {}
        for gubre, bilgi in mikro_gubreler.items():
            element = bilgi["element"]
            if element not in mikro_element_gruplari:
                mikro_element_gruplari[element] = []
            mikro_element_gruplari[element].append(gubre)
        
        # Her element için tek bir seçim yapılması
        for element, gubreleri in mikro_element_gruplari.items():
            st.markdown("**" + element + " Kaynakları**")
            secilen_gubre = st.radio(
                element + " için gübre seçimi",
                options=["Seçilmedi"] + gubreleri,
                index=0,
                key="radio_" + element
            )
            
            # Seçimi kaydet
            if secilen_gubre != "Seçilmedi":
                st.session_state.secilen_mikro_gubreler[element] = secilen_gubre
                # Ayrıca kullanılabilir gübreler listesini güncelle
                for gubre in gubreleri:
                    st.session_state.kullanilabilir_mikro_gubreler[gubre] = (gubre == secilen_gubre)
            else:
                st.session_state.secilen_mikro_gubreler[element] = None
                # Eğer seçilmediyse, tüm ilgili gübreleri kapatın
                for gubre in gubreleri:
                    st.session_state.kullanilabilir_mikro_gubreler[gubre] = False
    
    # Gübre seçimini göster
    secilen_gubreler = [gubre for gubre, secildi in st.session_state.kullanilabilir_gubreler.items() if secildi]
    secilen_mikro_gubreler = [gubre for element, gubre in st.session_state.secilen_mikro_gubreler.items() if gubre is not None]
    
    st.subheader("Seçilen Gübreler")
    if secilen_gubreler:
        st.write("**Makro Gübreler:**")
        for gubre in secilen_gubreler:
            st.write("✓ " + gubre + " (" + gubreler[gubre]['formul'] + ")")
    else:
        st.warning("Henüz makro gübre seçmediniz!")
    
    if secilen_mikro_gubreler:
        st.write("**Mikro Gübreler:**")
        for gubre in secilen_mikro_gubreler:
            st.write("✓ " + gubre + " (" + mikro_gubreler[gubre]['formul'] + ")")
    else:
        st.warning("Henüz mikro gübre seçmediniz!")
    
    # DÜZELTİLMİŞ: Gübre Seçimi kontrol algoritması
    if secilen_gubreler:
        # Simulasyon ile eksik besinleri belirle
        eksik_besinler = karsilanabilirlik_kontrolu(st.session_state.recete, secilen_gubreler)
        
        if eksik_besinler:
            st.error("⚠️ Seçilen gübrelerle karşılanamayacak besinler: " + ", ".join(eksik_besinler))
            st.markdown("Önerilen gübreler:")
            for besin in eksik_besinler:
                oneriler = []
                for gubre, bilgi in gubreler.items():
                    if besin in bilgi["iyonlar"] and gubre not in secilen_gubreler:
                        oneriler.append("☐ " + gubre)
                if oneriler:
                    st.markdown("- " + besin + " için: " + ", ".join(oneriler))
                else:
                    st.markdown("- " + besin + " için: Önerilen gübre bulunamadı. Reçeteyi gözden geçirin.")
        else:
            st.success("✅ Seçilen gübrelerle tüm besinler karşılanabilir.")

# Tab 4: Gübre Hesaplama
with tabs[3]:
    st.header("Gübre Hesaplama")
    
    if st.button("Gübre Hesapla", type="primary"):
        secilen_gubreler = [gubre for gubre, secildi in st.session_state.kullanilabilir_gubreler.items() if secildi]
        secilen_mikro_gubreler = [gubre for element, gubre in st.session_state.secilen_mikro_gubreler.items() if gubre is not None]
        
        if not secilen_gubreler:
            st.error("Lütfen önce 'Gübre Seçimi' sekmesinden en az bir makro gübre seçiniz!")
        else:
            # Hesaplama log'u sıfırla
            st.session_state.hesaplama_log = []
            
            # Reçete ihtiyaçlarını hazırla (kuyu suyu değerlerini çıkar)
            net_ihtiyac = {
                "NO3": max(0, st.session_state.recete["NO3"] - st.session_state.kuyu_suyu["NO3"]),
                "H2PO4": max(0, st.session_state.recete["H2PO4"] - st.session_state.kuyu_suyu["H2PO4"]),
                "SO4": max(0, st.session_state.recete["SO4"] - st.session_state.kuyu_suyu["SO4"]),
                "NH4": max(0, st.session_state.recete["NH4"] - st.session_state.kuyu_suyu["NH4"]),
                "K": max(0, st.session_state.recete["K"] - st.session_state.kuyu_suyu["K"]),
                "Ca": max(0, st.session_state.recete["Ca"] - st.session_state.kuyu_suyu["Ca"]),
                "Mg": max(0, st.session_state.recete["Mg"] - st.session_state.kuyu_suyu["Mg"])
            }
            
            # Tank gübre miktarları
            a_tank_gubreler = {}
            b_tank_gubreler = {}
            
            # Aşamalı gübre hesaplaması - log tutarak
            adim = 1
            
            # Başlangıç durumunu kaydet
            st.session_state.hesaplama_log.append({
                "adim": "Başlangıç",
                "aciklama": "Kuyu suyu çıkarıldıktan sonraki ihtiyaçlar",
                "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
            })
            
            # 1. Ca ve Mg ihtiyaçlarını karşıla (temel katyonlar)
            if "Kalsiyum Nitrat" in secilen_gubreler and net_ihtiyac["Ca"] > 0:
                ca_miktar = net_ihtiyac["Ca"]
                a_tank_gubreler["Kalsiyum Nitrat"] = ca_miktar
                net_ihtiyac["Ca"] = 0
                net_ihtiyac["NO3"] -= 2 * ca_miktar
                
                st.session_state.hesaplama_log.append({
                    "adim": "Adım " + str(adim),
                    "aciklama": "Kalsiyum Nitrat eklendi: " + str(round(ca_miktar, 2)) + " mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1
            
            if "Magnezyum Sülfat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
                mg_miktar = net_ihtiyac["Mg"]
                b_tank_gubreler["Magnezyum Sülfat"] = mg_miktar
                net_ihtiyac["Mg"] = 0
                net_ihtiyac["SO4"] -= mg_miktar
                
                st.session_state.hesaplama_log.append({
                    "adim": "Adım " + str(adim),
                    "aciklama": "Magnezyum Sülfat eklendi: " + str(round(mg_miktar, 2)) + " mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1
            
            if "Magnezyum Nitrat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
                mg_miktar = net_ihtiyac["Mg"]
                a_tank_gubreler["Magnezyum Nitrat"] = mg_miktar
                net_ihtiyac["Mg"] = 0
                net_ihtiyac["NO3"] -= 2 * mg_miktar
                
                st.session_state.hesaplama_log.append({
                    "adim": "Adım " + str(adim),
                    "aciklama": "Magnezyum Nitrat eklendi: " + str(round(mg_miktar, 2)) + " mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1
            
            # 2. Fosfat ihtiyacını karşıla - DÜZELTİLMİŞ: H2PO4 öncelikli
            if "Monoamonyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
                # Tüm H2PO4 ihtiyacını karşıla
                map_miktar = net_ihtiyac["H2PO4"]
                b_tank_gubreler["Monoamonyum Fosfat"] = map_miktar
                net_ihtiyac["H2PO4"] = 0
                net_ihtiyac["NH4"] -= map_miktar
                
                st.session_state.hesaplama_log.append({
                    "adim": "Adım " + str(adim),
                    "aciklama": "Monoamonyum Fosfat eklendi: " + str(round(map_miktar, 2)) + " mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1
            
            if "Monopotasyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
                # Tüm H2PO4 ihtiyacını karşıla
                mkp_miktar = net_ihtiyac["H2PO4"]
                b_tank_gubreler["Monopotasyum Fosfat"] = mkp_miktar
                net_ihtiyac["H2PO4"] = 0
                net_ihtiyac["K"] -= mkp_miktar
                
                st.session_state.hesaplama_log.append({
                    "adim": "Adım " + str(adim),
                    "aciklama": "Monopotasyum Fosfat eklendi: " + str(round(mkp_miktar, 2)) + " mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1
            
            # 3. Kalan NH4 ihtiyacını karşıla
            if "Amonyum Sülfat" in secilen_gubreler and net_ihtiyac["NH4"] > 0 and net_ihtiyac["SO4"] > 0:
                as_miktar = min(net_ihtiyac["NH4"] / 2, net_ihtiyac["SO4"])
                if as_miktar > 0:
                    b_tank_gubreler["Amonyum Sülfat"] = as_miktar
                    net_ihtiyac["NH4"] -= 2 * as_miktar
                    net_ihtiyac["SO4"] -= as_miktar
                    
                    st.session_state.hesaplama_log.append({
                        "adim": "Adım " + str(adim),
                        "aciklama": "Amonyum Sülfat eklendi: " + str(round(as_miktar, 2)) + " mmol/L",
                        "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                    })
                    adim += 1
            
            # 4. Kalan K ve NO3 ihtiyacını karşıla
            if "Potasyum Nitrat" in secilen_gubreler and net_ihtiyac["K"] > 0 and net_ihtiyac["NO3"] > 0:
                kn_miktar = min(net_ihtiyac["K"], net_ihtiyac["NO3"])
                if kn_miktar > 0:
                    a_tank_gubreler["Potasyum Nitrat"] = kn_miktar
                    net_ihtiyac["K"] -= kn_miktar
                    net_ihtiyac["NO3"] -= kn_miktar
                    
                    st.session_state.hesaplama_log.append({
                        "adim": "Adım " + str(adim),
                        "aciklama": "Potasyum Nitrat eklendi: " + str(round(kn_miktar, 2)) + " mmol/L",
                        "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                    })
                    adim += 1
            
            # 5. Kalan K ve SO4 ihtiyacını karşıla - DÜZELTİLMİŞ: K öncelikli
            if "Potasyum Sülfat" in secilen_gubreler and net_ihtiyac["K"] > 0:
                # K öncelikli, tüm K ihtiyacını karşıla
                ks_miktar = net_ihtiyac["K"] / 2  # Her K2SO4 için 2 K
                if ks_miktar > 0:
                    b_tank_gubreler["Potasyum Sülfat"] = ks_miktar
                    net_ihtiyac["K"] = 0
                    net_ihtiyac["SO4"] -= ks_miktar
                    
                    st.session_state.hesaplama_log.append({
                        "adim": "Adım " + str(adim),
                        "aciklama": "Potasyum Sülfat eklendi: " + str(round(ks_miktar, 2)) + " mmol/L",
                        "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                    })
                    adim += 1
            
            # 6. Negatif değerlere karşı kontrol
            negatif_ihtiyaclar = [iyon for iyon, miktar in net_ihtiyac.items() if miktar < -0.1]
            
            # Mikro besin elementleri için gübre hesaplama
            mikro_sonuc = []
            
            for element, bilgi in [
                ("Fe", "Demir"), 
                ("B", "Bor"), 
                ("Mn", "Mangan"), 
                ("Zn", "Çinko"), 
                ("Cu", "Bakır"), 
                ("Mo", "Molibden")
            ]:
                secilen_gubre = st.session_state.secilen_mikro_gubreler[element]
                
                if secilen_gubre and element in st.session_state.recete and st.session_state.recete[element] > 0:
                    mikromol = st.session_state.recete[element]
                    gubre_bilgi = mikro_gubreler[secilen_gubre]
                    mmol = mikromol / 1000  # mikromol -> mmol
                    
                    # Saf element için hesaplama
                    element_mol_agirligi = element_atomik_kutle[element] * (100 / gubre_bilgi["yuzde"])
                    
                    # mg ve g hesapla
                    mg_l = mmol * element_mol_agirligi
                    g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.b_tank) / 1000
                    
                    mikro_sonuc.append([secilen_gubre, gubre_bilgi["formul"], float(mikromol), float(mg_l), float(g_tank)])
            
            # Sonuçları hesaplama
            a_tank_sonuc = []
            a_tank_toplam = 0
            
            for gubre, mmol in a_tank_gubreler.items():
                formul = gubreler[gubre]["formul"]
                mg_l = mmol * gubreler[gubre]["agirlik"]
                g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.a_tank) / 1000
                kg_tank = g_tank / 1000  # g -> kg
                a_tank_toplam += g_tank
                
                a_tank_sonuc.append([gubre, formul, float(mmol), float(mg_l), float(kg_tank)])
            
            b_tank_sonuc = []
            b_tank_toplam = 0
            
            for gubre, mmol in b_tank_gubreler.items():
                formul = gubreler[gubre]["formul"]
                mg_l = mmol * gubreler[gubre]["agirlik"]
                g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.b_tank) / 1000
                kg_tank = g_tank / 1000  # g -> kg
                b_tank_toplam += g_tank
                
                b_tank_sonuc.append([gubre, formul, float(mmol), float(mg_l), float(kg_tank)])
            
            # Sonuçları gösterme
            col_sonuc1, col_sonuc2 = st.columns(2)
            
            with col_sonuc1:
                st.subheader("A Tankı (Kalsiyum içeren)")
                
                if a_tank_sonuc:
                    a_tank_df = pd.DataFrame(a_tank_sonuc, 
                                          columns=["Gübre Adı", "Formül", "mmol/L", "mg/L", "kg/Tank"])
                    st.dataframe(a_tank_df.style.format({
                        "mmol/L": "{:.2f}", 
                        "mg/L": "{:.2f}", 
                        "kg/Tank": "{:.3f}"
                    }))
                    st.write("**Toplam A Tankı gübresi:** " + str(round(a_tank_toplam/1000, 3)) + " kg")
                else:
                    st.info("A Tankı için gübre eklenmedi.")
            
            with col_sonuc2:
                st.subheader("B Tankı (Fosfat, Sülfat ve Amonyum)")
                
                if b_tank_sonuc:
                    b_tank_df = pd.DataFrame(b_tank_sonuc, 
                                         columns=["Gübre Adı", "Formül", "mmol/L", "mg/L", "kg/Tank"])
                    st.dataframe(b_tank_df.style.format({
                        "mmol/L": "{:.2f}", 
                        "mg/L": "{:.2f}", 
                        "kg/Tank": "{:.3f}"
                    }))
                    st.write("**Toplam B Tankı gübresi:** " + str(round(b_tank_toplam/1000, 3)) + " kg")
                else:
                    st.info("B Tankı için gübre eklenmedi.")
            
            # Mikro besinleri göster
            st.subheader("Mikro Besin Elementleri")
            
            if mikro_sonuc:
                mikro_df = pd.DataFrame(mikro_sonuc, 
                                     columns=["Gübre Adı", "Formül", "mikromol/L", "mg/L", "gram/Tank"])
                st.dataframe(mikro_df.style.format({
                    "mikromol/L": "{:.2f}", 
                    "mg/L": "{:.4f}", 
                    "gram/Tank": "{:.2f}"
                }))
                mikro_toplam = sum(sonuc[4] for sonuc in mikro_sonuc)
                st.write("**Toplam mikro besin gübresi:** " + str(round(mikro_toplam, 2)) + " gram")
            else:
                st.info("Mikro besin elementi eklenmedi veya seçilen gübrelerle karşılanamadı.")
            
            # Kuyu suyu kullanımı uyarısı
            if any(st.session_state.kuyu_suyu.values()):
                st.success("✅ Kuyu suyu analiziniz hesaplamada dikkate alındı.")
            
            # Negatif ihtiyaç uyarıları
            if negatif_ihtiyaclar:
                st.warning("⚠️ Dikkat! Aşağıdaki besinler reçete ihtiyacından fazla eklendi:")
                for iyon in negatif_ihtiyaclar:
                    st.markdown("- " + iyon + ": " + str(round(-net_ihtiyac[iyon], 2)) + " mmol/L fazla")
                st.markdown("Bu durum bitki sağlığını olumsuz etkileyebilir veya EC değerini gereksiz yükseltebilir.")
            
            # Karşılanamayan besinleri gösterme
            st.subheader("Denge Kontrol")
            
            eksik_var = False
            uyari = ""
            
            # Kalan ihtiyaçları kontrol et (negatif değerleri sıfır olarak kabul et)
            for iyon, miktar in net_ihtiyac.items():
                if miktar > 0.1:  # 0.1 mmol/L'den büyük eksikler önemli
                    eksik_var = True
                    uyari += " " + iyon + ": " + str(round(miktar, 2)) + " mmol/L,"
            
            if eksik_var:
                st.warning("⚠️ Seçilen gübrelerle karşılanamayan besinler:" + uyari[:-1])
                st.markdown("**Önerilen Ek Gübreler:**")
                
                # Her eksik besin için öneriler
                for iyon, miktar in net_ihtiyac.items():
                    if miktar > 0.1:
                        oneriler = []
                        for gubre, bilgi in gubreler.items():
                            if iyon in bilgi["iyonlar"] and gubre not in secilen_gubreler:
                                oneriler.append("☐ " + gubre + " (" + bilgi['formul'] + ")")
                        
                        if oneriler:
                            st.markdown("- " + iyon + " için: " + ", ".join(oneriler))
                        else:
                            st.markdown("- " + iyon + " için: Reçeteyi gözden geçirin.")
            else:
                st.success("✅ Tüm besinler seçilen gübrelerle karşılandı.")
            
            # Hesaplama adımlarını göster
            with st.expander("Hesaplama Adımları"):
                for log in st.session_state.hesaplama_log:
                    st.write("**" + log['adim'] + ":** " + log['aciklama'])
                    
                    # İhtiyaçları tablo olarak göster
                    ihtiyac_data = []
                    for iyon, miktar in log["ihtiyac"].items():
                        ihtiyac_data.append([iyon, miktar])
                    
                    ihtiyac_df = pd.DataFrame(ihtiyac_data, columns=["İyon", "İhtiyaç (mmol/L)"])
                    st.dataframe(ihtiyac_df.style.format({"İhtiyaç (mmol/L)": "{:.2f}"}))
                    st.markdown("---")

# Alt bilgi
st.markdown("---")
st.markdown("HydroBuddy Türkçe | Hidroponik besin çözeltisi hesaplama aracı")
