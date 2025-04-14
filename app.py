import streamlit as st
import pandas as pd
import numpy as np
import base64
from io import BytesIO

# Sayfa ayarları
st.set_page_config(
    page_title="HydroBuddy Türkçe",
    page_icon="🌱",
    layout="wide"
)

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
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2.4H2O", "agirlik": 236.15, 
                         "deger": {"NO3": 2, "Ca": 1}, "tank": "A"},
    "Potasyum Nitrat": {"formul": "KNO3", "agirlik": 101.10, 
                         "deger": {"NO3": 1, "K": 1}, "tank": "A"},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "agirlik": 136.09, 
                            "deger": {"H2PO4": 1, "K": 1}, "tank": "B"},
    "Magnezyum Sülfat": {"formul": "MgSO4.7H2O", "agirlik": 246.51, 
                          "deger": {"SO4": 1, "Mg": 1}, "tank": "B"},
    "Potasyum Sülfat": {"formul": "K2SO4", "agirlik": 174.26, 
                         "deger": {"SO4": 1, "K": 2}, "tank": "B"},
    "Amonyum Sülfat": {"formul": "(NH4)2SO4", "agirlik": 132.14, 
                        "deger": {"SO4": 1, "NH4": 2}, "tank": "B"},
    "Monoamonyum Fosfat": {"formul": "NH4H2PO4", "agirlik": 115.03, 
                           "deger": {"H2PO4": 1, "NH4": 1}, "tank": "B"}
}

# Mikro elementler
mikro_gubreler = {
    "Demir EDDHA": {"formul": "Fe-EDDHA", "agirlik": 435, "element": "Fe"},
    "Borak": {"formul": "Na2B4O7.10H2O", "agirlik": 381.37, "element": "B"},
    "Mangan Sülfat": {"formul": "MnSO4.H2O", "agirlik": 169.02, "element": "Mn"},
    "Çinko Sülfat": {"formul": "ZnSO4.7H2O", "agirlik": 287.56, "element": "Zn"},
    "Bakır Sülfat": {"formul": "CuSO4.5H2O", "agirlik": 249.68, "element": "Cu"},
    "Sodyum Molibdat": {"formul": "Na2MoO4.2H2O", "agirlik": 241.95, "element": "Mo"}
}

# Hazır reçeteler
hazir_receteler = {
    "Genel Amaçlı": {
        "NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0,
        "NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0,
        "Fe": 40, "B": 30, "Mn": 5, "Zn": 4, "Cu": 0.75, "Mo": 0.5
    },
    "Domates": {
        "NO3": 14.0, "H2PO4": 1.5, "SO4": 1.5,
        "NH4": 1.2, "K": 7.0, "Ca": 4.0, "Mg": 1.5,
        "Fe": 50, "B": 40, "Mn": 8, "Zn": 4, "Cu": 0.8, "Mo": 0.5
    },
    "Salatalık": {
        "NO3": 12.0, "H2PO4": 1.3, "SO4": 1.2,
        "NH4": 1.1, "K": 5.8, "Ca": 3.5, "Mg": 1.2,
        "Fe": 45, "B": 35, "Mn": 6, "Zn": 4, "Cu": 0.75, "Mo": 0.5
    },
    "Marul": {
        "NO3": 10.0, "H2PO4": 1.0, "SO4": 0.8,
        "NH4": 0.8, "K": 4.5, "Ca": 3.0, "Mg": 0.8,
        "Fe": 35, "B": 25, "Mn": 4, "Zn": 3, "Cu": 0.5, "Mo": 0.4
    },
    "Çilek": {
        "NO3": 11.0, "H2PO4": 1.2, "SO4": 1.0,
        "NH4": 0.9, "K": 5.0, "Ca": 3.2, "Mg": 1.0,
        "Fe": 40, "B": 30, "Mn": 5, "Zn": 4, "Cu": 0.6, "Mo": 0.4
    }
}

# Session state için varsayılan değerleri ayarla
if 'recete' not in st.session_state:
    st.session_state.recete = {
        "NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0,
        "NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0,
        "Fe": 40, "B": 30, "Mn": 5, "Zn": 4, "Cu": 0.75, "Mo": 0.5
    }

if 'a_tank_hacmi' not in st.session_state:
    st.session_state.a_tank_hacmi = 10

if 'b_tank_hacmi' not in st.session_state:
    st.session_state.b_tank_hacmi = 10

