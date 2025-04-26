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
    "Magnezyum Nitrat": {"formul": "Mg(NO3)2.6H2O", "agirlik": 256.41, "tank": "A", "iyonlar": {"Mg": 1, "NO3": 2}},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "agirlik": 136.09, "tank": "B", "iyonlar": {"K": 1, "H2PO4": 1}},
    "Magnezyum Sulfat": {"formul": "MgSO4.7H2O", "agirlik": 246.51, "tank": "B", "iyonlar": {"Mg": 1, "SO4": 1}},
    "Potasyum Sulfat": {"formul": "K2SO4", "agirlik": 174.26, "tank": "B", "iyonlar": {"K": 2, "SO4": 1}},
    "Amonyum Sulfat": {"formul": "(NH4)2SO4", "agirlik": 132.14, "tank": "B", "iyonlar": {"NH4": 2, "SO4": 1}},
    "Monoamonyum Fosfat": {"formul": "NH4H2PO4", "agirlik": 115.03, "tank": "B", "iyonlar": {"NH4": 1, "H2PO4": 1}}
}

# Mikro elementler
mikro_gubreler = {
    "Demir EDDHA": {"formul": "Fe-EDDHA %6", "agirlik": 435.0, "element": "Fe", "yuzde": 6},
    "Demir EDTA": {"formul": "Fe-EDTA %13", "agirlik": 346.0, "element": "Fe", "yuzde": 13},
    "Demir DTPA": {"formul": "Fe-DTPA %11", "agirlik": 468.0, "element": "Fe", "yuzde": 11},
    "Borak": {"formul": "Na2B4O7.10H2O", "agirlik": 381.37, "element": "B", "yuzde": 11},
    "Borik Asit": {"formul": "H3BO3", "agirlik": 61.83, "element": "B", "yuzde": 17.5},
    "Mangan Sulfat": {"formul": "MnSO4.H2O", "agirlik": 169.02, "element": "Mn", "yuzde": 32},
    "Çinko Sulfat": {"formul": "ZnSO4.7H2O", "agirlik": 287.56, "element": "Zn", "yuzde": 23},
    "Bakır Sulfat": {"formul": "CuSO4.5H2O", "agirlik": 249.68, "element": "Cu", "yuzde": 25},
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

# Element atomik kütleleri (g/mol)
element_atomik_kutle = {
    "Fe": 55.845, "B": 10.81, "Mn": 54.938, "Zn": 65.38, "Cu": 63.546, "Mo": 95.95
}

# Session state başlatma
def initialize_session_state():
    if 'recete' not in st.session_state:
        st.session_state.recete = hazir_receteler["Genel Amaçlı"].copy()
    
    if 'a_tank' not in st.session_state:
        st.session_state.a_tank = 19
    
    if 'b_tank' not in st.session_state:
        st.session_state.b_tank = 19
    
    if 'konsantrasyon' not in st.session_state:
        st.session_state.konsantrasyon = 100
    
    if 'kuyu_suyu' not in st.session_state:
        st.session_state.kuyu_suyu = {ion: 0.0 for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]}
    
    if 'kullanilabilir_gubreler' not in st.session_state:
        st.session_state.kullanilabilir_gubreler = {gubre: False for gubre in gubreler}
    
    if 'kullanilabilir_mikro_gubreler' not in st.session_state:
        st.session_state.kullanilabilir_mikro_gubreler = {gubre: False for gubre in mikro_gubreler}
    
    if 'secilen_mikro_gubreler' not in st.session_state:
        st.session_state.secilen_mikro_gubreler = {element: None for element in ["Fe", "B", "Mn", "Zn", "Cu", "Mo"]}
    
    if 'hesaplama_log' not in st.session_state:
        st.session_state.hesaplama_log = []
    
    if 'hesaplama_sonucu' not in st.session_state:
        st.session_state.hesaplama_sonucu = None

# İyonik denge hesaplama
def hesapla_iyonik_denge(recete):
    anyon_toplam = sum(recete[ion] * abs(iyon_degerlikleri[ion]) for ion in ["NO3", "H2PO4", "SO4"])
    katyon_toplam = sum(recete[ion] * abs(iyon_degerlikleri[ion]) for ion in ["NH4", "K", "Ca", "Mg"])
    return anyon_toplam, katyon_toplam

