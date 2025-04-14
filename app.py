import streamlit as st
import pandas as pd

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
                        "cozunurluk": 121.0, "anyonlar": {"NO3": 2}, "katyonlar": {"Ca": 1}},
    "Potasyum Nitrat": {"formul": "KNO3", "agirlik": 101.10, "tank": "A", 
                        "cozunurluk": 35.7, "anyonlar": {"NO3": 1}, "katyonlar": {"K": 1}},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "agirlik": 136.09, "tank": "B",
                            "cozunurluk": 22.0, "anyonlar": {"H2PO4": 1}, "katyonlar": {"K": 1}},
    "Magnezyum Sülfat": {"formul": "MgSO4.7H2O", "agirlik": 246.51, "tank": "B",
                         "cozunurluk": 71.0, "anyonlar": {"SO4": 1}, "katyonlar": {"Mg": 1}},
    "Potasyum Sülfat": {"formul": "K2SO4", "agirlik": 174.26, "tank": "B",
                         "cozunurluk": 12.0, "anyonlar": {"SO4": 1}, "katyonlar": {"K": 2}},
    "Amonyum Sülfat": {"formul": "(NH4)2SO4", "agirlik": 132.14, "tank": "B",
                       "cozunurluk": 75.4, "anyonlar": {"SO4": 1}, "katyonlar": {"NH4": 2}},
    "Monoamonyum Fosfat": {"formul": "NH4H2PO4", "agirlik": 115.03, "tank": "B",
                           "cozunurluk": 40.0, "anyonlar": {"H2PO4": 1}, "katyonlar": {"NH4": 1}}
}