if 'konsantrasyon' not in st.session_state:
    st.session_state.konsantrasyon = 100

# Sol tarafta menü
with st.sidebar:
    st.header("Reçete ve Tank Ayarları")
    
    # Hazır reçete seçimi
    secilen_recete = st.selectbox(
        "Hazır Reçete Seçin:",
        options=list(hazir_receteler.keys())
    )
    
    if st.button("Reçeteyi Yükle"):
        st.session_state.recete = hazir_receteler[secilen_recete].copy()
        st.success(f"{secilen_recete} reçetesi yüklendi!")
    
    # Tank ayarları
    st.subheader("Tank Ayarları")
    
    a_tank = st.number_input(
        "A Tankı Hacmi (litre):",
        min_value=1, max_value=1000,
        value=st.session_state.a_tank_hacmi
    )
    st.session_state.a_tank_hacmi = a_tank
    
    b_tank = st.number_input(
        "B Tankı Hacmi (litre):",
        min_value=1, max_value=1000,
        value=st.session_state.b_tank_hacmi
    )
    st.session_state.b_tank_hacmi = b_tank
    
    konsantrasyon = st.number_input(
        "Konsantrasyon Oranı:",
        min_value=1, max_value=1000,
        value=st.session_state.konsantrasyon
    )
    st.session_state.konsantrasyon = konsantrasyon
    
    # Bilgi kutusu
    st.info("""
    **Tank Tavsiyeleri:**
    - A Tankı: Kalsiyum içeren gübreler
    - B Tankı: Fosfat ve sülfat içeren gübreler
    - Konsantrasyon: Genellikle 100x veya 200x
    
    Tanklar eşit hacimde olmalıdır. Tank hacimleri çok küçük seçilirse, gübrelerin çözünebileceği maksimum değerleri aşabilir ve uyarı alırsınız.
    """)

# Ana sayfa düzeni
tab1, tab2 = st.tabs(["Reçete Girişi", "Gübre Hesaplama"])