# Besinlerin karşılanabilirliğini kontrol etme
def karsilanabilirlik_kontrolu(recete, secilen_gubreler):
    net_ihtiyac = {ion: max(0, recete[ion] - st.session_state.kuyu_suyu[ion]) 
                  for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]}
    
    # Kalsiyum Nitrat
    if "Kalsiyum Nitrat" in secilen_gubreler and net_ihtiyac["Ca"] > 0:
        net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Ca"]
        net_ihtiyac["Ca"] = 0
    
    # Magnezyum Nitrat veya Sülfat
    if "Magnezyum Nitrat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Mg"]
        net_ihtiyac["Mg"] = 0
    elif "Magnezyum Sulfat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        net_ihtiyac["SO4"] -= net_ihtiyac["Mg"]
        net_ihtiyac["Mg"] = 0
    
    # Fosfat kaynakları
    if "Monopotasyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        net_ihtiyac["K"] -= net_ihtiyac["H2PO4"]
        net_ihtiyac["H2PO4"] = 0
    elif "Monoamonyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        net_ihtiyac["NH4"] -= net_ihtiyac["H2PO4"]
        net_ihtiyac["H2PO4"] = 0
    
    # Amonyum Sülfat
    if "Amonyum Sulfat" in secilen_gubreler and net_ihtiyac["NH4"] > 0:
        net_ihtiyac["SO4"] -= net_ihtiyac["NH4"] / 2
        net_ihtiyac["NH4"] = 0
    
    # Potasyum kaynakları
    if "Potasyum Nitrat" in secilen_gubreler and net_ihtiyac["K"] > 0 and net_ihtiyac["NO3"] > 0:
        miktar = min(net_ihtiyac["K"], net_ihtiyac["NO3"])
        net_ihtiyac["K"] -= miktar
        net_ihtiyac["NO3"] -= miktar
    
    if "Potasyum Sulfat" in secilen_gubreler and net_ihtiyac["K"] > 0:
        net_ihtiyac["SO4"] -= net_ihtiyac["K"] / 2
        net_ihtiyac["K"] = 0
    
    # Negatif değerleri sıfırla
    for ion in net_ihtiyac:
        if net_ihtiyac[ion] < 0:
            net_ihtiyac[ion] = 0
    
    return [ion for ion, miktar in net_ihtiyac.items() if miktar > 0.1]

