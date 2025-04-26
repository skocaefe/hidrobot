import streamlit as st
import pandas as pd
import numpy as np

# Sayfa ayarları
st.set_page_config(page_title="HydroBuddy Türkçe", page_icon="🌱", layout="wide")

# Başlık ve açıklama
st.title("🌱 HydroBuddy Türkçe")
st.markdown("Hidroponik besin çözeltisi hesaplama aracı. Reçete oluşturun, kuyu suyu analizi ekleyin ve gübre miktarlarını hesaplayın.")

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

# Element atomik kütleleri (g/mol)
element_atomik_kutle = {
    "Fe": 55.845, "B": 10.81, "Mn": 54.938, "Zn": 65.38, "Cu": 63.546, "Mo": 95.95
}

# Hazır reçeteler
hazir_receteler = {
    "Genel Amaçlı": {
        "NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0, "NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0,
        "Fe": 40.0, "B": 30.0, "Mn": 5.0, "Zn": 4.0, "Cu": 0.75, "Mo": 0.5
    },
    "Domates": {
        "NO3": 14.0, "H2PO4": 1.5, "SO4": 1.5, "NH4": 1.2, "K": 7.0, "Ca": 4.0, "Mg": 1.5,
        "Fe": 50.0, "B": 40.0, "Mn": 8.0, "Zn": 4.0, "Cu": 0.8, "Mo": 0.5
    },
    "Salatalık": {
        "NO3": 12.0, "H2PO4": 1.3, "SO4": 1.2, "NH4": 1.1, "K": 5.8, "Ca": 3.5, "Mg": 1.2,
        "Fe": 45.0, "B": 35.0, "Mn": 6.0, "Zn": 4.0, "Cu": 0.75, "Mo": 0.5
    },
    "Marul": {
        "NO3": 10.0, "H2PO4": 1.0, "SO4": 0.8, "NH4": 0.8, "K": 4.5, "Ca": 3.0, "Mg": 0.8,
        "Fe": 35.0, "B": 25.0, "Mn": 4.0, "Zn": 3.0, "Cu": 0.5, "Mo": 0.4
    }
}

# Session state başlatma
if 'recete' not in st.session_state:
    st.session_state.recete = hazir_receteler["Genel Amaçlı"].copy()

if 'kuyu_suyu' not in st.session_state:
    st.session_state.kuyu_suyu = {"NO3": 0.0, "H2PO4": 0.0, "SO4": 0.0, "NH4": 0.0, "K": 0.0, "Ca": 0.0, "Mg": 0.0}

if 'a_tank' not in st.session_state:
    st.session_state.a_tank = 10

if 'b_tank' not in st.session_state:
    st.session_state.b_tank = 10

if 'konsantrasyon' not in st.session_state:
    st.session_state.konsantrasyon = 100

if 'kullanilabilir_gubreler' not in st.session_state:
    st.session_state.kullanilabilir_gubreler = {gubre: False for gubre in gubreler.keys()}

if 'kullanilabilir_mikro_gubreler' not in st.session_state:
    st.session_state.kullanilabilir_mikro_gubreler = {gubre: False for gubre in mikro_gubreler.keys()}

if 'secilen_mikro_gubreler' not in st.session_state:
    st.session_state.secilen_mikro_gubreler = {"Fe": None, "B": None, "Mn": None, "Zn": None, "Cu": None, "Mo": None}

if 'hesaplama_log' not in st.session_state:
    st.session_state.hesaplama_log = []

# İyonik denge hesaplama
def hesapla_iyonik_denge(recete):
    anyon_toplam = sum(recete[ion] * abs(iyon_degerlikleri[ion]) for ion in ["NO3", "H2PO4", "SO4"])
    katyon_toplam = sum(recete[ion] * abs(iyon_degerlikleri[ion]) for ion in ["NH4", "K", "Ca", "Mg"])
    return anyon_toplam, katyon_toplam

