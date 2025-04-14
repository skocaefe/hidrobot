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
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2.4H2O", "agirlik": 236.15, "tank": "A", 
                        "anyonlar": {"NO3": 2}, "katyonlar": {"Ca": 1}},
    "Potasyum Nitrat": {"formul": "KNO3", "agirlik": 101.10, "tank": "A", 
                       "anyonlar": {"NO3": 1}, "katyonlar": {"K": 1}},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "agirlik": 136.09, "tank": "B",
                           "anyonlar": {"H2PO4": 1}, "katyonlar": {"K": 1}},
    "Magnezyum Sülfat": {"formul": "MgSO4.7H2O", "agirlik": 246.51, "tank": "B",
                        "anyonlar": {"SO4": 1}, "katyonlar": {"Mg": 1}},
    "Potasyum Sülfat": {"formul": "K2SO4", "agirlik": 174.26, "tank": "B",
                       "anyonlar": {"SO4": 1}, "katyonlar": {"K": 2}},
    "Amonyum Sülfat": {"formul": "(NH4)2SO4", "agirlik": 132.14, "tank": "B",
                      "anyonlar": {"SO4": 1}, "katyonlar": {"NH4": 2}}
}

# Mikro elementler
mikro_gubreler = {
    "Demir EDDHA": {"formul": "Fe-EDDHA", "agirlik": 435.0, "element": "Fe"},
    "Borak": {"formul": "Na2B4O7.10H2O", "agirlik": 381.37, "element": "B"},
    "Mangan Sülfat": {"formul": "MnSO4.H2O", "agirlik": 169.02, "element": "Mn"},
    "Çinko Sülfat": {"formul": "ZnSO4.7H2O", "agirlik": 287.56, "element": "Zn"},
    "Bakır Sülfat": {"formul": "CuSO4.5H2O", "agirlik": 249.68, "element": "Cu"},
    "Sodyum Molibdat": {"formul": "Na2MoO4.2H2O", "agirlik": 241.95, "element": "Mo"}
}

