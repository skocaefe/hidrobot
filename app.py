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
    "HNO3": {"formul": "HNO3", "besin_icerigi": "22N", "formul_agirligi": 63.01, 
             "anyonlar": {"NO3": 1}, "katyonlar": {}, "asit": True},
    "H3PO4": {"formul": "H3PO4", "besin_icerigi": "32P", "formul_agirligi": 97.99, 
              "anyonlar": {"H2PO4": 1}, "katyonlar": {}, "asit": True},
    "Ca(NO3)2.4H2O": {"formul": "Ca(NO3)2.4H2O", "besin_icerigi": "16.9Ca, 11.9N", "formul_agirligi": 236.15, 
                      "anyonlar": {"NO3": 2}, "katyonlar": {"Ca": 1}, "a_tank": True},
    "KNO3": {"formul": "KNO3", "besin_icerigi": "38K, 13N", "formul_agirligi": 101.10, 
             "anyonlar": {"NO3": 1}, "katyonlar": {"K": 1}},
    "(NH4)2SO4": {"formul": "(NH4)2SO4", "besin_icerigi": "21.2N", "formul_agirligi": 132.14, 
                  "anyonlar": {"SO4": 1}, "katyonlar": {"NH4": 2}},
    "Mg(NO3)2.6H2O": {"formul": "Mg(NO3)2.6H2O", "besin_icerigi": "9Mg, 11N", "formul_agirligi": 256.41, 
                      "anyonlar": {"NO3": 2}, "katyonlar": {"Mg": 1}},
    "KH2PO4": {"formul": "KH2PO4", "besin_icerigi": "28K, 23P", "formul_agirligi": 136.09, 
               "anyonlar": {"H2PO4": 1}, "katyonlar": {"K": 1}, "b_tank": True},
    "NH4H2PO4": {"formul": "NH4H2PO4", "besin_icerigi": "27P, 12N", "formul_agirligi": 115.03, 
                 "anyonlar": {"H2PO4": 1}, "katyonlar": {"NH4": 1}, "b_tank": True},
    "K2SO4": {"formul": "K2SO4", "besin_icerigi": "45K, 18S", "formul_agirligi": 174.26, 
              "anyonlar": {"SO4": 1}, "katyonlar": {"K": 2}},
    "MgSO4.7H2O": {"formul": "MgSO4.7H2O", "besin_icerigi": "10Mg, 13S", "formul_agirligi": 246.51, 
                   "anyonlar": {"SO4": 1}, "katyonlar": {"Mg": 1}},
    "NH4NO3": {"formul": "NH4NO3", "besin_icerigi": "34N", "formul_agirligi": 80.04, 
               "anyonlar": {"NO3": 1}, "katyonlar": {"NH4": 1}},
    "KHCO3": {"formul": "KHCO3", "besin_icerigi": "39K", "formul_agirligi": 100.12, 
              "anyonlar": {"HCO3": 1}, "katyonlar": {"K": 1}},
    "Ca(OH)2": {"formul": "Ca(OH)2", "besin_icerigi": "54Ca", "formul_agirligi": 74.09, 
                "anyonlar": {"OH": 2}, "katyonlar": {"Ca": 1}, "a_tank": True}
}