# Gübre hesaplama fonksiyonu
def gubre_hesapla():
    secilen_gubreler = [g for g, secildi in st.session_state.kullanilabilir_gubreler.items() if secildi]
    secilen_mikro_gubreler = [g for g, secildi in st.session_state.kullanilabilir_mikro_gubreler.items() if secildi]
    
    if not secilen_gubreler:
        st.error("Lütfen en az bir makro gübre seçin!")
        return None
    
    st.session_state.hesaplama_log = []
    adim = 1
    
    # Net ihtiyaç hesaplama
    net_ihtiyac = {ion: max(0, st.session_state.recete[ion] - st.session_state.kuyu_suyu[ion]) 
                  for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]}
    
    a_tank_gubreler = {}
    b_tank_gubreler = {}
    
    # Hesaplama adımları
    # 1. Kalsiyum Nitrat
    if "Kalsiyum Nitrat" in secilen_gubreler and net_ihtiyac["Ca"] > 0:
        miktar = net_ihtiyac["Ca"]
        a_tank_gubreler["Kalsiyum Nitrat"] = miktar
        net_ihtiyac["Ca"] = 0
        net_ihtiyac["NO3"] -= 2 * miktar
        st.session_state.hesaplama_log.append({
            "adim": f"Adım {adim}", 
            "aciklama": f"Kalsiyum Nitrat: {miktar:.2f} mmol/L eklendi",
            "ihtiyac": net_ihtiyac.copy()
        })
        adim += 1
    
    # 2. Magnezyum Nitrat
    if "Magnezyum Nitrat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        miktar = net_ihtiyac["Mg"]
        a_tank_gubreler["Magnezyum Nitrat"] = miktar
        net_ihtiyac["Mg"] = 0
        net_ihtiyac["NO3"] -= 2 * miktar
        st.session_state.hesaplama_log.append({
            "adim": f"Adım {adim}", 
            "aciklama": f"Magnezyum Nitrat: {miktar:.2f} mmol/L eklendi",
            "ihtiyac": net_ihtiyac.copy()
        })
        adim += 1
    
    # 3. Magnezyum Sülfat
    if "Magnezyum Sulfat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        miktar = net_ihtiyac["Mg"]
        b_tank_gubreler["Magnezyum Sulfat"] = miktar
        net_ihtiyac["Mg"] = 0
        net_ihtiyac["SO4"] -= miktar
        st.session_state.hesaplama_log.append({
            "adim": f"Adım {adim}", 
            "aciklama": f"Magnezyum Sülfat: {miktar:.2f} mmol/L eklendi",
            "ihtiyac": net_ihtiyac.copy()
        })
        adim += 1
    
    # 4. Monopotasyum Fosfat
    if "Monopotasyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        miktar = net_ihtiyac["H2PO4"]
        b_tank_gubreler["Monopotasyum Fosfat"] = miktar
        net_ihtiyac["H2PO4"] = 0
        net_ihtiyac["K"] -= miktar
        st.session_state.hesaplama_log.append({
            "adim": f"Adım {adim}", 
            "aciklama": f"Monopotasyum Fosfat: {miktar:.2f} mmol/L eklendi",
            "ihtiyac": net_ihtiyac.copy()
        })
        adim += 1
    
    # 5. Monoamonyum Fosfat
    if "Monoamonyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        miktar = net_ihtiyac["H2PO4"]
        b_tank_gubreler["Monoamonyum Fosfat"] = miktar
        net_ihtiyac["H2PO4"] = 0
        net_ihtiyac["NH4"] -= miktar
        st.session_state.hesaplama_log.append({
            "adim": f"Adım {adim}", 
            "aciklama": f"Monoamonyum Fosfat: {miktar:.2f} mmol/L eklendi",
            "ihtiyac": net_ihtiyac.copy()
        })
        adim += 1
    
    # 6. Amonyum Sülfat
    if "Amonyum Sulfat" in secilen_gubreler and net_ihtiyac["NH4"] > 0:
        miktar = net_ihtiyac["NH4"] / 2
        b_tank_gubreler["Amonyum Sulfat"] = miktar
        net_ihtiyac["NH4"] = 0
        net_ihtiyac["SO4"] -= miktar
        st.session_state.hesaplama_log.append({
            "adim": f"Adım {adim}", 
            "aciklama": f"Amonyum Sülfat: {miktar:.2f} mmol/L eklendi",
            "ihtiyac": net_ihtiyac.copy()
        })
        adim += 1
    
    # 7. Potasyum Nitrat
    if "Potasyum Nitrat" in secilen_gubreler and net_ihtiyac["K"] > 0 and net_ihtiyac["NO3"] > 0:
        miktar = min(net_ihtiyac["K"], net_ihtiyac["NO3"])
        a_tank_gubreler["Potasyum Nitrat"] = miktar
        net_ihtiyac["K"] -= miktar
        net_ihtiyac["NO3"] -= miktar
        st.session_state.hesaplama_log.append({
            "adim": f"Adım {adim}", 
            "aciklama": f"Potasyum Nitrat: {miktar:.2f} mmol/L eklendi",
            "ihtiyac": net_ihtiyac.copy()
        })
        adim += 1
    
    # 8. Potasyum Sülfat
    if "Potasyum Sulfat" in secilen_gubreler and net_ihtiyac["K"] > 0:
        miktar = net_ihtiyac["K"] / 2
        b_tank_gubreler["Potasyum Sulfat"] = miktar
        net_ihtiyac["K"] = 0
        net_ihtiyac["SO4"] -= miktar
        st.session_state.hesaplama_log.append({
            "adim": f"Adım {adim}", 
            "aciklama": f"Potasyum Sülfat: {miktar:.2f} mmol/L eklendi",
            "ihtiyac": net_ihtiyac.copy()
        })
        adim += 1
    
    # Negatif ihtiyaçları sıfırla
    negatif_ihtiyaclar = {ion: miktar for ion, miktar in net_ihtiyac.items() if miktar < -0.1}
    for ion in net_ihtiyac:
        if net_ihtiyac[ion] < 0:
            net_ihtiyac[ion] = 0
    
    # Mikro besin hesaplamaları
    mikro_sonuc = []
    for element in ["Fe", "B", "Mn", "Zn", "Cu", "Mo"]:
        gubre = st.session_state.secilen_mikro_gubreler[element]
        if gubre and st.session_state.recete[element] > 0:
            mikromol = st.session_state.recete[element]
            bilgi = mikro_gubreler[gubre]
            mmol = mikromol / 1000
            element_mol_agirligi = element_atomik_kutle[element] * (100 / bilgi["yuzde"])
            mg_l = mmol * element_mol_agirligi
            g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.b_tank) / 1000
            mikro_sonuc.append([gubre, bilgi["formul"], mikromol, mg_l, g_tank])
    
    # Kütle hesaplamaları
    a_tank_sonuc = []
    a_tank_toplam = 0
    for gubre, mmol in a_tank_gubreler.items():
        bilgi = gubreler[gubre]
        mg_l = mmol * bilgi["agirlik"]
        g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.a_tank) / 1000
        kg_tank = g_tank / 1000
        a_tank_toplam += g_tank
        a_tank_sonuc.append([gubre, bilgi["formul"], mmol, mg_l, kg_tank])
    
    b_tank_sonuc = []
    b_tank_toplam = 0
    for gubre, mmol in b_tank_gubreler.items():
        bilgi = gubreler[gubre]
        mg_l = mmol * bilgi["agirlik"]
        g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.b_tank) / 1000
        kg_tank = g_tank / 1000
        b_tank_toplam += g_tank
        b_tank_sonuc.append([gubre, bilgi["formul"], mmol, mg_l, kg_tank])
    
    return {
        "a_tank_sonuc": a_tank_sonuc,
        "b_tank_sonuc": b_tank_sonuc,
        "mikro_sonuc": mikro_sonuc,
        "a_tank_toplam": a_tank_toplam,
        "b_tank_toplam": b_tank_toplam,
        "negatif_ihtiyaclar": negatif_ihtiyaclar,
        "net_ihtiyac": net_ihtiyac
    }