# Mikro elementler
mikro_gubreler = {
    "Demir EDDHA": {"formul": "Fe-EDDHA", "agirlik": 435.0, "element": "Fe", "cozunurluk": 60.0},
    "Borak": {"formul": "Na2B4O7.10H2O", "agirlik": 381.37, "element": "B", "cozunurluk": 5.1},
    "Mangan Sülfat": {"formul": "MnSO4.H2O", "agirlik": 169.02, "element": "Mn", "cozunurluk": 70.0},
    "Çinko Sülfat": {"formul": "ZnSO4.7H2O", "agirlik": 287.56, "element": "Zn", "cozunurluk": 57.7},
    "Bakır Sülfat": {"formul": "CuSO4.5H2O", "agirlik": 249.68, "element": "Cu", "cozunurluk": 32.0},
    "Sodyum Molibdat": {"formul": "Na2MoO4.2H2O", "agirlik": 241.95, "element": "Mo", "cozunurluk": 56.0}
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

# Session state başlatma
if 'recete' not in st.session_state:
    st.session_state.recete = {
        "NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0,
        "NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0,
        "Fe": 40.0, "B": 30.0, "Mn": 5.0, "Zn": 4.0, "Cu": 0.75, "Mo": 0.5
    }
    
if 'a_tank' not in st.session_state:
    st.session_state.a_tank = 10
    
if 'b_tank' not in st.session_state:
    st.session_state.b_tank = 10
    
if 'konsantrasyon' not in st.session_state:
    st.session_state.konsantrasyon = 100

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

# Ana düzen
tabs = st.tabs(["Reçete Oluşturma", "Gübre Hesaplama"])

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
        - B Tankı: Fosfat ve sülfat içeren gübreler
        
        **Konsantrasyon Oranı:**
        100x - Yaygın kullanılan konsantrasyon
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
        
        # Mikro besin değerleri
        st.subheader("Mikro Besinler (mikromol/L)")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            fe = st.number_input("Fe (Demir):", 
                             value=float(st.session_state.recete["Fe"]), 
                             min_value=0.0, max_value=100.0, step=1.0, format="%.1f",
                             key="fe_input")
            st.session_state.recete["Fe"] = fe
            
            mn = st.number_input("Mn (Mangan):", 
                             value=float(st.session_state.recete["Mn"]), 
                             min_value=0.0, max_value=50.0, step=0.5, format="%.1f",
                             key="mn_input")
            st.session_state.recete["Mn"] = mn
        
        with col_m2:
            b = st.number_input("B (Bor):", 
                            value=float(st.session_state.recete["B"]), 
                            min_value=0.0, max_value=100.0, step=1.0, format="%.1f",
                            key="b_input")
            st.session_state.recete["B"] = b
            
            zn = st.number_input("Zn (Çinko):", 
                             value=float(st.session_state.recete["Zn"]), 
                             min_value=0.0, max_value=50.0, step=0.5, format="%.1f",
                             key="zn_input")
            st.session_state.recete["Zn"] = zn
        
        with col_m3:
            cu = st.number_input("Cu (Bakır):", 
                             value=float(st.session_state.recete["Cu"]), 
                             min_value=0.0, max_value=10.0, step=0.05, format="%.2f",
                             key="cu_input")
            st.session_state.recete["Cu"] = cu
            
            mo = st.number_input("Mo (Molibden):", 
                             value=float(st.session_state.recete["Mo"]), 
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
            st.write(f"**Toplam:** {anyon_toplam:.2f} me/L")
        
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
            st.write(f"**Toplam:** {katyon_toplam:.2f} me/L")
        
        # Denge kontrolü
        fark = abs(anyon_toplam - katyon_toplam)
        if fark < 0.5:
            st.success(f"✅ İyonik denge iyi durumda! (Fark: {fark:.2f} me/L)")
        elif fark < 1.0:
            st.warning(f"⚠️ İyonik denge kabul edilebilir sınırda. (Fark: {fark:.2f} me/L)")
        else:
            st.error(f"❌ İyonik denge bozuk! (Fark: {fark:.2f} me/L)")

# Tab 2: Gübre Hesaplama
with tabs[1]:
    st.header("Gübre Hesaplama")
    
    if st.button("Gübre Hesapla", type="primary"):
        a_tank_gubreler = {}
        b_tank_gubreler = {}
        
        # 1. Önce NH4 ve H2PO4 dağılımını yap
        nh4_ihtiyac = st.session_state.recete["NH4"]
        h2po4_ihtiyac = st.session_state.recete["H2PO4"]
        
        # NH4H2PO4 - Monoamonyum Fosfat için
        if nh4_ihtiyac > 0 and h2po4_ihtiyac > 0:
            map_miktar = min(nh4_ihtiyac, h2po4_ihtiyac)
            b_tank_gubreler["Monoamonyum Fosfat"] = map_miktar
            nh4_ihtiyac -= map_miktar
            h2po4_ihtiyac -= map_miktar
        
        # Kalan H2PO4 için KH2PO4 - Monopotasyum Fosfat kullan
        if h2po4_ihtiyac > 0:
            b_tank_gubreler["Monopotasyum Fosfat"] = h2po4_ihtiyac
            k_ihtiyac = st.session_state.recete["K"] - h2po4_ihtiyac
        else:
            k_ihtiyac = st.session_state.recete["K"]
        
        # 2. Kalsiyum Nitrat (A Tankı)
        if st.session_state.recete["Ca"] > 0:
            a_tank_gubreler["Kalsiyum Nitrat"] = st.session_state.recete["Ca"]
            no3_ihtiyac = st.session_state.recete["NO3"] - (2 * st.session_state.recete["Ca"])
        else:
            no3_ihtiyac = st.session_state.recete["NO3"]
        
        # 3. Magnezyum Sülfat (B Tankı)
        if st.session_state.recete["Mg"] > 0:
            b_tank_gubreler["Magnezyum Sülfat"] = st.session_state.recete["Mg"]
            so4_ihtiyac = st.session_state.recete["SO4"] - st.session_state.recete["Mg"]
        else:
            so4_ihtiyac = st.session_state.recete["SO4"]
        
        # 4. Amonyum Sülfat - Kalan NH4 için
        if nh4_ihtiyac > 0 and so4_ihtiyac > 0:
            as_miktar = min(nh4_ihtiyac / 2, so4_ihtiyac)
            if as_miktar > 0:
                b_tank_gubreler["Amonyum Sülfat"] = as_miktar
                nh4_ihtiyac -= (as_miktar * 2)  # 2 NH4 per SO4
                so4_ihtiyac -= as_miktar
                
        # 5. Potasyum Nitrat (A Tankı)
        if no3_ihtiyac > 0 and k_ihtiyac > 0:
            kno3_miktar = min(no3_ihtiyac, k_ihtiyac)
            if kno3_miktar > 0:
                a_tank_gubreler["Potasyum Nitrat"] = kno3_miktar
                no3_ihtiyac -= kno3_miktar
                k_ihtiyac -= kno3_miktar
        
        # 6. Potasyum Sülfat - Kalan K ve SO4 için
        if k_ihtiyac > 0 and so4_ihtiyac > 0:
            k2so4_miktar = min(k_ihtiyac / 2, so4_ihtiyac)
            if k2so4_miktar > 0:
                b_tank_gubreler["Potasyum Sülfat"] = k2so4_miktar
                k_ihtiyac -= (k2so4_miktar * 2)
                so4_ihtiyac -= k2so4_miktar
        
        # Mikro elementler
        mikro_gubreler_sonuc = {}
        for element, bilgi in [("Fe", "Demir EDDHA"), 
                                ("B", "Borak"), 
                                ("Mn", "Mangan Sülfat"), 
                                ("Zn", "Çinko Sülfat"), 
                                ("Cu", "Bakır Sülfat"), 
                                ("Mo", "Sodyum Molibdat")]:
            if st.session_state.recete[element] > 0:
                mikro_gubreler_sonuc[bilgi] = st.session_state.recete[element]
        
        # Sonuçları hesapla
        # A Tankı sonuçları
        a_tank_sonuc = []
        a_tank_toplam_gram = 0
        a_tank_su_ihtiyaci_litre = 0
        
        for gubre, mmol in a_tank_gubreler.items():
            formul = gubreler[gubre]["formul"]
            mg_l = mmol * gubreler[gubre]["agirlik"]
            g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.a_tank) / 1000
            a_tank_toplam_gram += g_tank
            
            # Çözünürlük için gereken su miktarı
            gereken_su = g_tank / gubreler[gubre]["cozunurluk"] / 10
            a_tank_su_ihtiyaci_litre += gereken_su
            
            a_tank_sonuc.append([gubre, formul, float(mmol), float(mg_l), float(g_tank)])
        
        # B Tankı sonuçları
        b_tank_sonuc = []
        b_tank_toplam_gram = 0
        b_tank_su_ihtiyaci_litre = 0
        
        for gubre, mmol in b_tank_gubreler.items():
            formul = gubreler[gubre]["formul"]
            mg_l = mmol * gubreler[gubre]["agirlik"]
            g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.b_tank) / 1000
            b_tank_toplam_gram += g_tank
            
            # Çözünürlük için gereken su miktarı
            gereken_su = g_tank / gubreler[gubre]["cozunurluk"] / 10
            b_tank_su_ihtiyaci_litre += gereken_su
            
            b_tank_sonuc.append([gubre, formul, float(mmol), float(mg_l), float(g_tank)])
        
        # Mikro besin sonuçları
        mikro_sonuc = []
        
        for gubre, mikromol in mikro_gubreler_sonuc.items():
            formul = mikro_gubreler[gubre]["formul"]
            mmol = mikromol / 1000
            mg_l = mmol * mikro_gubreler[gubre]["agirlik"]
            g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.b_tank) / 1000
            b_tank_toplam_gram += g_tank
            
            # Çözünürlük için gereken su miktarı
            gereken_su = g_tank / mikro_gubreler[gubre]["cozunurluk"] / 10
            b_tank_su_ihtiyaci_litre += gereken_su
            
            mikro_sonuc.append([gubre, formul, float(mikromol), float(mg_l), float(g_tank)])
        
        # Sonuçları göster
        col_sonuc1, col_sonuc2 = st.columns(2)
        
        with col_sonuc1:
            st.subheader("A Tankı (Kalsiyum içeren)")
            
            if a_tank_sonuc:
                a_tank_df = pd.DataFrame(a_tank_sonuc, 
                                      columns=["Gübre Adı", "Formül", "mmol/L", "mg/L", "g/Tank"])
                st.dataframe(a_tank_df.style.format({
                    "mmol/L": "{:.2f}", 
                    "mg/L": "{:.2f}", 
                    "g/Tank": "{:.2f}"
                }))
                st.write(f"**Toplam:** {a_tank_toplam_gram:.2f} gram gübre")
                
                # Çözünme kontrolü
                if a_tank_su_ihtiyaci_litre > st.session_state.a_tank:
                    st.error(f"⚠️ A Tankı için {a_tank_su_ihtiyaci_litre:.1f} litre su gerekli!")
                else:
                    st.success(f"✅ A Tankı hacmi yeterli ({a_tank_su_ihtiyaci_litre:.1f}/{st.session_state.a_tank} litre)")
            else:
                st.info("A Tankı için gübre eklenmedi.")
        
        with col_sonuc2:
            st.subheader("B Tankı (Fosfat, Sülfat, NH4)")
            
            if b_tank_sonuc:
                b_tank_df = pd.DataFrame(b_tank_sonuc, 
                                      columns=["Gübre Adı", "Formül", "mmol/L", "mg/L", "g/Tank"])
                st.dataframe(b_tank_df.style.format({
                    "mmol/L": "{:.2f}", 
                    "mg/L": "{:.2f}", 
                    "g/Tank": "{:.2f}"
                }))
                st.write(f"**Toplam:** {b_tank_toplam_gram:.2f} gram gübre")
                
                # Çözünme kontrolü
                if b_tank_su_ihtiyaci_litre > st.session_state.b_tank:
                    st.error(f"⚠️ B Tankı için {b_tank_su_ihtiyaci_litre:.1f} litre su gerekli!")
                else:
                    st.success(f"✅ B Tankı hacmi yeterli ({b_tank_su_ihtiyaci_litre:.1f}/{st.session_state.b_tank} litre)")
            else:
                st.info("
