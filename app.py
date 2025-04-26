import streamlit as st
import pandas as pd
import numpy as np

# Sayfa ayarları
st.set_page_config(page_title="Hidrobot", page_icon="🤖", layout="wide")

# Başlık ve açıklama
st.title("🤖 Hidrobot")
st.markdown("Hidroponik besin çözeltisi hesaplama aracı")

# İyon değerlikleri
iyon_degerlikleri = {
    "NO3": -1, "H2PO4": -1, "SO4": -2,
    "NH4": 1, "K": 1, "Ca": 2, "Mg": 2
}

# Gübre bilgileri (Kalsiyum Amonyum Nitrat kaldırıldı)
gubreler = {
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2.4H2O", "agirlik": 236.15, "tank": "A", "iyonlar": {"Ca": 1, "NO3": 2}},
    "Potasyum Nitrat": {"formul": "KNO3", "agirlik": 101.10, "tank": "A", "iyonlar": {"K": 1, "NO3": 1}},
    "Magnezyum Nitrat": {"formul": "Mg(NO3)2.6H2O", "agirlik": 256.41, "tank": "A", "iyonlar": {"Mg": 1, "NO3": 2}},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "agirlik": 136.09, "tank": "B", "iyonlar": {"K": 1, "H2PO4": 1}},
    "Magnezyum Sülfat": {"formul": "MgSO4.7H2O", "agirlik": 246.51, "tank": "B", "iyonlar": {"Mg": 1, "SO4": 1}},
    "Potasyum Sülfat": {"formul": "K2SO4", "agirlik": 174.26, "tank": "B", "iyonlar": {"K": 2, "SO4": 1}},
    "Amonyum Sülfat": {"formul": "(NH4)2SO4", "agirlik": 132.14, "tank": "B", "iyonlar": {"NH4": 2, "SO4": 1}},
    "Monoamonyum Fosfat": {"formul": "NH4H2PO4", "agirlik": 115.03, "tank": "B", "iyonlar": {"NH4": 1, "H2PO4": 1}}
}

# gubreler sözlüğünün doğru tanımlandığını doğrula
for gubre_adi, gubre_bilgi in gubreler.items():
    gerekli_anahtarlar = ["formul", "agirlik", "tank", "iyonlar"]
    eksik_anahtarlar = [anahtar for anahtar in gerekli_anahtarlar if anahtar not in gubre_bilgi]
    
    if eksik_anahtarlar:
        st.error(f"Hata: '{gubre_adi}' gübresinde eksik bilgiler var: {', '.join(eksik_anahtarlar)}")
        st.stop()

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
    st.session_state.recete = {
        "NO3": 9.5, "H2PO4": 1.0, "SO4": 0.5, "NH4": 0.5, "K": 5.0, "Ca": 2.25, "Mg": 0.75
    }

if 'a_tank' not in st.session_state:
    st.session_state.a_tank = 19

if 'b_tank' not in st.session_state:
    st.session_state.b_tank = 19

if 'konsantrasyon' not in st.session_state:
    st.session_state.konsantrasyon = 100

if 'kuyu_suyu' not in st.session_state:
    st.session_state.kuyu_suyu = {
        "NO3": 0.0, "H2PO4": 0.0, "SO4": 0.0, "NH4": 0.0, "K": 0.0, "Ca": 0.0, "Mg": 0.0
    }

# YENİ: kullanılabilir_gubreler ayarı güncellendi
if 'kullanilabilir_gubreler' not in st.session_state:
    gubre_anahtarlari = list(gubreler.keys())
    st.session_state.kullanilabilir_gubreler = {}
    for gubre in gubre_anahtarlari:
        st.session_state.kullanilabilir_gubreler[gubre] = False

if 'kullanilabilir_mikro_gubreler' not in st.session_state:
    st.session_state.kullanilabilir_mikro_gubreler = {gubre: False for gubre in mikro_gubreler.keys()}

if 'secilen_mikro_gubreler' not in st.session_state:
    st.session_state.secilen_mikro_gubreler = {
        "Fe": None, "B": None, "Mn": None, "Zn": None, "Cu": None, "Mo": None
    }

if 'hesaplama_log' not in st.session_state:
    st.session_state.hesaplama_log = []