# Reçete Girişi Sekmesi
with tab1:
    st.header("Reçete Değerleri")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Makro Besinler (mmol/L)")
        
        # Anyon değerleri
        st.write("**Anyonlar:**")
        no3 = st.number_input("NO3 (Nitrat):", min_value=0.0, max_value=30.0, 
                              value=float(st.session_state.recete["NO3"]), step=0.1, format="%.2f")
        h2po4 = st.number_input("H2PO4 (Fosfat):", min_value=0.0, max_value=10.0, 
                                value=float(st.session_state.recete["H2PO4"]), step=0.1, format="%.2f")
        so4 = st.number_input("SO4 (Sülfat):", min_value=0.0, max_value=10.0, 
                              value=float(st.session_state.recete["SO4"]), step=0.1, format="%.2f")
        
        # Katyon değerleri
        st.write("**Katyonlar:**")
        nh4 = st.number_input("NH4 (Amonyum):", min_value=0.0, max_value=10.0, 
                              value=float(st.session_state.recete["NH4"]), step=0.1, format="%.2f")
        k = st.number_input("K (Potasyum):", min_value=0.0, max_value=20.0, 
                            value=float(st.session_state.recete["K"]), step=0.1, format="%.2f")
        ca = st.number_input("Ca (Kalsiyum):", min_value=0.0, max_value=15.0, 
                             value=float(st.session_state.recete["Ca"]), step=0.1, format="%.2f")
        mg = st.number_input("Mg (Magnezyum):", min_value=0.0, max_value=10.0, 
                             value=float(st.session_state.recete["Mg"]), step=0.1, format="%.2f")
        
        # Reçete güncelleme
        st.session_state.recete.update({
            "NO3": no3, "H2PO4": h2po4, "SO4": so4,
            "NH4": nh4, "K": k, "Ca": ca, "Mg": mg
        })
    
    with col2:
        st.subheader("Mikro Besinler (mikromol/L)")
        
        fe = st.number_input("Fe (Demir):", min_value=0.0, max_value=100.0, 
                             value=float(st.session_state.recete["Fe"]), step=1.0, format="%.1f")
        b = st.number_input("B (Bor):", min_value=0.0, max_value=100.0, 
                            value=float(st.session_state.recete["B"]), step=1.0, format="%.1f")
        mn = st.number_input("Mn (Mangan):", min_value=0.0, max_value=50.0, 
                             value=float(st.session_state.recete["Mn"]), step=0.5, format="%.1f")
        zn = st.number_input("Zn (Çinko):", min_value=0.0, max_value=50.0, 
                             value=float(st.session_state.recete["Zn"]), step=0.5, format="%.1f")
        cu = st.number_input("Cu (Bakır):", min_value=0.0, max_value=10.0, 
                             value=float(st.session_state.recete["Cu"]), step=0.05, format="%.2f")
        mo = st.number_input("Mo (Molibden):", min_value=0.0, max_value=10.0, 
                             value=float(st.session_state.recete["Mo"]), step=0.05, format="%.2f")
        
        # Mikro besinleri güncelleme
        st.session_state.recete.update({
            "Fe": fe, "B": b, "Mn": mn, "Zn": zn, "Cu": cu, "Mo": mo
        })
    
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
    
    # İyonik denge tablosu
    st.subheader("İyonik Denge Tablosu")
    
    # Anyonlar
    anyon_data = []
    for anyon, deger in [("NO3", st.session_state.recete["NO3"]), 
                         ("H2PO4", st.session_state.recete["H2PO4"]), 
                         ("SO4", st.session_state.recete["SO4"])]:
        valens = abs(iyon_degerlikleri[anyon])
        me = deger * valens
        anyon_data.append({"Anyon": anyon, "mmol/L": deger, "me/L": me})
    
    anyon_df = pd.DataFrame(anyon_data)
    anyon_toplam_mmol = anyon_df["mmol/L"].sum()
    anyon_toplam_me = anyon_df["me/L"].sum()
    
    # Katyonlar
    katyon_data = []
    for katyon, deger in [("NH4", st.session_state.recete["NH4"]), 
                          ("K", st.session_state.recete["K"]), 
                          ("Ca", st.session_state.recete["Ca"]), 
                          ("Mg", st.session_state.recete["Mg"])]:
        valens = abs(iyon_degerlikleri[katyon])
        me = deger * valens
        katyon_data.append({"Katyon": katyon, "mmol/L": deger, "me/L": me})
    
    katyon_df = pd.DataFrame(katyon_data)
    katyon_toplam_mmol = katyon_df["mmol/L"].sum()
    katyon_toplam_me = katyon_df["me/L"].sum()
    
    # İki tabloyu yan yana göster
    col3, col4 = st.columns(2)
    
    with col3:
        st.write("**Anyonlar:**")
        st.table(anyon_df.style.format({"mmol/L": "{:.2f}", "me/L": "{:.2f}"}))
        st.write(f"**Toplam:** {anyon_toplam_mmol:.2f} mmol/L | {anyon_toplam_me:.2f} me/L")
    
    with col4:
        st.write("**Katyonlar:**")
        st.table(katyon_df.style.format({"mmol/L": "{:.2f}", "me/L": "{:.2f}"}))
        st.write(f"**Toplam:** {katyon_toplam_mmol:.2f} mmol/L | {katyon_toplam_me:.2f} me/L")
    
    # Denge durumu
    fark = abs(anyon_toplam_me - katyon_toplam_me)
    if fark < 0.5:
        st.success(f"✅ İyonik denge sağlanmış! (Fark: {fark:.2f} me/L)")
    elif fark < 1.0:
        st.warning(f"⚠️ İyonik denge kabul edilebilir sınırda. (Fark: {fark:.2f} me/L)")
    else:
        st.error(f"❌ İyonik denge sağlanamamış! (Fark: {fark:.2f} me/L)")
        
        if anyon_toplam_me > katyon_toplam_me:
            st.info("Öneri: Katyon değerlerini artırın veya anyon değerlerini azaltın.")
        else:
            st.info("Öneri: Anyon değerlerini artırın veya katyon değerlerini azaltın.")

