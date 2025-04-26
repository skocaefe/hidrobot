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
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2.4H2O", "agirlik": 236.15, "tank": "A", "iyonlar": {"Ca": 1, "NO3": 2}},
    "Potasyum Nitrat": {"formul": "KNO3", "agirlik": 101.10, "tank": "A", "iyonlar": {"K": 1, "NO3": 1}},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "agirlik": 136.09, "tank": "B", "iyonlar": {"K": 1, "H2PO4": 1}},
    "Magnezyum Sülfat": {"formul": "MgSO4.7H2O", "agirlik": 246.51, "tank": "B", "iyonlar": {"Mg": 1, "SO4": 1}},
    "Potasyum Sülfat": {"formul": "K2SO4", "agirlik": 174.26, "tank": "B", "iyonlar": {"K": 2, "SO4": 1}},
    "Amonyum Sülfat": {"formul": "(NH4)2SO4", "agirlik": 132.14, "tank": "B", "iyonlar": {"NH4": 2, "SO4": 1}},
    "Monoamonyum Fosfat": {"formul": "NH4H2PO4", "agirlik": 115.03, "tank": "B", "iyonlar": {"NH4": 1, "H2PO4": 1}}
}

# Mikro elementler
mikro_gubreler = {
    "Demir EDDHA": {"formul": "Fe-EDDHA %6", "agirlik": 435.0, "element": "Fe", "yuzde": 6},
    "Borak": {"formul": "Na2B4O7.10H2O", "agirlik": 381.37, "element": "B", "yuzde": 11},
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

# Session state başlatma
if 'recete' not in st.session_state:
    st.session_state.recete = hazir_receteler["Genel Amaçlı"].copy()
    
if 'a_tank' not in st.session_state:
    st.session_state.a_tank = 10
    
if 'b_tank' not in st.session_state:
    st.session_state.b_tank = 10
    
if 'konsantrasyon' not in st.session_state:
    st.session_state.konsantrasyon = 100

# Kullanılabilir gübreler için session state
if 'kullanilabilir_gubreler' not in st.session_state:
    st.session_state.kullanilabilir_gubreler = {gubre: False for gubre in gubreler.keys()}

# Kullanılabilir mikro gübreler için session state
if 'kullanilabilir_mikro_gubreler' not in st.session_state:
    st.session_state.kullanilabilir_mikro_gubreler = {gubre: False for gubre in mikro_gubreler.keys()}

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
tabs = st.tabs(["Reçete Oluşturma", "Gübre Seçimi", "Gübre Hesaplama"])

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

# Tab 2: Gübre Seçimi
with tabs[1]:
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
                f"☐ {gubre} ({gubreler[gubre]['formul']})", 
                value=st.session_state.kullanilabilir_gubreler[gubre],
                key=f"checkbox_{gubre}"
            )
        
        st.markdown("**B Tankı Gübreleri**")
        for gubre in b_tank_gubreler:
            st.session_state.kullanilabilir_gubreler[gubre] = st.checkbox(
                f"☐ {gubre} ({gubreler[gubre]['formul']})", 
                value=st.session_state.kullanilabilir_gubreler[gubre],
                key=f"checkbox_{gubre}"
            )
    
    # Mikro gübreler seçimi
    with col2:
        st.subheader("Mikro Gübreler")
        
        for gubre, bilgi in mikro_gubreler.items():
            st.session_state.kullanilabilir_mikro_gubreler[gubre] = st.checkbox(
                f"☐ {gubre} ({bilgi['formul']})", 
                value=st.session_state.kullanilabilir_mikro_gubreler[gubre],
                key=f"checkbox_mikro_{gubre}"
            )
    
    # Gübre seçimini göster
    secilen_gubreler = [gubre for gubre, secildi in st.session_state.kullanilabilir_gubreler.items() if secildi]
    secilen_mikro_gubreler = [gubre for gubre, secildi in st.session_state.kullanilabilir_mikro_gubreler.items() if secildi]
    
    st.subheader("Seçilen Gübreler")
    if secilen_gubreler:
        st.write("**Makro Gübreler:**")
        for gubre in secilen_gubreler:
            st.write(f"✓ {gubre} ({gubreler[gubre]['formul']})")
    else:
        st.warning("Henüz makro gübre seçmediniz!")
    
    if secilen_mikro_gubreler:
        st.write("**Mikro Gübreler:**")
        for gubre in secilen_mikro_gubreler:
            st.write(f"✓ {gubre} ({mikro_gubreler[gubre]['formul']})")
    else:
        st.warning("Henüz mikro gübre seçmediniz!")
    
    # Eksik gübre kontrolü
    makro_besinler_min = {"NO3": False, "H2PO4": False, "SO4": False, "NH4": False, "K": False, "Ca": False, "Mg": False}
    
    # Eldeki gübrelerle hangi besinlerin sağlanabileceğini kontrol et
    for gubre in secilen_gubreler:
        for iyon, miktar in gubreler[gubre]["iyonlar"].items():
            makro_besinler_min[iyon] = True
    
    # Eksik besinleri göster
    eksik_besinler = [besin for besin, var in makro_besinler_min.items() if not var and st.session_state.recete.get(besin, 0) > 0]
    
    if eksik_besinler:
        st.error("⚠️ Seçilen gübrelerle sağlanamayacak besinler: " + ", ".join(eksik_besinler))
        st.markdown("Önerilen gübreler:")
        for besin in eksik_besinler:
            if besin == "NO3":
                st.markdown("- NO3 (Nitrat) için: ☐ Kalsiyum Nitrat veya ☐ Potasyum Nitrat")
            elif besin == "H2PO4":
                st.markdown("- H2PO4 (Fosfat) için: ☐ Monopotasyum Fosfat veya ☐ Monoamonyum Fosfat")
            elif besin == "SO4":
                st.markdown("- SO4 (Sülfat) için: ☐ Magnezyum Sülfat, ☐ Potasyum Sülfat veya ☐ Amonyum Sülfat")
            elif besin == "NH4":
                st.markdown("- NH4 (Amonyum) için: ☐ Amonyum Sülfat veya ☐ Monoamonyum Fosfat")
            elif besin == "K":
                st.markdown("- K (Potasyum) için: ☐ Potasyum Nitrat, ☐ Monopotasyum Fosfat veya ☐ Potasyum Sülfat")
            elif besin == "Ca":
                st.markdown("- Ca (Kalsiyum) için: ☐ Kalsiyum Nitrat")
            elif besin == "Mg":
                st.markdown("- Mg (Magnezyum) için: ☐ Magnezyum Sülfat")
    else:
        if secilen_gubreler:
            st.success("✅ Seçilen gübrelerle tüm makro besinler sağlanabilir.")