# Session state sıfırlama butonu
with st.sidebar:
    st.header("Ayarlar")
    if st.button("Session State'i Sıfırla"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.recete = {
            "NO3": 9.5, "H2PO4": 1.0, "SO4": 0.5, "NH4": 0.5, "K": 5.0, "Ca": 2.25, "Mg": 0.75
        }
        st.session_state.a_tank = 19
        st.session_state.b_tank = 19
        st.session_state.konsantrasyon = 100
        st.session_state.kuyu_suyu = {
            "NO3": 0.0, "H2PO4": 0.0, "SO4": 0.0, "NH4": 0.0, "K": 0.0, "Ca": 0.0, "Mg": 0.0
        }
        # YENİ: kullanılabilir_gubreler sıfırlama kodu güncellendi
        gubre_anahtarlari = list(gubreler.keys())
        st.session_state.kullanilabilir_gubreler = {}
        for gubre in gubre_anahtarlari:
            st.session_state.kullanilabilir_gubreler[gubre] = False
        
        st.session_state.kullanilabilir_mikro_gubreler = {gubre: False for gubre in mikro_gubreler.keys()}
        st.session_state.secilen_mikro_gubreler = {
            "Fe": None, "B": None, "Mn": None, "Zn": None, "Cu": None, "Mo": None
        }
        st.session_state.hesaplama_log = []
        st.success("Session state sıfırlandı!")

# İyonik denge hesaplama
def hesapla_iyonik_denge(recete):
    anyon_toplam = sum(float(recete[ion]) * abs(iyon_degerlikleri[ion]) for ion in ["NO3", "H2PO4", "SO4"])
    katyon_toplam = sum(float(recete[ion]) * abs(iyon_degerlikleri[ion]) for ion in ["NH4", "K", "Ca", "Mg"])
    return anyon_toplam, katyon_toplam
   
# ⬇️ YENİ EKLENECEK: İyonik dengeyi otomatik düzeltme fonksiyonu
def otomatik_iyon_duzelt(recete, hedef_fark=0.5):
    anyon_toplam, katyon_toplam = hesapla_iyonik_denge(recete)
    fark = anyon_toplam - katyon_toplam
    
    if abs(fark) <= hedef_fark:
        return recete, "Zaten dengede."
    
    if fark > 0:  # Aniyon fazlası var
        recete["K"] += fark
        duzeltme = f"K (potasyum) artırıldı: +{fark:.2f} mmol/L"
    else:  # Katyon fazlası var
        recete["NO3"] += abs(fark)
        duzeltme = f"NO3 (nitrat) artırıldı: +{abs(fark):.2f} mmol/L"
    
    return recete, duzeltme

# Simulasyon ile besinlerin karşılanıp karşılanamayacağını kontrol etme
def karsilanabilirlik_kontrolu(recete, secilen_gubreler):
    # Seçilen gübrelerin geçerli olup olmadığını kontrol et
    gecerli_secilen_gubreler = []
    for gubre in secilen_gubreler:
        if gubre in gubreler:
            gecerli_secilen_gubreler.append(gubre)
        else:
            st.warning(f"Karşılanabilirlik kontrolünde: '{gubre}' gübresi tanımlı değil!")
    
    net_ihtiyac = {ion: max(0, float(recete[ion])) for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]}
    
    if "Kalsiyum Nitrat" in gecerli_secilen_gubreler and net_ihtiyac["Ca"] > 0:
        net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Ca"]
        net_ihtiyac["Ca"] = 0
    if "Magnezyum Nitrat" in gecerli_secilen_gubreler and net_ihtiyac["Mg"] > 0:
        net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Mg"]
        net_ihtiyac["Mg"] = 0
    elif "Magnezyum Sülfat" in gecerli_secilen_gubreler and net_ihtiyac["Mg"] > 0:
        net_ihtiyac["SO4"] -= net_ihtiyac["Mg"]
        net_ihtiyac["Mg"] = 0
    if "Monopotasyum Fosfat" in gecerli_secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        net_ihtiyac["K"] -= net_ihtiyac["H2PO4"]
        net_ihtiyac["H2PO4"] = 0
    elif "Monoamonyum Fosfat" in gecerli_secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        net_ihtiyac["NH4"] -= net_ihtiyac["H2PO4"]
        net_ihtiyac["H2PO4"] = 0
    if "Amonyum Sülfat" in gecerli_secilen_gubreler and net_ihtiyac["NH4"] > 0:
        as_miktar = min(net_ihtiyac["NH4"] / 2, net_ihtiyac["SO4"])
        net_ihtiyac["NH4"] -= 2 * as_miktar
        net_ihtiyac["SO4"] -= as_miktar
    if "Potasyum Nitrat" in gecerli_secilen_gubreler and net_ihtiyac["K"] > 0 and net_ihtiyac["NO3"] > 0:
        kn_miktar = min(net_ihtiyac["K"], net_ihtiyac["NO3"])
        net_ihtiyac["K"] -= kn_miktar
        net_ihtiyac["NO3"] -= kn_miktar
    if "Potasyum Sülfat" in gecerli_secilen_gubreler and net_ihtiyac["K"] > 0:
        net_ihtiyac["SO4"] -= net_ihtiyac["K"] / 2
        net_ihtiyac["K"] = 0
    for iyon in net_ihtiyac:
        if net_ihtiyac[iyon] < 0:
            net_ihtiyac[iyon] = 0
    return [iyon for iyon, miktar in net_ihtiyac.items() if miktar > 0.1]