# Hesaplama sonucunu gösterme
def goster_hesaplama_sonucu(hesaplama_sonucu):
    if not hesaplama_sonucu:
        return
    
    st.subheader("Hesaplama Sonuçları")
    
    # A ve B tankları
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**A Tankı (Kalsiyum içeren)**")
        if hesaplama_sonucu["a_tank_sonuc"]:
            df = pd.DataFrame(
                hesaplama_sonucu["a_tank_sonuc"],
                columns=["Gübre", "Formül", "mmol/L", "mg/L", "kg/Tank"]
            )
            st.dataframe(df.style.format({
                "mmol/L": "{:.2f}",
                "mg/L": "{:.2f}",
                "kg/Tank": "{:.3f}"
            }))
            st.write(f"**Toplam:** {hesaplama_sonucu['a_tank_toplam']/1000:.3f} kg")
        else:
            st.info("A tankı için gübre eklenmedi")
    
    with col2:
        st.markdown("**B Tankı (Fosfat ve Sülfat içeren)**")
        if hesaplama_sonucu["b_tank_sonuc"]:
            df = pd.DataFrame(
                hesaplama_sonucu["b_tank_sonuc"],
                columns=["Gübre", "Formül", "mmol/L", "mg/L", "kg/Tank"]
            )
            st.dataframe(df.style.format({
                "mmol/L": "{:.2f}",
                "mg/L": "{:.2f}",
                "kg/Tank": "{:.3f}"
            }))
            st.write(f"**Toplam:** {hesaplama_sonucu['b_tank_toplam']/1000:.3f} kg")
        else:
            st.info("B tankı için gübre eklenmedi")
    
    # Mikro besinler
    st.markdown("**Mikro Besinler**")
    if hesaplama_sonucu["mikro_sonuc"]:
        df = pd.DataFrame(
            hesaplama_sonucu["mikro_sonuc"],
            columns=["Gübre", "Formül", "µmol/L", "mg/L", "g/Tank"]
        )
        st.dataframe(df.style.format({
            "µmol/L": "{:.1f}",
            "mg/L": "{:.4f}",
            "g/Tank": "{:.2f}"
        }))
    else:
        st.info("Mikro besin eklenmedi")
    
    # Uyarılar
    if hesaplama_sonucu["negatif_ihtiyaclar"]:
        st.warning("Aşağıdaki besinler reçete ihtiyacından fazla eklendi:")
        for ion, miktar in hesaplama_sonucu["negatif_ihtiyaclar"].items():
            st.write(f"- {ion}: {-miktar:.2f} mmol/L fazla")
    
    eksik_besinler = [ion for ion, miktar in hesaplama_sonucu["net_ihtiyac"].items() if miktar > 0.1]
    if eksik_besinler:
        st.error(f"Seçilen gübrelerle karşılanamayan besinler: {', '.join(eksik_besinler)}")
    else:
        st.success("Tüm besinler seçilen gübrelerle karşılanabilir.")

