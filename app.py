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
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2.4H2O", "agirlik": 236.15, "tank": "A"},
    "Potasyum Nitrat": {"formul": "KNO3", "agirlik": 101.10, "tank": "A"},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "agirlik": 136.09, "tank": "B"},
    "Magnezyum Sülfat": {"formul": "MgSO4.7H2O", "agirlik": 246.51, "tank": "B"},
    "Potasyum Sülfat": {"formul": "K2SO4", "agirlik": 174.26, "tank": "B"},
    "Amonyum Sülfat": {"formul": "(NH4)2SO4", "agirlik": 132.14, "tank": "B"},
    "Monoamonyum Fosfat": {"formul": "NH4H2PO4", "agirlik": 115.03, "tank": "B"}
}

# Hazır reçeteler
hazir_receteler = {
    "Genel Amaçlı": {
        "NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0,
        "NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0
    },
    "Domates": {
        "NO3": 14.0, "H2PO4": 1.5, "SO4": 1.5,
        "NH4": 1.2, "K": 7.0, "Ca": 4.0, "Mg": 1.5
    },
    "Salatalık": {
        "NO3": 12.0, "H2PO4": 1.3, "SO4": 1.2,
        "NH4": 1.1, "K": 5.8, "Ca": 3.5, "Mg": 1.2
    },
    "Marul": {
        "NO3": 10.0, "H2PO4": 1.0, "SO4": 0.8,
        "NH4": 0.8, "K": 4.5, "Ca": 3.0, "Mg": 0.8
    }
}

# Session state başlatma
if 'recete' not in st.session_state:
    st.session_state.recete = {
        "NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0,
        "NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0
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
        
        # 1. Monoamonyum Fosfat (NH4H2PO4) için
        map_miktari = min(st.session_state.recete["NH4"], st.session_state.recete["H2PO4"])
        if map_miktari > 0:
            b_tank_gubreler["Monoamonyum Fosfat"] = map_miktari
            kalan_nh4 = st.session_state.recete["NH4"] - map_miktari
            kalan_h2po4 = st.session_state.recete["H2PO4"] - map_miktari
        else:
            kalan_nh4 = st.session_state.recete["NH4"]
            kalan_h2po4 = st.session_state.recete["H2PO4"]
        
        # 2. Monopotasyum Fosfat (KH2PO4) için
        if kalan_h2po4 > 0:
            b_tank_gubreler["Monopotasyum Fosfat"] = kalan_h2po4
            kalan_k = st.session_state.recete["K"] - kalan_h2po4
        else:
            kalan_k = st.session_state.recete["K"]
        
        # 3. Kalsiyum Nitrat (Ca(NO3)2) için
        if st.session_state.recete["Ca"] > 0:
            a_tank_gubreler["Kalsiyum Nitrat"] = st.session_state.recete["Ca"]
            kalan_no3 = st.session_state.recete["NO3"] - (2 * st.session_state.recete["Ca"])
        else:
            kalan_no3 = st.session_state.recete["NO3"]
        
        # 4. Magnezyum Sülfat (MgSO4) için
        if st.session_state.recete["Mg"] > 0:
            b_tank_gubreler["Magnezyum Sülfat"] = st.session_state.recete["Mg"]
            kalan_so4 = st.session_state.recete["SO4"] - st.session_state.recete["Mg"]
        else:
            kalan_so4 = st.session_state.recete["SO4"]
        
        # 5. Amonyum Sülfat ((NH4)2SO4) için
        if kalan_nh4 > 0 and kalan_so4 > 0:
            as_miktari = min(kalan_nh4 / 2, kalan_so4)
            if as_miktari > 0:
                b_tank_gubreler["Amonyum Sülfat"] = as_miktari
                kalan_nh4 -= (2 * as_miktari)
                kalan_so4 -= as_miktari
        
        # 6. Potasyum Nitrat (KNO3) için
        if kalan_no3 > 0 and kalan_k > 0:
            kno3_miktari = min(kalan_no3, kalan_k)
            if kno3_miktari > 0:
                a_tank_gubreler["Potasyum Nitrat"] = kno3_miktari
                kalan_no3 -= kno3_miktari
                kalan_k -= kno3_miktari
        
        # 7. Potasyum Sülfat (K2SO4) için
        if kalan_k > 0 and kalan_so4 > 0:
            k2so4_miktari = min(kalan_k / 2, kalan_so4)
            if k2so4_miktari > 0:
                b_tank_gubreler["Potasyum Sülfat"] = k2so4_miktari
                kalan_k -= (2 * k2so4_miktari)
                kalan_so4 -= k2so4_miktari
        
        # Sonuçları hesaplama
        a_tank_sonuc = []
        a_tank_toplam = 0
        
        for gubre, mmol in a_tank_gubreler.items():
            formul = gubreler[gubre]["formul"]
            mg_l = mmol * gubreler[gubre]["agirlik"]
            g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.a_tank) / 1000
            a_tank_toplam += g_tank
            
            a_tank_sonuc.append([gubre, formul, float(mmol), float(mg_l), float(g_tank)])
        
        b_tank_sonuc = []
        b_tank_toplam = 0
        
        for gubre, mmol in b_tank_gubreler.items():
            formul = gubreler[gubre]["formul"]
            mg_l = mmol * gubreler[gubre]["agirlik"]
            g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.b_tank) / 1000
            b_tank_toplam += g_tank
            
            b_tank_sonuc.append([gubre, formul, float(mmol), float(mg_l), float(g_tank)])
        
        # Sonuçları gösterme
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
                st.write(f"**Toplam A Tankı gübresi:** {a_tank_toplam:.2f} gram")
            else:
                st.info("A Tankı için gübre eklenmedi.")
        
        with col_sonuc2:
            st.subheader("B Tankı (Fosfat, Sülfat ve Amonyum)")
            
            if b_tank_sonuc:
                b_tank_df = pd.DataFrame(b_tank_sonuc, 
                                     columns=["Gübre Adı", "Formül", "mmol/L", "mg/L", "g/Tank"])
                st.dataframe(b_tank_df.style.format({
                    "mmol/L": "{:.2f}", 
                    "mg/L": "{:.2f}", 
                    "g/Tank": "{:.2f}"
                }))
                st.write(f"**Toplam B Tankı gübresi:** {b_tank_toplam:.2f} gram")
            else:
                st.info("B Tankı için gübre eklenmedi.")
        
        # Karşılanamayan besinleri gösterme
        st.subheader("Denge Kontrol")
        
        eksik_var = False
        uyari = ""
        
        if kalan_nh4 > 0.1:
            eksik_var = True
            uyari += f" NH4: {kalan_nh4:.2f} mmol/L,"
        
        if kalan_k > 0.1:
            eksik_var = True
            uyari += f" K: {kalan_k:.2f} mmol/L,"
        
        if kalan_no3 > 0.1:
            eksik_var = True
            uyari += f" NO3: {kalan_no3:.2f} mmol/L,"
        
        if kalan_so4 > 0.1:
            eksik_var = True
            uyari += f" SO4: {kalan_so4:.2f} mmol/L,"
        
        if eksik_var:
            st.warning(f"⚠️ Karşılanamayan besinler:{uyari[:-1]}")
        else:
            st.success("✅ Tüm besinler uygun şekilde karşılandı.")

# Alt bilgi
st.markdown("---")
st.markdown("HydroBuddy Türkçe | Hidroponik besin çözeltisi hesaplama aracı")