# Hazır reçeteler
hazir_receteler = {
    "Genel Amaçlı": {
        "anyonlar": {"NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0},
        "katyonlar": {"NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0},
        "mikro": {"Fe": 40, "B": 30, "Mn": 5, "Zn": 4, "Cu": 0.75, "Mo": 0.5}
    },
    "Domates": {
        "anyonlar": {"NO3": 14.0, "H2PO4": 1.5, "SO4": 1.5},
        "katyonlar": {"NH4": 1.2, "K": 7.0, "Ca": 4.0, "Mg": 1.5},
        "mikro": {"Fe": 50, "B": 40, "Mn": 8, "Zn": 4, "Cu": 0.8, "Mo": 0.5}
    },
    "Salatalık": {
        "anyonlar": {"NO3": 12.0, "H2PO4": 1.3, "SO4": 1.2},
        "katyonlar": {"NH4": 1.1, "K": 5.8, "Ca": 3.5, "Mg": 1.2},
        "mikro": {"Fe": 45, "B": 35, "Mn": 6, "Zn": 4, "Cu": 0.75, "Mo": 0.5}
    },
    "Marul": {
        "anyonlar": {"NO3": 10.0, "H2PO4": 1.0, "SO4": 0.8},
        "katyonlar": {"NH4": 0.8, "K": 4.5, "Ca": 3.0, "Mg": 0.8},
        "mikro": {"Fe": 35, "B": 25, "Mn": 4, "Zn": 3, "Cu": 0.5, "Mo": 0.4}
    }
}

# Session state başlatma
if 'anyonlar' not in st.session_state:
    st.session_state.anyonlar = {"NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0}
    
if 'katyonlar' not in st.session_state:
    st.session_state.katyonlar = {"NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0}
    
if 'mikro' not in st.session_state:
    st.session_state.mikro = {"Fe": 40, "B": 30, "Mn": 5, "Zn": 4, "Cu": 0.75, "Mo": 0.5}
    
if 'a_tank' not in st.session_state:
    st.session_state.a_tank = 10
    
if 'b_tank' not in st.session_state:
    st.session_state.b_tank = 10
    
if 'konsantrasyon' not in st.session_state:
    st.session_state.konsantrasyon = 100

# İyonik denge hesaplama
def hesapla_iyonik_denge(anyonlar, katyonlar):
    anyon_toplam = 0
    katyon_toplam = 0
    
    for anyon, deger in anyonlar.items():
        anyon_toplam += deger * abs(iyon_degerlikleri[anyon])
    
    for katyon, deger in katyonlar.items():
        katyon_toplam += deger * abs(iyon_degerlikleri[katyon])
    
    return anyon_toplam, katyon_toplam

# Temel düzen
col1, col2 = st.columns([1, 2])

# Sol taraf: Reçete seçimi ve tank ayarları
with col1:
    st.header("Reçete ve Tank Ayarları")
    
    # Hazır reçete seçimi
    secilen_recete = st.selectbox(
        "Hazır Reçete:",
        options=list(hazir_receteler.keys())
    )
    
    if st.button("Reçeteyi Yükle"):
        st.session_state.anyonlar = hazir_receteler[secilen_recete]["anyonlar"].copy()
        st.session_state.katyonlar = hazir_receteler[secilen_recete]["katyonlar"].copy()
        st.session_state.mikro = hazir_receteler[secilen_recete]["mikro"].copy()
        st.success(f"{secilen_recete} reçetesi yüklendi!")
    
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
    **Tank İçerikleri:**
    - A Tankı: Kalsiyum içeren gübreler
    - B Tankı: Fosfat ve sülfat içeren gübreler ve mikro elementler
    """)

# Sağ taraf: Reçete değerleri ve hesaplamalar
with col2:
    tabs = st.tabs(["Reçete Değerleri", "Gübre Hesaplama"])
    
    # Reçete değerleri
    with tabs[0]:
        st.header("Reçete Değerleri")
        
        col_a, col_b = st.columns(2)
        
        # Anyon değerleri
        with col_a:
            st.subheader("Anyonlar (mmol/L)")
            
            no3 = st.number_input("NO3 (Nitrat):", value=st.session_state.anyonlar["NO3"], 
                               min_value=0.0, max_value=30.0, step=0.1, format="%.2f")
            h2po4 = st.number_input("H2PO4 (Fosfat):", value=st.session_state.anyonlar["H2PO4"], 
                                 min_value=0.0, max_value=10.0, step=0.1, format="%.2f")
            so4 = st.number_input("SO4 (Sülfat):", value=st.session_state.anyonlar["SO4"], 
                               min_value=0.0, max_value=10.0, step=0.1, format="%.2f")
            
            # Anyonları güncelle
            st.session_state.anyonlar["NO3"] = no3
            st.session_state.anyonlar["H2PO4"] = h2po4
            st.session_state.anyonlar["SO4"] = so4
        
        # Katyon değerleri
        with col_b:
            st.subheader("Katyonlar (mmol/L)")
            
            nh4 = st.number_input("NH4 (Amonyum):", value=st.session_state.katyonlar["NH4"], 
                               min_value=0.0, max_value=10.0, step=0.1, format="%.2f")
            k = st.number_input("K (Potasyum):", value=st.session_state.katyonlar["K"], 
                             min_value=0.0, max_value=20.0, step=0.1, format="%.2f")
            ca = st.number_input("Ca (Kalsiyum):", value=st.session_state.katyonlar["Ca"], 
                              min_value=0.0, max_value=15.0, step=0.1, format="%.2f")
            mg = st.number_input("Mg (Magnezyum):", value=st.session_state.katyonlar["Mg"], 
                              min_value=0.0, max_value=10.0, step=0.1, format="%.2f")
            
            # Katyonları güncelle
            st.session_state.katyonlar["NH4"] = nh4
            st.session_state.katyonlar["K"] = k
            st.session_state.katyonlar["Ca"] = ca
            st.session_state.katyonlar["Mg"] = mg
        
        # Mikro besin değerleri
        st.subheader("Mikro Besinler (mikromol/L)")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            fe = st.number_input("Fe (Demir):", value=st.session_state.mikro["Fe"], 
                              min_value=0.0, max_value=100.0, step=1.0, format="%.1f")
            mn = st.number_input("Mn (Mangan):", value=st.session_state.mikro["Mn"], 
                              min_value=0.0, max_value=50.0, step=0.5, format="%.1f")
            
            st.session_state.mikro["Fe"] = fe
            st.session_state.mikro["Mn"] = mn
        
        with col_m2:
            b = st.number_input("B (Bor):", value=st.session_state.mikro["B"], 
                             min_value=0.0, max_value=100.0, step=1.0, format="%.1f")
            zn = st.number_input("Zn (Çinko):", value=st.session_state.mikro["Zn"], 
                              min_value=0.0, max_value=50.0, step=0.5, format="%.1f")
            
            st.session_state.mikro["B"] = b
            st.session_state.mikro["Zn"] = zn
        
        with col_m3:
            cu = st.number_input("Cu (Bakır):", value=st.session_state.mikro["Cu"], 
                              min_value=0.0, max_value=10.0, step=0.05, format="%.2f")
            mo = st.number_input("Mo (Molibden):", value=st.session_state.mikro["Mo"], 
                              min_value=0.0, max_value=10.0, step=0.05, format="%.2f")
            
            st.session_state.mikro["Cu"] = cu
            st.session_state.mikro["Mo"] = mo
        
        # İyonik denge hesaplaması
        st.subheader("İyonik Denge")
        
        anyon_toplam, katyon_toplam = hesapla_iyonik_denge(
            st.session_state.anyonlar, st.session_state.katyonlar
        )
        
        col_denge1, col_denge2 = st.columns(2)
        
        # Anyonlar tablosu
        with col_denge1:
            anyon_data = []
            for anyon, deger in st.session_state.anyonlar.items():
                me = deger * abs(iyon_degerlikleri[anyon])
                anyon_data.append([anyon, deger, me])
            
            anyon_df = pd.DataFrame(anyon_data, columns=["Anyon", "mmol/L", "me/L"])
            st.write("**Anyonlar:**")
            st.dataframe(anyon_df.style.format({"mmol/L": "{:.2f}", "me/L": "{:.2f}"}))
            st.write(f"**Toplam:** {anyon_toplam:.2f} me/L")
        
        # Katyonlar tablosu
        with col_denge2:
            katyon_data = []
            for katyon, deger in st.session_state.katyonlar.items():
                me = deger * abs(iyon_degerlikleri[katyon])
                katyon_data.append([katyon, deger, me])
            
            katyon_df = pd.DataFrame(katyon_data, columns=["Katyon", "mmol/L", "me/L"])
            st.write("**Katyonlar:**")
            st.dataframe(katyon_df.style.format({"mmol/L": "{:.2f}", "me/L": "{:.2f}"}))
            st.write(f"**Toplam:** {katyon_toplam:.2f} me/L")
        
        # Denge kontrolü
        fark = abs(anyon_toplam - katyon_toplam)
        if fark < 0.5:
            st.success(f"✅ İyonik denge iyi durumda! (Fark: {fark:.2f} me/L)")
        elif fark < 1.0:
            st.warning(f"⚠️ İyonik denge kabul edilebilir sınırda. (Fark: {fark:.2f} me/L)")
        else:
            st.error(f"❌ İyonik denge bozuk! (Fark: {fark:.2f} me/L)")
    
    # Gübre hesaplama
    with tabs[1]:
        st.header("Gübre Hesaplama")
        
        if st.button("Gübre Hesapla"):
            # 1. Kalsiyum Nitrat (A Tankı)
            a_tank_gubreler = {}
            if st.session_state.katyonlar["Ca"] > 0:
                a_tank_gubreler["Kalsiyum Nitrat"] = st.session_state.katyonlar["Ca"]
                kalan_no3 = st.session_state.anyonlar["NO3"] - 2 * st.session_state.katyonlar["Ca"]
            else:
                kalan_no3 = st.session_state.anyonlar["NO3"]
            
            # 2. Monopotasyum Fosfat (B Tankı)
            b_tank_gubreler = {}
            if st.session_state.anyonlar["H2PO4"] > 0:
                b_tank_gubreler["Monopotasyum Fosfat"] = st.session_state.anyonlar["H2PO4"]
                kalan_k = st.session_state.katyonlar["K"] - st.session_state.anyonlar["H2PO4"]
            else:
                kalan_k = st.session_state.katyonlar["K"]
            
            # 3. Magnezyum Sülfat (B Tankı)
            if st.session_state.katyonlar["Mg"] > 0:
                b_tank_gubreler["Magnezyum Sülfat"] = st.session_state.katyonlar["Mg"]
                kalan_so4 = st.session_state.anyonlar["SO4"] - st.session_state.katyonlar["Mg"]
            else:
                kalan_so4 = st.session_state.anyonlar["SO4"]
            
            # 4. Potasyum Nitrat (A Tankı)
            if kalan_no3 > 0 and kalan_k > 0:
                kno3_miktar = min(kalan_no3, kalan_k)
                if kno3_miktar > 0:
                    a_tank_gubreler["Potasyum Nitrat"] = kno3_miktar
                    kalan_no3 -= kno3_miktar
                    kalan_k -= kno3_miktar
            
            # 5. Potasyum Sülfat (B Tankı)
            if kalan_k > 0 and kalan_so4 > 0:
                k2so4_miktar = min(kalan_k / 2, kalan_so4)
                if k2so4_miktar > 0:
                    b_tank_gubreler["Potasyum Sülfat"] = k2so4_miktar
                    kalan_so4 -= k2so4_miktar
                    kalan_k -= 2 * k2so4_miktar
            
            # 6. Amonyum Sülfat (B Tankı)
            if st.session_state.katyonlar["NH4"] > 0 and kalan_so4 > 0:
                nh4_miktar = min(st.session_state.katyonlar["NH4"] / 2, kalan_so4)
                if nh4_miktar > 0:
                    b_tank_gubreler["Amonyum Sülfat"] = nh4_miktar
            
            # Mikro elementler
            mikro_gubreler_sonuc = {}
            for element, mikromol in st.session_state.mikro.items():
                if mikromol > 0:
                    for gubre_adi, bilgi in mikro_gubreler.items():
                        if bilgi["element"] == element:
                            mikro_gubreler_sonuc[gubre_adi] = mikromol
            
            # A Tankı sonuçları
            a_tank_sonuc = []
            a_tank_toplam = 0
            
            for gubre, mmol in a_tank_gubreler.items():
                formul = gubreler[gubre]["formul"]
                mg_l = mmol * gubreler[gubre]["agirlik"]
                g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.a_tank) / 1000
                a_tank_toplam += g_tank
                a_tank_sonuc.append([gubre, formul, mmol, mg_l, g_tank])
            
            # B Tankı sonuçları
            b_tank_sonuc = []
            b_tank_toplam = 0
            
            for gubre, mmol in b_tank_gubreler.items():
                formul = gubreler[gubre]["formul"]
                mg_l = mmol * gubreler[gubre]["agirlik"]
                g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.b_tank) / 1000
                b_tank_toplam += g_tank
                b_tank_sonuc.append([gubre, formul, mmol, mg_l, g_tank])
            
            # Mikro besin sonuçları
            mikro_sonuc = []
            
            for gubre, mikromol in mikro_gubreler_sonuc.items():
                formul = mikro_gubreler[gubre]["formul"]
                mmol = mikromol / 1000
                mg_l = mmol * mikro_gubreler[gubre]["agirlik"]
                g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.b_tank) / 1000
                b_tank_toplam += g_tank
                mikro_sonuc.append([gubre, formul, mikromol, mg_l, g_tank])
            
            # Sonuçları göster
            if a_tank_sonuc:
                st.subheader("A Tankı (Kalsiyum içeren)")
                a_tank_df = pd.DataFrame(a_tank_sonuc, 
                                      columns=["Gübre Adı", "Formül", "mmol/L", "mg/L", "g/Tank"])
                st.dataframe(a_tank_df.style.format({
                    "mmol/L": "{:.2f}", 
                    "mg/L": "{:.2f}", 
                    "g/Tank": "{:.2f}"
                }))
                st.write(f"**Toplam A Tankı gübresi:** {a_tank_toplam:.2f} gram")
                
                # Tank kapasitesi kontrolü (yaklaşık 300g/L çözünürlük)
                kapasite_a = st.session_state.a_tank * 300
                if a_tank_toplam > kapasite_a:
                    st.error(f"⚠️ A Tankı kapasitesi yetersiz! ({a_tank_toplam:.0f}g > {kapasite_a:.0f}g)")
                    st.info("A Tankı hacmini artırın veya konsantrasyon oranını düşürün.")
            else:
                st.info("A Tankı için gübre eklenmedi.")
            
            if b_tank_sonuc or mikro_sonuc:
                st.subheader("B Tankı (Fosfat, Sülfat ve Mikro elementler)")
                
                if b_tank_sonuc:
                    b_tank_df = pd.DataFrame(b_tank_sonuc, 
                                          columns=["Gübre Adı", "Formül", "mmol/L", "mg/L", "g/Tank"])
                    st.dataframe(b_tank_df.style.format({
                        "mmol/L": "{:.2f}", 
                        "mg/L": "{:.2f}", 
                        "g/Tank": "{:.2f}"
                    }))
                
                if mikro_sonuc:
                    st.subheader("Mikro Besinler")
                    mikro_df = pd.DataFrame(mikro_sonuc, 
                                         columns=["Gübre Adı", "Formül", "mikromol/L", "mg/L", "g/Tank"])
                    st.dataframe(mikro_df.style.format({
                        "mikromol/L": "{:.2f}", 
                        "mg/L": "{:.4f}", 
                        "g/Tank": "{:.4f}"
                    }))
                
                st.write(f"**Toplam B Tankı gübresi:** {b_tank_toplam:.2f} gram")
                
                # Tank kapasitesi kontrolü (yaklaşık 250g/L çözünürlük)
                kapasite_b = st.session_state.b_tank * 250
                if b_tank_toplam > kapasite_b:
                    st.error(f"⚠️ B Tankı kapasitesi yetersiz! ({b_tank_toplam:.0f}g > {kapasite_b:.0f}g)")
                    st.info("B Tankı hacmini artırın veya konsantrasyon oranını düşürün.")
            else:
                st.info("B Tankı için gübre eklenmedi.")

# Alt bilgi
st.markdown("---")
st.markdown("HydroBuddy Türkçe | Hidroponik besin çözeltisi hesaplama aracı")