# Simülasyon fonksiyonu: Tüm besinlerin karşılanıp karşılanamayacağını kontrol eder
def simulasyon_hesapla(recete, secilen_gubreler):
    net_ihtiyac = {
        ion: max(0, recete[ion] - st.session_state.kuyu_suyu[ion])
        for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]
    }

    if "Kalsiyum Nitrat" in secilen_gubreler and net_ihtiyac["Ca"] > 0:
        net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Ca"]
        net_ihtiyac["Ca"] = 0

    if "Magnezyum Nitrat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Mg"]
        net_ihtiyac["Mg"] = 0

    if "Magnezyum Sülfat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        net_ihtiyac["SO4"] -= net_ihtiyac["Mg"]
        net_ihtiyac["Mg"] = 0

    if "Monoamonyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        map_miktar = net_ihtiyac["H2PO4"]
        net_ihtiyac["H2PO4"] = 0
        net_ihtiyac["NH4"] -= map_miktar

    if "Monopotasyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        mkp_miktar = net_ihtiyac["H2PO4"]
        net_ihtiyac["H2PO4"] = 0
        net_ihtiyac["K"] -= mkp_miktar

    if "Amonyum Sülfat" in secilen_gubreler and net_ihtiyac["NH4"] > 0:
        as_miktar = net_ihtiyac["NH4"] / 2
        net_ihtiyac["NH4"] = 0
        net_ihtiyac["SO4"] -= as_miktar

    if "Potasyum Nitrat" in secilen_gubreler and net_ihtiyac["K"] > 0 and net_ihtiyac["NO3"] > 0:
        kn_miktar = min(net_ihtiyac["K"], net_ihtiyac["NO3"])
        net_ihtiyac["K"] -= kn_miktar
        net_ihtiyac["NO3"] -= kn_miktar

    if "Potasyum Sülfat" in secilen_gubreler and net_ihtiyac["K"] > 0:
        ks_miktar = net_ihtiyac["K"] / 2
        net_ihtiyac["K"] = 0
        net_ihtiyac["SO4"] -= ks_miktar

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
        - **A Tankı**: Kalsiyum içeren gübreler (örn. kalsiyum nitrat).
        - **B Tankı**: Fosfat ve sülfat içeren gübreler.
        - **Konsantrasyon Oranı**: Stok çözeltinin son kullanım konsantrasyonundan kaç kat konsantre olduğunu belirtir (örn. 100x, 100 litre su için 1 litre stok).
        """)

    with col2:
        st.header("Reçete Değerleri")
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("Anyonlar (mmol/L)")
            for ion in ["NO3", "H2PO4", "SO4"]:
                st.session_state.recete[ion] = st.number_input(
                    f"{ion} ({'Nitrat' if ion == 'NO3' else 'Fosfat' if ion == 'H2PO4' else 'Sülfat'}):",
                    value=float(st.session_state.recete[ion]), min_value=0.0, max_value=30.0, step=0.1, format="%.2f",
                    key=f"{ion}_input"
                )

        with col_b:
            st.subheader("Katyonlar (mmol/L)")
            for ion in ["NH4", "K", "Ca", "Mg"]:
                st.session_state.recete[ion] = st.number_input(
                    f"{ion} ({'Amonyum' if ion == 'NH4' else 'Potasyum' if ion == 'K' else 'Kalsiyum' if ion == 'Ca' else 'Magnezyum'}):",
                    value=float(st.session_state.recete[ion]), min_value=0.0, max_value=20.0, step=0.1, format="%.2f",
                    key=f"{ion}_input"
                )

        st.subheader("Mikro Besinler (µmol/L)")
        col_m1, col_m2, col_m3 = st.columns(3)
        for ion, col in zip(["Fe", "Mn", "B", "Zn", "Cu", "Mo"], [col_m1, col_m1, col_m2, col_m2, col_m3, col_m3]):
            with col:
                st.session_state.recete[ion] = st.number_input(
                    f"{ion} ({'Demir' if ion == 'Fe' else 'Mangan' if ion == 'Mn' else 'Bor' if ion == 'B' else 'Çinko' if ion == 'Zn' else 'Bakır' if ion == 'Cu' else 'Molibden'}):",
                    value=float(st.session_state.recete.get(ion, 0.0)), min_value=0.0, max_value=100.0, step=0.1, format="%.2f",
                    key=f"{ion}_input"
                )

        st.subheader("İyonik Denge")
        anyon_toplam, katyon_toplam = hesapla_iyonik_denge(st.session_state.recete)
        col_denge1, col_denge2 = st.columns(2)

        with col_denge1:
            anyon_data = [[ion, st.session_state.recete[ion], st.session_state.recete[ion] * abs(iyon_degerlikleri[ion])]
                          for ion in ["NO3", "H2PO4", "SO4"]]
            anyon_df = pd.DataFrame(anyon_data, columns=["Anyon", "mmol/L", "me/L"])
            st.write("**Anyonlar:**")
            st.dataframe(anyon_df.style.format({"mmol/L": "{:.2f}", "me/L": "{:.2f}"}))
            st.write(f"**Toplam:** {anyon_toplam:.2f} me/L")

        with col_denge2:
            katyon_data = [[ion, st.session_state.recete[ion], st.session_state.recete[ion] * abs(iyon_degerlikleri[ion])]
                           for ion in ["NH4", "K", "Ca", "Mg"]]
            katyon_df = pd.DataFrame(katyon_data, columns=["Katyon", "mmol/L", "me/L"])
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
            st.markdown("**İyileştirme Önerisi:** " + (
                "Anyon fazlası var. Daha fazla katyon (K, Ca, Mg, NH4) ekleyin." if anyon_toplam > katyon_toplam
                else "Katyon fazlası var. Daha fazla anyon (NO3, H2PO4, SO4) ekleyin."))

# Tab 2: Kuyu Suyu
with tabs[1]:
    st.header("Kuyu Suyu Analizi")
    st.info("Kuyu suyu veya şebeke suyu kullanıyorsanız, iyon konsantrasyonlarını girin. Bu, gübre miktarlarını daha doğru hesaplamanızı sağlar.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Anyonlar (mmol/L)")
        for ion in ["NO3", "H2PO4", "SO4"]:
            st.session_state.kuyu_suyu[ion] = st.number_input(
                f"{ion} ({'Nitrat' if ion == 'NO3' else 'Fosfat' if ion == 'H2PO4' else 'Sülfat'}):",
                value=float(st.session_state.kuyu_suyu[ion]), min_value=0.0, max_value=10.0, step=0.05, format="%.2f",
                key=f"kuyu_{ion}_input"
            )

    with col2:
        st.subheader("Katyonlar (mmol/L)")
        for ion in ["NH4", "K", "Ca", "Mg"]:
            st.session_state.kuyu_suyu[ion] = st.number_input(
                f"{ion} ({'Amonyum' if ion == 'NH4' else 'Potasyum' if ion == 'K' else 'Kalsiyum' if ion == 'Ca' else 'Magnezyum'}):",
                value=float(st.session_state.kuyu_suyu[ion]), min_value=0.0, max_value=10.0, step=0.05, format="%.2f",
                key=f"kuyu_{ion}_input"
            )

    if any(st.session_state.kuyu_suyu.values()):
        st.success("✅ Kuyu suyu değerleri kaydedildi ve hesaplamalarda dikkate alınacak.")
    else:
        st.info("ℹ️ Kuyu suyu değeri girilmedi. Saf su varsayılacak.")

# Tab 3: Gübre Seçimi
with tabs[2]:
    st.header("Elimdeki Gübreler")
    st.info("Kullanmak istediğiniz gübreleri seçin. Hesaplamalar sadece seçilen gübrelerle yapılır.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Makro Gübreler")
        a_tank_gubreler = [gubre for gubre, bilgi in gubreler.items() if bilgi["tank"] == "A"]
        b_tank_gubreler = [gubre for gubre, bilgi in gubreler.items() if bilgi["tank"] == "B"]

        st.markdown("**A Tankı Gübreleri**")
        for gubre in a_tank_gubreler:
            st.session_state.kullanilabilir_gubreler[gubre] = st.checkbox(
                f"☐ {gubre} ({gubreler[gubre]['formul']})",
                value=st.session_state.kullanilabilir_gubreler[gubre], key=f"checkbox_{gubre}"
            )

        st.markdown("**B Tankı Gübreleri**")
        for gubre in b_tank_gubreler:
            st.session_state.kullanilabilir_gubreler[gubre] = st.checkbox(
                f"☐ {gubre} ({gubreler[gubre]['formul']})",
                value=st.session_state.kullanilabilir_gubreler[gubre], key=f"checkbox_{gubre}"
            )

    with col2:
        st.subheader("Mikro Gübreler")
        mikro_element_gruplari = {}
        for gubre, bilgi in mikro_gubreler.items():
            element = bilgi["element"]
            if element not in mikro_element_gruplari:
                mikro_element_gruplari[element] = []
            mikro_element_gruplari[element].append(gubre)

        for element, gubreler in mikro_element_gruplari.items():
            st.markdown(f"**{element} Kaynağı**")
            secilen_gubre = st.radio(
                f"{element} için gübre seçimi", options=["Seçilmedi"] + gubreler,
                index=0 if st.session_state.secilen_mikro_gubreler[element] not in gubreler else gubreler.index(st.session_state.secilen_mikro_gubreler[element]) + 1,
                key=f"radio_{element}"
            )
            st.session_state.secilen_mikro_gubreler[element] = None if secilen_gubre == "Seçilmedi" else secilen_gubre
            for gubre in gubreler:
                st.session_state.kullanilabilir_mikro_gubreler[gubre] = (gubre == secilen_gubre)

    secilen_gubreler = [gubre for gubre, secildi in st.session_state.kullanilabilir_gubreler.items() if secildi]
    secilen_mikro_gubreler = [gubre for element, gubre in st.session_state.secilen_mikro_gubreler.items() if gubre]

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

    if secilen_gubreler:
        eksik_besinler = simulasyon_hesapla(st.session_state.recete, secilen_gubreler)
        if eksik_besinler:
            st.error(f"⚠️ Seçilen gübrelerle karşılanamayan besinler: {', '.join(eksik_besinler)}")
            st.markdown("**Önerilen Gübreler:**")
            for besin in eksik_besinler:
                oneriler = [f"☐ {gubre} ({bilgi['formul']})" for gubre, bilgi in gubreler.items()
                            if besin in bilgi["iyonlar"] and gubre not in secilen_gubreler]
                st.markdown(f"- {besin} için: {', '.join(oneriler) if oneriler else 'Reçeteyi gözden geçirin.'}")
        else:
            st.success("✅ Seçilen gübrelerle tüm makro besinler karşılanabilir.")

# Tab 4: Gübre Hesaplama
with tabs[3]:
    st.header("Gübre Hesaplama")
    if st.button("Gübre Hesapla", type="primary"):
        secilen_gubreler = [gubre for gubre, secildi in st.session_state.kullanilabilir_gubreler.items() if secildi]
        secilen_mikro_gubreler = [gubre for element, gubre in st.session_state.secilen_mikro_gubreler.items() if gubre]

        if not secilen_gubreler:
            st.error("Lütfen 'Gübre Seçimi' sekmesinden en az bir makro gübre seçin!")
        else:
            st.session_state.hesaplama_log = []
            net_ihtiyac = {
                ion: max(0, st.session_state.recete[ion] - st.session_state.kuyu_suyu[ion])
                for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]
            }
            a_tank_gubreler = {}
            b_tank_gubreler = {}
            adim = 1

            st.session_state.hesaplama_log.append({
                "adim": "Başlangıç", "aciklama": "Kuyu suyu sonrası ihtiyaçlar",
                "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
            })

            if "Kalsiyum Nitrat" in secilen_gubreler and net_ihtiyac["Ca"] > 0:
                a_tank_gubreler["Kalsiyum Nitrat"] = net_ihtiyac["Ca"]
                net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Ca"]
                net_ihtiyac["Ca"] = 0
                st.session_state.hesaplama_log.append({
                    "adim": f"Adım {adim}", "aciklama": f"Kalsiyum Nitrat: {net_ihtiyac['Ca']:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1

            if "Magnezyum Nitrat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
                a_tank_gubreler["Magnezyum Nitrat"] = net_ihtiyac["Mg"]
                net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Mg"]
                net_ihtiyac["Mg"] = 0
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "aciklama": f"Magnezyum Nitrat: {net_ihtiyac['Mg']:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1

            if "Magnezyum Sülfat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
                b_tank_gubreler["Magnezyum Sülfat"] = net_ihtiyac["Mg"]
                net_ihtiyac["SO4"] -= net_ihtiyac["Mg"]
                net_ihtiyac["Mg"] = 0
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "aciklama": f"Magnezyum Sülfat: {net_ihtiyac['Mg']:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1

            if "Monoamonyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
                map_miktar = net_ihtiyac["H2PO4"]
                b_tank_gubreler["Monoamonyum Fosfat"] = map_miktar
                net_ihtiyac["H2PO4"] = 0
                net_ihtiyac["NH4"] -= map_miktar
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "aciklama": f"Monoamonyum Fosfat: {map_miktar:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1

            if "Monopotasyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
                mkp_miktar = net_ihtiyac["H2PO4"]
                b_tank_gubreler["Monopotasyum Fosfat"] = mkp_miktar
                net_ihtiyac["H2PO4"] = 0
                net_ihtiyac["K"] -= mkp_miktar
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "aciklama": f"Monopotasyum Fosfat: {mkp_miktar:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1

            if "Amonyum Sülfat" in secilen_gubreler and net_ihtiyac["NH4"] > 0:
                as_miktar = net_ihtiyac["NH4"] / 2
                b_tank_gubreler["Amonyum Sülfat"] = as_miktar
                net_ihtiyac["NH4"] = 0
                net_ihtiyac["SO4"] -= as_miktar
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "aciklama": f"Amonyum Sülfat: {as_miktar:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1

            if "Potasyum Nitrat" in secilen_gubreler and net_ihtiyac["K"] > 0 and net_ihtiyac["NO3"] > 0:
                kn_miktar = min(net_ihtiyac["K"], net_ihtiyac["NO3"])
                a_tank_gubreler["Potasyum Nitrat"] = kn_miktar
                net_ihtiyac["K"] -= kn_miktar
                net_ihtiyac["NO3"] -= kn_miktar
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "aciklama": f"Potasyum Nitrat: {kn_miktar:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1

            if "Potasyum Sülfat" in secilen_gubreler and net_ihtiyac["K"] > 0:
                ks_miktar = net_ihtiyac["K"] / 2
                b_tank_gubreler["Potasyum Sülfat"] = ks_miktar
                net_ihtiyac["K"] = 0
                net_ihtiyac["SO4"] -= ks_miktar
                st.session_state.hesaplama_log.append({
                    "adım": f"Adım {adim}", "aciklama": f"Potasyum Sülfat: {ks_miktar:.2f} mmol/L",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })
                adim += 1

            negatif_ihtiyaclar = [iyon for iyon, miktar in net_ihtiyac.items() if miktar < -0.1]
            mikro_sonuc = []

            for element in ["Fe", "B", "Mn", "Zn", "Cu", "Mo"]:
                secilen_gubre = st.session_state.secilen_mikro_gubreler.get(element)
                if secilen_gubre and element in st.session_state.recete and st.session_state.recete[element] > 0:
                    mikromol = st.session_state.recete[element]
                    gubre_bilgi = mikro_gubreler[secilen_gubre]
                    mmol = mikromol / 1000
                    element_mol_agirligi = element_atomik_kutle[element] * (100 / gubre_bilgi["yuzde"])
                    mg_l = mmol * element_mol_agirligi
                    g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.b_tank) / 1000
                    mikro_sonuc.append([secilen_gubre, gubre_bilgi["formul"], mikromol, mg_l, g_tank])

            a_tank_sonuc = []
            a_tank_toplam = 0
            for gubre, mmol in a_tank_gubreler.items():
                formul = gubreler[gubre]["formul"]
                mg_l = mmol * gubreler[gubre]["agirlik"]
                g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.a_tank) / 1000
                kg_tank = g_tank / 1000
                a_tank_toplam += g_tank
                a_tank_sonuc.append([gubre, formul, mmol, mg_l, kg_tank])

            b_tank_sonuc = []
            b_tank_toplam = 0
            for gubre, mmol in b_tank_gubreler.items():
                formul = gubreler[gubre]["formul"]
                mg_l = mmol * gubreler[gubre]["agirlik"]
                g_tank = (mg_l * st.session_state.konsantrasyon * st.session_state.b_tank) / 1000
                kg_tank = g_tank / 1000
                b_tank_toplam += g_tank
                b_tank_sonuc.append([gubre, formul, mmol, mg_l, kg_tank])

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

            st.subheader("Mikro Besin Elementleri")
            if mikro_sonuc:
                mikro_df = pd.DataFrame(mikro_sonuc, columns=["Gübre Adı", "Formül", "µmol/L", "mg/L", "g/Tank"])
                st.dataframe(mikro_df.style.format({"µmol/L": "{:.2f}", "mg/L": "{:.4f}", "g/Tank": "{:.4f}"}))
                mikro_toplam = sum(sonuc[4] for sonuc in mikro_sonuc)
                st.write(f"**Toplam mikro besin gübresi:** {mikro_toplam:.2f} g")
            else:
                st.info("Mikro besin elementi eklenmedi veya seçilen gübrelerle karşılanamadı.")

            if any(st.session_state.kuyu_suyu.values()):
                st.success("✅ Kuyu suyu analiziniz hesaplamada dikkate alındı.")

            if negatif_ihtiyaclar:
                st.warning("⚠️ Aşağıdaki besinler reçete ihtiyacından fazla eklendi:")
                for iyon in negatif_ihtiyaclar:
                    st.markdown(f"- {iyon}: {-net_ihtiyac[iyon]:.2f} mmol/L fazla")
                st.markdown("Bu, bitki sağlığını etkileyebilir veya EC değerini yükseltebilir.")

            st.subheader("Denge Kontrol")
            eksik_var = False
            uyari = ""
            for iyon, miktar in net_ihtiyac.items():
                if miktar > 0.1:
                    eksik_var = True
                    uyari += f" {iyon}: {miktar:.2f} mmol/L,"

            if eksik_var:
                st.warning(f"⚠️ Seçilen gübrelerle karşılanamayan besinler:{uyari[:-1]}")
                st.markdown("**Önerilen Ek Gübreler:**")
                for iyon, miktar in net_ihtiyac.items():
                    if miktar > 0.1:
                        oneriler = [f"☐ {gubre} ({bilgi['formul']})" for gubre, bilgi in gubreler.items()
                                    if iyon in bilgi["iyonlar"] and gubre not in secilen_gubreler]
                        st.markdown(f"- {iyon} için: {', '.join(oneriler) if oneriler else 'Reçeteyi gözden geçirin.'}")
            else:
                st.success("✅ Tüm besinler seçilen gübrelerle karşılandı.")

            with st.expander("Hesaplama Adımları"):
                for log in st.session_state.hesaplama_log:
                    st.write(f"**{log['adım']}:** {log['aciklama']}")
                    ihtiyac_df = pd.DataFrame([[k, v] for k, v in log["ihtiyac"].items()], columns=["İyon", "İhtiyaç (mmol/L)"])
                    st.dataframe(ihtiyac_df.style.format({"İhtiyaç (mmol/L)": "{:.2f}"}))
                    st.markdown("---")

# Alt bilgi
st.markdown("---")
st.markdown("HydroBuddy Türkçe | Hidroponik besin çözeltisi hesaplama aracı | xAI destekli")