# Gübre Hesaplama Sekmesi
with tab2:
    st.header("Gübre Hesaplama")
    
    if st.button("Gübre Formülü Hesapla"):
        # İyonik dengeyi kontrol et
        anyon_toplam, katyon_toplam = hesapla_iyonik_denge(st.session_state.recete)
        fark = abs(anyon_toplam - katyon_toplam)
        
        if fark > 1.0:
            st.warning("⚠️ İyonik denge sağlanmadan hesaplama yapılıyor. Sonuçlar ideal olmayabilir.")
        
        # Gübre hesaplama algoritması
        a_tank_gubreler = {}
        b_tank_gubreler = {}
        
        # 1. Kalsiyum ihtiyacını karşıla (A Tankı)
        if st.session_state.recete["Ca"] > 0:
            a_tank_gubreler["Kalsiyum Nitrat"] = st.session_state.recete["Ca"]
            kalan_nitrat = st.session_state.recete["NO3"] - 2 * st.session_state.recete["Ca"]
        else:
            kalan_nitrat = st.session_state.recete["NO3"]
        
        # 2. Fosfat ihtiyacını karşıla (B Tankı)
        if st.session_state.recete["H2PO4"] > 0:
            h2po4_miktar = st.session_state.recete["H2PO4"]
            
            # Eğer amonyum varsa bir kısmını MAP ile karşıla
            if st.session_state.recete["NH4"] > 0:
                map_miktar = min(h2po4_miktar, st.session_state.recete["NH4"])
                if map_miktar > 0:
                    b_tank_gubreler["Monoamonyum Fosfat"] = map_miktar
                    h2po4_miktar -= map_miktar
                    kalan_nh4 = st.session_state.recete["NH4"] - map_miktar
                else:
                    kalan_nh4 = st.session_state.recete["NH4"]
            else:
                kalan_nh4 = st.session_state.recete["NH4"]
            
            # Kalan fosfatı MKP ile karşıla
            if h2po4_miktar > 0:
                b_tank_gubreler["Monopotasyum Fosfat"] = h2po4_miktar
                kalan_k = st.session_state.recete["K"] - h2po4_miktar
            else:
                kalan_k = st.session_state.recete["K"]
        else:
            kalan_k = st.session_state.recete["K"]
            kalan_nh4 = st.session_state.recete["NH4"]
        
        # 3. Magnezyum ihtiyacını karşıla (B Tankı)
        if st.session_state.recete["Mg"] > 0:
            b_tank_gubreler["Magnezyum Sülfat"] = st.session_state.recete["Mg"]
            kalan_sulfat = st.session_state.recete["SO4"] - st.session_state.recete["Mg"]
        else:
            kalan_sulfat = st.session_state.recete["SO4"]
        
        # 4. Kalan nitrat ihtiyacını Potasyum Nitrat ile karşıla (A Tankı)
        if kalan_nitrat > 0 and kalan_k > 0:
            kno3_miktar = min(kalan_nitrat, kalan_k)
            if kno3_miktar > 0:
                a_tank_gubreler["Potasyum Nitrat"] = kno3_miktar
                kalan_nitrat -= kno3_miktar
                kalan_k -= kno3_miktar
        
        # 5. Kalan potasyum ihtiyacını Potasyum Sülfat ile karşıla (B Tankı)
        if kalan_k > 0 and kalan_sulfat > 0:
            k2so4_miktar = min(kalan_k / 2, kalan_sulfat)
            if k2so4_miktar > 0:
                b_tank_gubreler["Potasyum Sülfat"] = k2so4_miktar
                kalan_sulfat -= k2so4_miktar
                kalan_k -= 2 * k2so4_miktar
        
        # 6. Kalan amonyum ihtiyacını Amonyum Sülfat ile karşıla (B Tankı)
        if kalan_nh4 > 0 and kalan_sulfat > 0:
            nh42so4_miktar = min(kalan_nh4 / 2, kalan_sulfat)
            if nh42so4_miktar > 0:
                b_tank_gubreler["Amonyum Sülfat"] = nh42so4_miktar
                kalan_sulfat -= nh42so4_miktar
                kalan_nh4 -= 2 * nh42so4_miktar
        
        # Mikro besin hesaplama
        mikro_sonuclar = {}
        
        for element, deger in [("Fe", st.session_state.recete["Fe"]), 
                               ("B", st.session_state.recete["B"]), 
                               ("Mn", st.session_state.recete["Mn"]), 
                               ("Zn", st.session_state.recete["Zn"]), 
                               ("Cu", st.session_state.recete["Cu"]), 
                               ("Mo", st.session_state.recete["Mo"])]:
            if deger > 0:
                # Mikro besin gubresi bul
                for gubre_adi, bilgi in mikro_gubreler.items():
                    if bilgi["element"] == element:
                        mikro_sonuclar[gubre_adi] = deger / 1000  # mikromol -> mmol
                        break
        
        # Sonuç tablolarını oluştur
        
        # A Tankı sonuçları
        a_tank_data = []
        a_tank_toplam_gram = 0
        
        for gubre, mmol in a_tank_gubreler.items():
            formul = gubreler[gubre]["formul"]
            mg_per_liter = mmol * gubreler[gubre]["agirlik"]
            g_per_tank = mg_per_liter * st.session_state.konsantrasyon * st.session_state.a_tank_hacmi / 1000
            a_tank_toplam_gram += g_per_tank
            
            a_tank_data.append({
                "Gübre Adı": gubre,
                "Formül": formul,
                "mmol/L": mmol,
                "mg/L": mg_per_liter,
                "g/Tank": g_per_tank
            })
        
        a_tank_df = pd.DataFrame(a_tank_data)
        
        # B Tankı sonuçları
        b_tank_data = []
        b_tank_toplam_gram = 0
        
        for gubre, mmol in b_tank_gubreler.items():
            formul = gubreler[gubre]["formul"]
            mg_per_liter = mmol * gubreler[gubre]["agirlik"]
            g_per_tank = mg_per_liter * st.session_state.konsantrasyon * st.session_state.b_tank_hacmi / 1000
            b_tank_toplam_gram += g_per_tank
            
            b_tank_data.append({
                "Gübre Adı": gubre,
                "Formül": formul,
                "mmol/L": mmol,
                "mg/L": mg_per_liter,
                "g/Tank": g_per_tank
            })
        
        b_tank_df = pd.DataFrame(b_tank_data)
        
        # Mikro besin sonuçları
        mikro_data = []
        
        for gubre, mmol in mikro_sonuclar.items():
            formul = mikro_gubreler[gubre]["formul"]
            mikromol = mmol * 1000
            mg_per_liter = mmol * mikro_gubreler[gubre]["agirlik"]
            g_per_tank = mg_per_liter * st.session_state.konsantrasyon * st.session_state.b_tank_hacmi / 1000
            b_tank_toplam_gram += g_per_tank
            
            mikro_data.append({
                "Gübre Adı": gubre,
                "Formül": formul,
                "mikromol/L": mikromol,
                "mg/L": mg_per_liter,
                "g/Tank": g_per_tank
            })
        
        mikro_df = pd.DataFrame(mikro_data)
        
        # Tank kapasitesi kontrolü
        # Çözünürlük limitleri (yaklaşık değerler)
        a_tank_limit = st.session_state.a_tank_hacmi * 300  # g/L
        b_tank_limit = st.session_state.b_tank_hacmi * 250  # g/L
        
        # Sonuçları göster
        st.subheader("Hesaplanan Gübreler:")
        
        # A Tankı (Kalsiyum içeren)
        st.write("**A Tankı (Kalsiyum içeren):**")
        if not a_tank_df.empty:
            st.table(a_tank_df.style.format({
                "mmol/L": "{:.2f}",
                "mg/L": "{:.2f}",
                "g/Tank": "{:.2f}"
            }))
            st.write(f"**Toplam A Tankı gübresi:** {a_tank_toplam_gram:.2f} gram")
            
            # Tank kapasitesi kontrolü
            if a_tank_toplam_gram > a_tank_limit:
                st.error(f"⚠️ A Tankı kapasitesi aşılmış! ({a_tank_toplam_gram:.0f}g > {a_tank_limit:.0f}g)")
                st.info("Çözüm: Tank hacmini artırın veya konsantrasyon oranını düşürün.")
            else:
                st.success(f"✅ A Tankı kapasitesi yeterli. (Kullanım: %{(a_tank_toplam_gram/a_tank_limit)*100:.1f})")
        else:
            st.info("A Tankı için gübre eklenmedi.")
        
        # B Tankı (Fosfat ve Sülfat içeren)
        st.write("**B Tankı (Fosfat ve Sülfat içeren):**")
        if not b_tank_df.empty:
            st.table(b_tank_df.style.format({
                "mmol/L": "{:.2f}",
                "mg/L": "{:.2f}",
                "g/Tank": "{:.2f}"
            }))
            st.write(f"**B Tankına mikro besinler dahil toplam gübre:** {b_tank_toplam_gram:.2f} gram")
            
            # Tank kapasitesi kontrolü
            if b_tank_toplam_gram > b_tank_limit:
                st.error(f"⚠️ B Tankı kapas