# Ana düzen
tabs = st.tabs(["Reçete Oluşturma", "Kuyu Suyu", "Gübre Seçimi", "Gübre Hesaplama"])

# Tab 1: Reçete Oluşturma
with tabs[0]:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.header("Reçete ve Tank Ayarları")
        secilen_recete = st.selectbox("Hazır Reçete:", options=list(hazir_receteler.keys()))
        if st.button("Reçeteyi Yükle"):
            st.session_state.recete = hazir_receteler[secilen_recete].copy()
            st.success(f"{secilen_recete} reçetesi yüklendi!")
        st.subheader("Tank Ayarları")
        st.session_state.a_tank = st.number_input("A Tankı Hacmi (litre):", min_value=1, max_value=1000, value=st.session_state.a_tank)
        st.session_state.b_tank = st.number_input("B Tankı Hacmi (litre):", min_value=1, max_value=1000, value=st.session_state.b_tank)
        st.session_state.konsantrasyon = st.number_input("Konsantrasyon Oranı:", min_value=1, max_value=1000, value=st.session_state.konsantrasyon)
        st.info("""
        **Tank Ayarları Bilgisi:**
        - **A Tankı**: Kalsiyum içeren gübreler (örn. kalsiyum nitrat) için.
        - **B Tankı**: Fosfat ve sülfat içeren gübreler için.
        - **Konsantrasyon Oranı**: Stok çözeltinin son kullanım konsantrasyonundan kaç kat daha konsantre olduğunu belirtir.
        """)
    with col2:
        st.header("Reçete Değerleri")
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Anyonlar (mmol/L)")
            for ion in ["NO3", "H2PO4", "SO4"]:
                st.session_state.recete[ion] = st.number_input(
                    f"{ion}:", value=float(st.session_state.recete[ion]), min_value=0.0, max_value=30.0, step=0.1, format="%.2f", key=f"{ion}_input"
                )
        with col_b:
            st.subheader("Katyonlar (mmol/L)")
            for ion in ["NH4", "K", "Ca", "Mg"]:
                st.session_state.recete[ion] = st.number_input(
                    f"{ion}:", value=float(st.session_state.recete[ion]), min_value=0.0, max_value=20.0, step=0.1, format="%.2f", key=f"{ion}_input"
                )
        st.subheader("Mikro Besinler (mikromol/L)")
        col_m1, col_m2, col_m3 = st.columns(3)
        for col, elements in [(col_m1, ["Fe", "Mn"]), (col_m2, ["B", "Zn"]), (col_m3, ["Cu", "Mo"])]:
            with col:
                for element in elements:
                    st.session_state.recete[element] = st.number_input(
                        f"{element}:", value=float(st.session_state.recete.get(element, 0.0)), min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key=f"{element}_input"
                    )
        st.subheader("İyonik Denge")
        anyon_toplam, katyon_toplam = hesapla_iyonik_denge(st.session_state.recete)
        col_denge1, col_denge2 = st.columns(2)
       
        # ⬇️ YENİ EKLENECEK: Otomatik İyonik Denge Butonu
        if st.button("🔧 İyonik Dengeyi Otomatik Düzelt"):
         st.session_state.recete, mesaj = otomatik_iyon_duzelt(st.session_state.recete)
        st.success(f"✅ {mesaj}")
        with col_denge1:
            anyon_df = pd.DataFrame(
                [[ion, st.session_state.recete[ion], st.session_state.recete[ion] * abs(iyon_degerlikleri[ion])] for ion in ["NO3", "H2PO4", "SO4"]],
                columns=["Anyon", "mmol/L", "me/L"]
            )
            st.write("**Anyonlar:**")
            st.dataframe(anyon_df.style.format({"mmol/L": "{:.2f}", "me/L": "{:.2f}"}))
            st.write(f"**Toplam:** {anyon_toplam:.2f} me/L")
        with col_denge2:
            katyon_df = pd.DataFrame(
                [[ion, st.session_state.recete[ion], st.session_state.recete[ion] * abs(iyon_degerlikleri[ion])] for ion in ["NH4", "K", "Ca", "Mg"]],
                columns=["Katyon", "mmol/L", "me/L"]
            )
            st.write("**Katyonlar:**")
            st.dataframe(katyon_df.style.format({"mmol/L": "{:.2f}", "me/L": "{:.2f}"}))
            st.write(f"**Toplam:** {katyon_toplam:.2f} me/L")
        fark = abs(anyon_toplam - katyon_toplam)
        if fark < 0.5:
            st.success(f"✅ İyonik denge iyi durumda! (Fark: {fark:.2f} me/L)")
        elif fark < 1.0:
            st.warning(f"⚠️ İyonik denge kabul edilebilir sınırda. (Fark: {fark:.2f} me/L)")
        else:
            st.error(f"❌ İyonik denge bozuk! (Fark: {fark:.2f} me/L)")
            st.markdown("**İyileştirme Önerisi:** " + ("Anyon fazlası var. Daha fazla katyon ekleyin." if anyon_toplam > katyon_toplam else "Katyon fazlası var. Daha fazla anyon ekleyin."))