# Mikro besin veritabanı
mikro_besin_veritabani = {
    "Fe-EDDHA": {"formul": "Fe-EDDHA", "besin_icerigi": "5Fe", "formul_agirligi": 435, "element": "Fe"},
    "Na2B4O7.10H2O": {"formul": "Na2B4O7.10H2O", "besin_icerigi": "11B", "formul_agirligi": 381.37, "element": "B"},
    "MnSO4.H2O": {"formul": "MnSO4.H2O", "besin_icerigi": "32Mn", "formul_agirligi": 169.02, "element": "Mn"},
    "ZnSO4.7H2O": {"formul": "ZnSO4.7H2O", "besin_icerigi": "23Zn", "formul_agirligi": 287.56, "element": "Zn"},
    "CuSO4.5H2O": {"formul": "CuSO4.5H2O", "besin_icerigi": "25Cu", "formul_agirligi": 249.68, "element": "Cu"},
    "Na2MoO4.2H2O": {"formul": "Na2MoO4.2H2O", "besin_icerigi": "40Mo", "formul_agirligi": 241.95, "element": "Mo"}
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
    "NO3": -1, "H2PO4": -1, "SO4": -2, "HCO3": -1, "OH": -1,
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

if 'gubre_secimi' not in st.session_state:
    st.session_state.gubre_secimi = {}

if 'sonuclar' not in st.session_state:
    st.session_state.sonuclar = {}

# Ana sekmeleri oluştur
tab1, tab2, tab3 = st.tabs(["Reçete Seçimi", "İyonik Denge ve Gübre Seçimi", "Sonuçlar ve Tavsiyeler"])

# Sekmeler
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

with tab2:
    st.header("İyonik Denge ve Gübre Seçimi")
    
    # Üst kısım: İyonik denge tablosu
    st.subheader("Anyon-Katyon Dengesi")
    
    # İyonik denge tablosu
    anyon_data = []
    for anyon in ["NO3", "H2PO4", "SO4"]:
        deger = st.session_state.recete_secimleri[anyon]
        valens = abs(iyon_degerlikleri[anyon])
        me = deger * valens
        anyon_data.append([anyon, f"{deger:.2f}", f"{me:.2f}"])
    
    anyon_df = pd.DataFrame(anyon_data, columns=["Anyon", "mmol/L", "me/L"])
    
    katyon_data = []
    for katyon in ["NH4", "K", "Ca", "Mg"]:
        deger = st.session_state.recete_secimleri[katyon]
        valens = abs(iyon_degerlikleri[katyon])
        me = deger * valens
        katyon_data.append([katyon, f"{deger:.2f}", f"{me:.2f}"])
    
    katyon_df = pd.DataFrame(katyon_data, columns=["Katyon", "mmol/L", "me/L"])
    
    # İki tabloyu yan yana göster
    col_tablo1, col_tablo2 = st.columns(2)
    
    with col_tablo1:
        st.table(anyon_df)
        anyon_toplam_mmol = sum(st.session_state.recete_secimleri[a] for a in ["NO3", "H2PO4", "SO4"])
        anyon_toplam_me = sum(st.session_state.recete_secimleri[a] * abs(iyon_degerlikleri[a]) for a in ["NO3", "H2PO4", "SO4"])
        st.write(f"**Toplam:** {anyon_toplam_mmol:.2f} mmol/L | {anyon_toplam_me:.2f} me/L")
    
    with col_tablo2:
        st.table(katyon_df)
        katyon_toplam_mmol = sum(st.session_state.recete_secimleri[k] for k in ["NH4", "K", "Ca", "Mg"])
        katyon_toplam_me = sum(st.session_state.recete_secimleri[k] * abs(iyon_degerlikleri[k]) for k in ["NH4", "K", "Ca", "Mg"])
        st.write(f"**Toplam:** {katyon_toplam_mmol:.2f} mmol/L | {katyon_toplam_me:.2f} me/L")
    
    # Alt kısım: Gübre seçimi
    st.subheader("Gübre Seçimi")
    
    # Gübre seçimi yöntemi
    secim_yontemi = st.radio(
        "Gübre seçim yöntemi:",
        ["Otomatik Gübre Seçimi", "Manuel Gübre Seçimi"]
    )
    
    if secim_yontemi == "Otomatik Gübre Seçimi":
        if st.button("Otomatik Gübre Seçimi Yap"):
            # Otomatik gübre seçimi algoritması
            
            # Seçilen gübreler ve miktarları
            secilen_gubreler = {}
            
            # 1. Kalsiyum Nitrat (A tankı için)
            if st.session_state.recete_secimleri["Ca"] > 0:
                secilen_gubreler["Ca(NO3)2.4H2O"] = st.session_state.recete_secimleri["Ca"]
                kalan_nitrat = st.session_state.recete_secimleri["NO3"] - (2 * st.session_state.recete_secimleri["Ca"])
            else:
                kalan_nitrat = st.session_state.recete_secimleri["NO3"]
            
            # 2. Monopotasyum Fosfat (B tankı için)
            if st.session_state.recete_secimleri["H2PO4"] > 0:
                secilen_gubreler["KH2PO4"] = st.session_state.recete_secimleri["H2PO4"]
                kalan_k = st.session_state.recete_secimleri["K"] - st.session_state.recete_secimleri["H2PO4"]
            else:
                kalan_k = st.session_state.recete_secimleri["K"]
            
            # 3. Magnezyum Sülfat
            if st.session_state.recete_secimleri["Mg"] > 0:
                secilen_gubreler["MgSO4.7H2O"] = st.session_state.recete_secimleri["Mg"]
                kalan_sulfat = st.session_state.recete_secimleri["SO4"] - st.session_state.recete_secimleri["Mg"]
            else:
                kalan_sulfat = st.session_state.recete_secimleri["SO4"]
            
            # 4. Amonyum Nitrat
            if st.session_state.recete_secimleri["NH4"] > 0:
                kullanilacak_nh4no3 = min(st.session_state.recete_secimleri["NH4"], kalan_nitrat)
                if kullanilacak_nh4no3 > 0:
                    secilen_gubreler["NH4NO3"] = kullanilacak_nh4no3
                    kalan_nitrat -= kullanilacak_nh4no3
                    kalan_nh4 = st.session_state.recete_secimleri["NH4"] - kullanilacak_nh4no3
                else:
                    kalan_nh4 = st.session_state.recete_secimleri["NH4"]
            else:
                kalan_nh4 = 0
            
            # 5. Potasyum Nitrat
            if kalan_k > 0 and kalan_nitrat > 0:
                kullanilacak_kno3 = min(kalan_k, kalan_nitrat)
                if kullanilacak_kno3 > 0:
                    secilen_gubreler["KNO3"] = kullanilacak_kno3
                    kalan_nitrat -= kullanilacak_kno3
                    kalan_k -= kullanilacak_kno3
            
            # 6. Potasyum Sülfat (kalan K için)
            if kalan_k > 0 and kalan_sulfat > 0:
                kullanilacak_k2so4 = min(kalan_k / 2, kalan_sulfat)
                if kullanilacak_k2so4 > 0:
                    secilen_gubreler["K2SO4"] = kullanilacak_k2so4
                    kalan_sulfat -= kullanilacak_k2so4
                    kalan_k -= (2 * kullanilacak_k2so4)
            
            # 7. Amonyum Sülfat (kalan NH4 için)
            if kalan_nh4 > 0 and kalan_sulfat > 0:
                kullanilacak_nh42so4 = min(kalan_nh4 / 2, kalan_sulfat)
                if kullanilacak_nh42so4