# Tab 3: Gübre Hesaplama
with tabs[2]:
    st.header("Gübre Hesaplama")
    
    if st.button("Gübre Hesapla", type="primary"):
        secilen_gubreler = [gubre for gubre, secildi in st.session_state.kullanilabilir_gubreler.items() if secildi]
        secilen_mikro_gubreler = [gubre for gubre, secildi in st.session_state.kullanilabilir_mikro_gubreler.items() if secildi]
        
        if not secilen_gubreler:
            st.error("Lütfen önce 'Gübre Seçimi' sekmesinden en az bir makro gübre seçiniz!")
        else:
            # Besin ihtiyaçlarını kopyala
            ihtiyac = {
                "NO3": st.session_state.recete["NO3"],
                "H2PO4": st.session_state.recete["H2PO4"],
                "SO4": st.session_state.recete["SO4"],
                "NH4": st.session_state.recete["NH4"],
                "K": st.session_state.recete["K"],
                "Ca": st.session_state.recete["Ca"],
                "Mg": st.session_state.recete["Mg"]
            }
            
            # Tank gübre miktarları
            a_tank_gubreler = {}
            b_tank_gubreler = {}
            
            # Mevcut gübreleri optimize ederek kullan
            for gubre in secilen_gubreler:
                bilgi = gubreler[gubre]
                
                # Gübre ile sağlanacak besin miktarını hesapla
                min_oran = float('inf')
                for iyon, miktar in bilgi["iyonlar"].items():
                    if ihtiyac[iyon] > 0:
                        oran = ihtiyac[iyon] / miktar
                        min_oran = min(min_oran, oran)
                
                # Bu gübre ile en fazla besin sağla
                if min_oran != float('inf') and min_oran > 0:
                    gubre_miktari = min_oran
                    
                    # Tankları ayrı ayrı kontrol et
                    if bilgi["tank"] == "A":
                        a_tank_gubreler[gubre] = gubre_miktari
                    else:
                        b_tank_gubreler[gubre] = gubre_miktari
                    
                    # Sağlanan besinleri ihtiyaçtan düş
                    for iyon, miktar in bilgi["iyonlar"].items():
                        ihtiyac[iyon] -= gubre_miktari * miktar
            
            # Mikro elementler için gübre hesaplama
            mikro_sonuc = []
            
            for element, gubre_adi in [
                ("Fe", "Demir EDDHA"), 
                ("B", "Borak"), 
                ("Mn", "Mangan Sülfat"), 
                ("Zn", "Çinko Sülfat"), 
                ("Cu", "Bakır Sülfat"), 
                ("Mo", "Sodyum Molibdat")
            ]:
                if element in st.session_state.recete and st.session_state.recete[element] > 0 and gubre_adi in secilen_mikro_gubreler:
                    mikromol = st.session_state.recete[element]
                    bilgi = mikro_gubreler[gubre_adi]
                    mmol = mikromol / 1000  # mikromol -> mmol
                    
                    # Saf element için formül ağırlığını hesapla
                    element_mol_agirligi = bilgi["agirlik"] * (100 / bilgi["yuzde"])
                    
                    # mg ve g hesapla
                    mg_l = mmol * element_mol_agirligi
                    g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.b_tank) / 1000
                    
                    mikro_sonuc.append([gubre_adi, bilgi["formul"], float(mikromol), float(mg_l), float(g_tank)])
            
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
                    st.write(f"**Toplam A Tankı gübresi:** {a_tank_toplam/1000:.3f} kg")
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
                    st.write(f"**Toplam B Tankı gübresi:** {b_tank_toplam/1000:.3f} kg")
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
                    "gram/Tank": "{:.4f}"
                }))
                mikro_toplam = sum(sonuc[4] for sonuc in mikro_sonuc)
                st.write(f"**Toplam mikro besin gübresi:** {mikro_toplam:.2f} gram")
            else:
                st.info("Mikro besin elementi eklenmedi veya seçilen gübrelerle karşılanamadı.")
            
            # Karşılanamayan besinleri gösterme
            st.subheader("Denge Kontrol")
            
            eksik_var = False
            uyari = ""
            
            # Kalan ihtiyaçları kontrol et
            for iyon, miktar in ihtiyac.items():
                if miktar > 0.1:
                    eksik_var = True
                    uyari += f" {iyon}: {miktar:.2f} mmol/L,"
            
            if eksik_var:
                st.warning(f"⚠️ Seçilen gübrelerle karşılanamayan besinler:{uyari[:-1]}")
                st.markdown("**Önerilen Ek Gübreler:**")
                for iyon, miktar in ihtiyac.items():
                    if miktar > 0.1:
                        st.markdown(f"- {iyon} için:")
                        for gubre, bilgi in gubreler.items():
                            if iyon in bilgi["iyonlar"] and gubre not in secilen_gubreler:
                                st.markdown(f"  ☐ {gubre} ({bilgi['formul']})")
            else:
                st.success("✅ Tüm besinler seçilen gübrelerle karşılandı.")

# Alt bilgi
st.markdown("---")
st.markdown("HydroBuddy Türkçe | Hidroponik besin çözeltisi hesaplama aracı")