# Tab 2: Kuyu Suyu
with tabs[1]:
    st.header("Kuyu Suyu Analizi")
    st.info("Kuyu suyu kullanıyorsanız, içindeki iyonları girerek hesaplamada dikkate alınmasını sağlayabilirsiniz.")
    col1, col2 = st.columns(2)
    for col, ions in [(col1, ["NO3", "H2PO4", "SO4"]), (col2, ["NH4", "K", "Ca", "Mg"])]:
        with col:
            st.subheader(f"{'Anyonlar' if col == col1 else 'Katyonlar'} (mmol/L)")
            for ion in ions:
                st.session_state.kuyu_suyu[ion] = st.number_input(
                    f"{ion}:", value=float(st.session_state.kuyu_suyu[ion]), min_value=0.0, max_value=10.0, step=0.05, format="%.2f", key=f"kuyu_{ion}_input"
                )
    if sum(st.session_state.kuyu_suyu.values()) > 0:
        st.success("✅ Kuyu suyu değerleri kaydedildi ve hesaplamalarda dikkate alınacak.")
    else:
        st.info("ℹ️ Şu anda kuyu suyu değeri girilmemiş. Saf su varsayılacak.")

# Tab 3: Gübre Seçimi
with tabs[2]:
    st.header("Elimdeki Gübreler")
    st.info("Kullanmak istediğiniz gübreleri seçin. Hesaplamalar sadece seçilen gübrelerle yapılır.")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Makro Gübreler")
        a_tank_gubreler = [gubre for gubre in gubreler.keys() if gubreler[gubre]["tank"] == "A"]
        b_tank_gubreler = [gubre for gubre in gubreler.keys() if gubreler[gubre]["tank"] == "B"]
        st.markdown("**A Tankı Gübreleri**")
        for gubre in a_tank_gubreler:
            # YENİ: checkbox ve anahtar için aynı kesin string değeri kullan
            st.session_state.kullanilabilir_gubreler[gubre] = st.checkbox(
                f"☐ {gubre} ({gubreler[gubre]['formul']})",
                value=st.session_state.kullanilabilir_gubreler.get(gubre, False),
                key=f"checkbox_{gubre}"
            )
        st.markdown("**B Tankı Gübreleri**")
        for gubre in b_tank_gubreler:
            # YENİ: checkbox ve anahtar için aynı kesin string değeri kullan
            st.session_state.kullanilabilir_gubreler[gubre] = st.checkbox(
                f"☐ {gubre} ({gubreler[gubre]['formul']})",
                value=st.session_state.kullanilabilir_gubreler.get(gubre, False),
                key=f"checkbox_b_{gubre}"
            )
    with col2:
        st.subheader("Mikro Gübreler")
        mikro_element_gruplari = {}
        for gubre, bilgi in mikro_gubreler.items():
            mikro_element_gruplari.setdefault(bilgi["element"], []).append(gubre)
        for element, gubreler_listesi in mikro_element_gruplari.items():
            st.markdown(f"**{element} Kaynağı**")
            secilen_gubre = st.radio(
                f"{element} için gübre seçimi",
                options=["Seçilmedi"] + gubreler_listesi,
                index=0 if st.session_state.secilen_mikro_gubreler[element] not in gubreler_listesi else gubreler_listesi.index(st.session_state.secilen_mikro_gubreler[element]) + 1,
                key=f"radio_{element}"
            )
            st.session_state.secilen_mikro_gubreler[element] = None if secilen_gubre == "Seçilmedi" else secilen_gubre
            for gubre in gubreler_listesi:
                st.session_state.kullanilabilir_mikro_gubreler[gubre] = (gubre == secilen_gubre)
    # Seçilen gübreleri al
    secilen_gubreler = [gubre for gubre, secildi in st.session_state.kullanilabilir_gubreler.items() if secildi]
    secilen_mikro_gubreler = [gubre for element, gubre in st.session_state.secilen_mikro_gubreler.items() if gubre]
    
    # YENİ: Seçilen gübrelerin gübreler sözlüğünde olup olmadığını kontrol et
    gecerli_secilen_gubreler = []
    gecersiz_secilen_gubreler = []
    for gubre in secilen_gubreler:
        if gubre in gubreler:
            gecerli_secilen_gubreler.append(gubre)
        else:
            gecersiz_secilen_gubreler.append(gubre)
    
    st.subheader("Seçilen Gübreler")
    if secilen_gubreler:
        st.write("**Makro Gübreler:**")
        for gubre in secilen_gubreler:
            if gubre in gubreler:
                st.write(f"✓ {gubre} ({gubreler[gubre]['formul']})")
            else:
                st.warning(f"Uyarı: '{gubre}' gübresi tanımlı değil!")
    else:
        st.warning("Henüz makro gübre seçmediniz!")
    if secilen_mikro_gubreler:
        st.write("**Mikro Gübreler:**")
        for gubre in secilen_mikro_gubreler:
            if gubre in mikro_gubreler:
                st.write(f"✓ {gubre} ({mikro_gubreler[gubre]['formul']})")
            else:
                st.warning(f"Uyarı: '{gubre}' mikro gübresi tanımlı değil!")
    else:
        st.warning("Henüz mikro gübre seçmediniz!")
    # Hata ayıklama
    with st.expander("Hata Ayıklama: Gübre Durumu"):
        st.write("**Gübreler sözlüğündeki anahtarlar:**", list(gubreler.keys()))
        st.write("**Seçilen Makro Gübreler:**", secilen_gubreler)
        st.write("**Geçerli Seçilen Gübreler:**", gecerli_secilen_gubreler)
        st.write("**Geçersiz Seçilen Gübreler:**", gecersiz_secilen_gubreler)
        
        # Kullanılabilir gübreler sözlüğünü göster
        st.write("**Kullanılabilir Gübreler Durumu:**")
        for gubre, durum in st.session_state.kullanilabilir_gubreler.items():
            st.write(f"{gubre}: {durum}")
            
    if secilen_gubreler:
        eksik_besinler = karsilanabilirlik_kontrolu(st.session_state.recete, secilen_gubreler)
        if eksik_besinler:
            st.error(f"⚠️ Seçilen gübrelerle karşılanamayan besinler: {', '.join(eksik_besinler)}")
            st.markdown("**Önerilen Gübreler:**")
            for besin in eksik_besinler:
                # YENİ: Hata veren kod düzeltildi - try/except ekledik
                oneriler = []
                for gubre, bilgi in gubreler.items():
                    try:
                        if "iyonlar" in bilgi and besin in bilgi["iyonlar"] and gubre not in secilen_gubreler:
                            oneriler.append(f"☐ {gubre} ({bilgi['formul']})")
                    except Exception as e:
                        st.error(f"Hata: '{gubre}' gübresi önerileri oluştururken sorun: {str(e)}")
                st.markdown(f"- {besin} için: {', '.join(oneriler) if oneriler else 'Reçeteyi gözden geçirin.'}")
        else:
            st.success("✅ Seçilen gübrelerle tüm besinler karşılanabilir.")