# Ana uygulama
def main():
    initialize_session_state()
    
    tabs = st.tabs(["Reçete Oluşturma", "Kuyu Suyu", "Gübre Seçimi", "Gübre Hesaplama"])
    
    # Reçete Oluşturma Sekmesi
    with tabs[0]:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.header("Reçete ve Tank Ayarları")
            secilen_recete = st.selectbox("Hazır Reçete:", options=list(hazir_receteler.keys()))
            
            if st.button("Reçeteyi Yükle"):
                st.session_state.recete = hazir_receteler[secilen_recete].copy()
                st.success(f"{secilen_recete} reçetesi yüklendi!")
            
            st.subheader("Tank Ayarları")
            st.session_state.a_tank = st.number_input(
                "A Tankı Hacmi (litre):", 
                min_value=1, value=st.session_state.a_tank
            )
            st.session_state.b_tank = st.number_input(
                "B Tankı Hacmi (litre):", 
                min_value=1, value=st.session_state.b_tank
            )
            st.session_state.konsantrasyon = st.number_input(
                "Konsantrasyon Oranı:", 
                min_value=1, value=st.session_state.konsantrasyon
            )
        
        with col2:
            st.header("Reçete Değerleri")
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.subheader("Anyonlar (mmol/L)")
                for ion in ["NO3", "H2PO4", "SO4"]:
                    st.session_state.recete[ion] = st.number_input(
                        f"{ion}:", 
                        value=st.session_state.recete[ion], 
                        min_value=0.0, step=0.1, format="%.2f"
                    )
            
            with col_b:
                st.subheader("Katyonlar (mmol/L)")
                for ion in ["NH4", "K", "Ca", "Mg"]:
                    st.session_state.recete[ion] = st.number_input(
                        f"{ion}:", 
                        value=st.session_state.recete[ion], 
                        min_value=0.0, step=0.1, format="%.2f"
                    )
            
            st.subheader("Mikro Besinler (µmol/L)")
            col_m1, col_m2, col_m3 = st.columns(3)
            for col, elements in [(col_m1, ["Fe", "Mn"]), (col_m2, ["B", "Zn"]), (col_m3, ["Cu", "Mo"])]:
                with col:
                    for element in elements:
                        st.session_state.recete[element] = st.number_input(
                            f"{element}:", 
                            value=st.session_state.recete[element], 
                            min_value=0.0, step=0.1, format="%.1f"
                        )
            
            st.subheader("İyonik Denge")
            anyon_toplam, katyon_toplam = hesapla_iyonik_denge(st.session_state.recete)
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown("**Anyonlar**")
                anyon_df = pd.DataFrame([
                    [ion, st.session_state.recete[ion], st.session_state.recete[ion] * abs(iyon_degerlikleri[ion])]
                    for ion in ["NO3", "H2PO4", "SO4"]
                ], columns=["İyon", "mmol/L", "meq/L"])
                st.dataframe(anyon_df.style.format({"mmol/L": "{:.2f}", "meq/L": "{:.2f}"}))
                st.write(f"**Toplam:** {anyon_toplam:.2f} meq/L")
            
            with col_d2:
                st.markdown("**Katyonlar**")
                katyon_df = pd.DataFrame([
                    [ion, st.session_state.recete[ion], st.session_state.recete[ion] * abs(iyon_degerlikleri[ion])]
                    for ion in ["NH4", "K", "Ca", "Mg"]
                ], columns=["İyon", "mmol/L", "meq/L"])
                st.dataframe(katyon_df.style.format({"mmol/L": "{:.2f}", "meq/L": "{:.2f}"}))
                st.write(f"**Toplam:** {katyon_toplam:.2f} meq/L")
            
            fark = abs(anyon_toplam - katyon_toplam)
            if fark < 0.5:
                st.success(f"İyonik denge iyi! (Fark: {fark:.2f} meq/L)")
            elif fark < 1.0:
                st.warning(f"İyonik denge kabul edilebilir. (Fark: {fark:.2f} meq/L)")
            else:
                st.error(f"İyonik denge bozuk! (Fark: {fark:.2f} meq/L)")
    
    # Kuyu Suyu Sekmesi
    with tabs[1]:
        st.header("Kuyu Suyu Analizi")
        st.info("Kuyu suyu kullanıyorsanız, içindeki iyonları girin")
        
        col1, col2 = st.columns(2)
        for col, ions in [(col1, ["NO3", "H2PO4", "SO4"]), (col2, ["NH4", "K", "Ca", "Mg"])]:
            with col:
                for ion in ions:
                    st.session_state.kuyu_suyu[ion] = st.number_input(
                        f"{ion} (mmol/L):", 
                        value=st.session_state.kuyu_suyu[ion], 
                        min_value=0.0, step=0.05, format="%.2f"
                    )
    
    # Gübre Seçimi Sekmesi
    with tabs[2]:
        st.header("Elimdeki Gübreler")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Makro Gübreler")
            a_tank_gubreler = [g for g, b in gubreler.items() if b["tank"] == "A"]
            b_tank_gubreler = [g for g, b in gubreler.items() if b["tank"] == "B"]
            
            st.markdown("**A Tankı Gübreleri**")
            for gubre in a_tank_gubreler:
                st.session_state.kullanilabilir_gubreler[gubre] = st.checkbox(
                    f"{gubre} ({gubreler[gubre]['formul']})",
                    value=st.session_state.kullanilabilir_gubreler[gubre]
                )
            
            st.markdown("**B Tankı Gübreleri**")
            for gubre in b_tank_gubreler:
                st.session_state.kullanilabilir_gubreler[gubre] = st.checkbox(
                    f"{gubre} ({gubreler[gubre]['formul']})",
                    value=st.session_state.kullanilabilir_gubreler[gubre]
                )
        
        with col2:
            st.subheader("Mikro Gübreler")
            for element in ["Fe", "B", "Mn", "Zn", "Cu", "Mo"]:
                gubreler = [g for g, b in mikro_gubreler.items() if b["element"] == element]
                secim = st.radio(
                    f"{element} kaynağı seçin:",
                    options=["Seçilmedi"] + gubreler,
                    index=0 if st.session_state.secilen_mikro_gubreler[element] is None 
                          else gubreler.index(st.session_state.secilen_mikro_gubreler[element]) + 1,
                    key=f"mikro_{element}"
                )
                st.session_state.secilen_mikro_gubreler[element] = None if secim == "Seçilmedi" else secim
        
        # Seçilen gübreleri göster
        secilen_gubreler = [g for g, secildi in st.session_state.kullanilabilir_gubreler.items() if secildi]
        secilen_mikro_gubreler = [g for g, secildi in st.session