# Tab 4: Gübre Hesaplama
with tabs[3]:
    st.header("Gübre Hesaplama")
    if st.button("Gübre Hesapla", type="primary"):
        # Seçilen gübreleri al
        secilen_gubreler = [gubre for gubre, secildi in st.session_state.kullanilabilir_gubreler.items() if secildi]
        secilen_mikro_gubreler = [gubre for element, gubre in st.session_state.secilen_mikro_gubreler.items() if gubre]
        
        # YENİ: Seçilen gübreleri ve gübreler sözlüğünü kontrol et (hata ayıklama)
        st.write("**Hata Ayıklama:** Seçilen gübreler:", secilen_gubreler)
        st.write("**Hata Ayıklama:** Gübreler sözlüğündeki anahtarlar:", list(gubreler.keys()))
        
        # YENİ: Geçerli seçilen gübreleri filtrele
        gecerli_gubreler = [gubre for gubre in secilen_gubreler if gubre in gubreler]
        gecersiz_gubreler = [gubre for gubre in secilen_gubreler if gubre not in gubreler]
        
        if gecersiz_gubreler:
            st.error(f"Seçilen gübrelerden {len(gecersiz_gubreler)} tanesi tanımlı değil: {gecersiz_gubreler}")
            st.warning("Hesaplama sadece tanımlı gübrelerle yapılacak.")
        
        # Hata ayıklama logu
        st.session_state.hesaplama_log = []
        st.session_state.hesaplama_log.append({
            "adım": "Başlangıç", "açıklama": f"Seçilen makro gübreler: {gecerli_gubreler}", "ihtiyac": {}
        })
        
        if not gecerli_gubreler:
            st.error("Lütfen 'Gübre Seçimi' sekmesinden en az bir makro gübre seçin!")
            st.warning(f"Hata Ayıklama: Geçerli gübre seçilmedi. Tüm gübre durumu: {st.session_state.kullanilabilir_gubreler}")
        else:
            net_ihtiyac = {
                ion: max(0, float(st.session_state.recete[ion]) - float(st.session_state.kuyu_suyu[ion]))
                for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]
            }
            a_tank_gubreler = {}
            b_tank_gubreler = {}
            adim = 1
            st.session_state.hesaplama_log.append({
                "adım": "Kuyu Suyu Sonrası", "açıklama": "Kuyu suyu sonrası ihtiyaçlar",
                "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
            })
            # 1. Kalsiyum Nitrat
            if "Kalsiyum Nitrat" in gecerli_gubreler and net_ihtiyac["Ca"] > 0:
                ca_miktar = net_ihtiyac["Ca"]
                a_tank_gubreler["Kalsiyum Nitrat"] = ca_miktar
                net_ihtiyac["Ca"] = 0
                net_ihtiyac["NO3"] -= 2 * ca_miktar
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "açıklama": f"Kalsiyum Nitrat: {ca_miktar:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1
            # 2. Magnezyum Nitrat
            if "Magnezyum Nitrat" in gecerli_gubreler and net_ihtiyac["Mg"] > 0:
                mg_miktar = net_ihtiyac["Mg"]
                a_tank_gubreler["Magnezyum Nitrat"] = mg_miktar
                net_ihtiyac["Mg"] = 0
                net_ihtiyac["NO3"] -= 2 * mg_miktar
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "açıklama": f"Magnezyum Nitrat: {mg_miktar:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1
            # 3. Magnezyum Sülfat
            if "Magnezyum Sülfat" in gecerli_gubreler and net_ihtiyac["Mg"] > 0:
                mg_miktar = net_ihtiyac["Mg"]
                b_tank_gubreler["Magnezyum Sülfat"] = mg_miktar
                net_ihtiyac["Mg"] = 0
                net_ihtiyac["SO4"] -= mg_miktar
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "açıklama": f"Magnezyum Sülfat: {mg_miktar:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1
            # 4. Monopotasyum Fosfat
            if "Monopotasyum Fosfat" in gecerli_gubreler and net_ihtiyac["H2PO4"] > 0:
                mkp_miktar = net_ihtiyac["H2PO4"]
                b_tank_gubreler["Monopotasyum Fosfat"] = mkp_miktar
                net_ihtiyac["H2PO4"] = 0
                net_ihtiyac["K"] -= mkp_miktar
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "açıklama": f"Monopotasyum Fosfat: {mkp_miktar:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1
            # 5. Monoamonyum Fosfat
            if "Monoamonyum Fosfat" in gecerli_gubreler and net_ihtiyac["H2PO4"] > 0:
                map_miktar = net_ihtiyac["H2PO4"]
                b_tank_gubreler["Monoamonyum Fosfat"] = map_miktar
                net_ihtiyac["H2PO4"] = 0
                net_ihtiyac["NH4"] -= map_miktar
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "açıklama": f"Monoamonyum Fosfat: {map_miktar:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1
            # 6. Amonyum Sülfat
            if "Amonyum Sülfat" in gecerli_gubreler and net_ihtiyac["NH4"] > 0:
                as_miktar = net_ihtiyac["NH4"] / 2
                b_tank_gubreler["Amonyum Sülfat"] = as_miktar
                net_ihtiyac["NH4"] = 0
                net_ihtiyac["SO4"] -= as_miktar
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "açıklama": f"Amonyum Sülfat: {as_miktar:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1
            # 7. Potasyum Nitrat
            if "Potasyum Nitrat" in gecerli_gubreler and net_ihtiyac["K"] > 0 and net_ihtiyac["NO3"] > 0:
                kn_miktar = min(net_ihtiyac["K"], net_ihtiyac["NO3"])
                a_tank_gubreler["Potasyum Nitrat"] = kn_miktar
                net_ihtiyac["K"] -= kn_miktar
                net_ihtiyac["NO3"] -= kn_miktar
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "açıklama": f"Potasyum Nitrat: {kn_miktar:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1
            # 8. Potasyum Sülfat
            if "Potasyum Sülfat" in gecerli_gubreler and net_ihtiyac["K"] > 0:
                ks_miktar = net_ihtiyac["K"] / 2
                b_tank_gubreler["Potasyum Sülfat"] = ks_miktar
                net_ihtiyac["K"] = 0
                net_ihtiyac["SO4"] -= ks_miktar
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "açıklama": f"Potasyum Sülfat: {ks_miktar:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1
            # Negatif ihtiyaçları sıfırla
            negatif_ihtiyaclar = {iyon: miktar for iyon, miktar in net_ihtiyac.items() if miktar < -0.1}
            for iyon in net_ihtiyac:
                if net_ihtiyac[iyon] < 0:
                    net_ihtiyac[iyon] = 0
            # Mikro besin hesaplamaları
            mikro_sonuc = []
            for element, label in [("Fe", "Demir"), ("B", "Bor"), ("Mn", "Mangan"), ("Zn", "Çinko"), ("Cu", "Bakır"), ("Mo", "Molibden")]:
                secilen_gubre = st.session_state.secilen_mikro_gubreler[element]
                if secilen_gubre and element in st.session_state.recete and float(st.session_state.recete[element]) > 0:
                    try:
                        mikromol = float(st.session_state.recete[element])
                        gubre_bilgi = mikro_gubreler[secilen_gubre]
                        mmol = mikromol / 1000
                        element_mol_agirligi = element_atomik_kutle[element] * (100 / gubre_bilgi["yuzde"])
                        mg_l = mmol * element_mol_agirligi
                        g_tank = (mg_l * float(st.session_state.konsantrasyon) * float(st.session_state.b_tank)) / 1000
                        mikro_sonuc.append([secilen_gubre, gubre_bilgi["formul"], mikromol, mg_l, g_tank])
                    except (TypeError, ValueError) as e:
                        st.error(f"Mikro besin '{element}' hesaplanırken hata: {str(e)}")
            # Kütle hesaplamaları
            a_tank_sonuc = []
            a_tank_toplam = 0
            st.session_state.hesaplama_log.append({
                "adım": "A Tankı Öncesi", "açıklama": f"A Tankı gübreleri: {a_tank_gubreler}", "ihtiyac": {}
            })
            for gubre, mmol in a_tank_gubreler.items():
                try:
                    if gubre not in gubreler:
                        st.session_state.hesaplama_log.append({
                            "adım": f"Hata - A Tankı - {gubre}", 
                            "açıklama": f"Gübre '{gubre}' gubreler sözlüğünde bulunamadı. Tanımlı gübreler: {list(gubreler.keys())}", 
                            "ihtiyac": {}
                        })
                        continue
                    formul = gubreler[gubre]["formul"]
                    agirlik = float(gubreler[gubre]["agirlik"])
                    mg_l = float(mmol) * agirlik
                    g_tank = (mg_l * float(st.session_state.konsantrasyon) * float(st.session_state.a_tank)) / 1000
                    kg_tank = g_tank / 1000
                    a_tank_toplam += g_tank
                    a_tank_sonuc.append([gubre, formul, mmol, mg_l, kg_tank])
                    st.session_state.hesaplama_log.append({
                        "adım": f"A Tankı - {gubre}", "açıklama": f"{gubre}: {mmol:.2f} mmol/L, {kg_tank:.3f} kg",
                        "ihtiyac": {}
                    })
                except (TypeError, ValueError, KeyError, IndexError) as e:
                    st.error(f"A Tankı gübresi '{gubre}' hesaplanırken hata: {str(e)}")
                    st.session_state.hesaplama_log.append({
                        "adım": f"Hata - A Tankı - {gubre}", "açıklama": f"Hata: {str(e)}", "ihtiyac": {}
                    })
            b_tank_sonuc = []
            b_tank_toplam = 0
            st.session_state.hesaplama_log.append({
                "adım": "B Tankı Öncesi", "açıklama": f"B Tankı gübreleri: {b_tank_gubreler}", "ihtiyac": {}
            })
            for gubre, mmol in b_tank_gubreler.items():
                try:
                    if gubre not in gubreler:
                        st.session_state.hesaplama_log.append({
                            "adım": f"Hata - B Tankı - {gubre}", 
                            "açıklama": f"Gübre '{gubre}' gubreler sözlüğünde bulunamadı. Tanımlı gübreler: {list(gubreler.keys())}", 
                            "ihtiyac": {}
                        })
                        continue
                    formul = gubreler[gubre]["formul"]
                    agirlik = float(gubreler[gubre]["agirlik"])
                    mg_l = float(mmol) * agirlik
                    g_tank = (mg_l * float(st.session_state.konsantrasyon) * float(st.session_state.b_tank)) / 1000
                    kg_tank = g_tank / 1000
                    b_tank_toplam += g_tank
                    b_tank_sonuc.append([gubre, formul, mmol, mg_l, kg_tank])
                    st.session_state.hesaplama_log.append({
                        "adım": f"B Tankı - {gubre}", "açıklama": f"{gubre}: {mmol:.2f} mmol/L, {kg_tank:.3f} kg",
                        "ihtiyac": {}
                    })
                except (TypeError, ValueError, KeyError, IndexError) as e:
                    st.error(f"B Tankı gübresi '{gubre}' hesaplanırken hata: {str(e)}")
                    st.session_state.hesaplama_log.append({
                        "adım": f"Hata - B Tankı - {gubre}", "açıklama": f"Hata: {str(e)}", "ihtiyac": {}
                    })
            # Sonuçları göster
            col_sonuc1, col_sonuc2 = st.columns(2)
            with col_sonuc1:
                st.subheader("A Tankı (Kalsiyum içeren)")
                if a_tank_sonuc:
                    a_tank_df = pd.DataFrame(a_tank_sonuc, columns=["Gübre Adı", "Formül", "mmol/L", "mg/L", "kg/Tank"])
                    st.dataframe(a_tank_df.style.format({"mmol/L": "{:.2f}", "mg/L": "{:.2f}", "kg/Tank": "{:.3f}"}))
                    st.write(f"**Toplam A Tankı gübresi:** {a_tank_toplam/1000:.3f} kg")
                else:
                    st.info("A Tankı için gübre eklenmedi.")
            with col_sonuc2:
                st.subheader("B Tankı (Fosfat, Sülfat ve Amonyum)")
                if b_tank_sonuc:
                    b_tank_df = pd.DataFrame(b_tank_sonuc, columns=["Gübre Adı", "Formül", "mmol/L", "mg/L", "kg/Tank"])
                    st.dataframe(b_tank_df.style.format({"mmol/L": "{:.2f}", "mg/L": "{:.2f}", "kg/Tank": "{:.3f}"}))
                    st.write(f"**Toplam B Tankı gübresi:** {b_tank_toplam/1000:.3f} kg")
                else:
                    st.info("B Tankı için gübre eklenmedi.")
            # Mikro besinler
            st.subheader("Mikro Besin Elementleri")
            if mikro_sonuc:
                mikro_df = pd.DataFrame(mikro_sonuc, columns=["Gübre Adı", "Formül", "mikromol/L", "mg/L", "gram/Tank"])
                st.dataframe(mikro_df.style.format({"mikromol/L": "{:.2f}", "mg/L": "{:.4f}", "gram/Tank": "{:.2f}"}))
                mikro_toplam = sum(sonuc[4] for sonuc in mikro_sonuc)
                st.write(f"**Toplam mikro besin gübresi:** {mikro_toplam:.2f} gram")
            else:
                st.info("Mikro besin elementi eklenmedi.")
            # Kuyu suyu uyarısı
            if any(st.session_state.kuyu_suyu.values()):
                st.success("✅ Kuyu suyu analiziniz hesaplamada dikkate alındı.")
            # Negatif ihtiyaç uyarısı
            if negatif_ihtiyaclar:
                st.warning("⚠️ Aşağıdaki besinler reçete ihtiyacından fazla eklendi:")
                for iyon, miktar in negatif_ihtiyaclar.items():
                    st.markdown(f"- {iyon}: {-miktar:.2f} mmol/L fazla")
                st.markdown("Bu, bitki sağlığını etkileyebilir veya EC değerini yükseltebilir.")
            # Eksik besin kontrolü
            eksik_var = False
            uyari = ""
            for iyon, miktar in net_ihtiyac.items():
                if miktar > 0.1:
                    eksik_var = True
                    uyari += f" {iyon}: {miktar:.2f} mmol/L,"
            if eksik_var:
                st.warning(f"⚠️ Seçilen gübrelerle karşılanamayan besinler:{uyari[:-1]}")
                st.markdown("**Önerilen Gübreler:**")
                for iyon, miktar in net_ihtiyac.items():
                    if miktar > 0.1:
                        # YENİ: Hata veren kod düzeltildi
                        oneriler = []
                        for gubre, bilgi in gubreler.items():
                            try:
                                if "iyonlar" in bilgi and iyon in bilgi["iyonlar"] and gubre not in secilen_gubreler:
                                    oneriler.append(f"☐ {gubre} ({bilgi['formul']})")
                            except Exception as e:
                                st.error(f"Hata: '{gubre}' gübresi önerileri oluştururken sorun: {str(e)}")
                        st.markdown(f"- {iyon} için: {', '.join(oneriler) if oneriler else 'Reçeteyi gözden geçirin.'}")
            else:
                st.success("✅ Tüm besinler seçilen gübrelerle karşılandı.")
            # Hesaplama adımları
            with st.expander("Hesaplama Adımları"):
                for log in st.session_state.hesaplama_log:
                    st.write(f"**{log['adım']}:** {log['açıklama']}")
                    if log["ihtiyac"]:
                        ihtiyac_df = pd.DataFrame([[k, v] for k, v in log["ihtiyac"].items()], columns=["İyon", "İhtiyaç (mmol/L)"])
                        st.dataframe(ihtiyac_df.style.format({"İhtiyaç (mmol/L)": "{:.2f}"}))
                    st.markdown("---")

# Alt bilgi
st.markdown("---")
st.markdown("Hidrobot Türkçe | Hidroponik besin çözeltisi hesaplama aracı")
