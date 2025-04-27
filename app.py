import streamlit as st
import pandas as pd
import datetime
import logging
from fpdf import FPDF
from io import BytesIO

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HydroBuddy")

# Yapılandırma sabitleri
IYON_ESIK_DEGERI = 0.1  # mmol/L

# Streamlit sayfa ayarları
st.set_page_config(page_title="HydroBuddy Türkçe", page_icon="🌱", layout="wide")

# Başlık ve açıklama
st.title("🌱 HydroBuddy Türkçe")
st.markdown("Hidroponik besin çözeltisi hesaplama aracı")

# İyon bilgileri ve etkileri
iyon_bilgileri = {
    "NO3": {"ad": "Nitrat", "birim": "mmol/L", "eksik": "Yapraklarda sararma, bitki gelişiminde yavaşlama", "fazla": "Aşırı vejetatif büyüme"},
    "H2PO4": {"ad": "Fosfat", "birim": "mmol/L", "eksik": "Koyu yeşil/mor yapraklar, zayıf kök sistemi", "fazla": "Çinko ve demir alımını engelleme"},
    "SO4": {"ad": "Sülfat", "birim": "mmol/L", "eksik": "Yeni yapraklarda sararma", "fazla": "Yüksek tuzluluk"},
    "NH4": {"ad": "Amonyum", "birim": "mmol/L", "eksik": "Büyümede durgunluk", "fazla": "Kök gelişiminde zayıflama"},
    "K": {"ad": "Potasyum", "birim": "mmol/L", "eksik": "Yaprak kenarlarında yanma", "fazla": "Magnezyum ve kalsiyum alımını engelleme"},
    "Ca": {"ad": "Kalsiyum", "birim": "mmol/L", "eksik": "Çiçek ucu çürüklüğü", "fazla": "Fosfor alımını engelleme"},
    "Mg": {"ad": "Magnezyum", "birim": "mmol/L", "eksik": "Yaşlı yapraklarda sararma", "fazla": "Kalsiyum ve potasyum alımında azalma"},
    "Fe": {"ad": "Demir", "birim": "mikromol/L", "eksik": "Genç yapraklarda kloroz", "fazla": "Yapraklarda bronzlaşma"},
    "B": {"ad": "Bor", "birim": "mikromol/L", "eksik": "Büyüme noktalarında ölüm", "fazla": "Yaprak kenarlarında yanma"},
    "Mn": {"ad": "Mangan", "birim": "mikromol/L", "eksik": "Yapraklarda sararma", "fazla": "Yaşlı yapraklarda nekroz"},
    "Zn": {"ad": "Çinko", "birim": "mikromol/L", "eksik": "Bodur büyüme", "fazla": "Demir ve mangan alımını engelleme"},
    "Cu": {"ad": "Bakır", "birim": "mikromol/L", "eksik": "Yapraklarda solgunluk", "fazla": "Kök gelişiminde inhibisyon"},
    "Mo": {"ad": "Molibden", "birim": "mikromol/L", "eksik": "Azot eksikliğine benzer belirtiler", "fazla": "Nadiren toksik etki"}
}

# Gübre bilgileri
gubreler = {
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2", "agirlik": 236.15, "tank": "A", "iyonlar": {"Ca": 1, "NO3": 2}},
    "Potasyum Nitrat": {"formul": "KNO3", "agirlik": 101.10, "tank": "A", "iyonlar": {"K": 1, "NO3": 1}},
    "Magnezyum Nitrat": {"formul": "Mg(NO3)2", "agirlik": 256.41, "tank": "A", "iyonlar": {"Mg": 1, "NO3": 2}},
    "Magnezyum Sülfat": {"formul": "MgSO4", "agirlik": 246.51, "tank": "B", "iyonlar": {"Mg": 1, "SO4": 1}},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "agirlik": 136.09, "tank": "B", "iyonlar": {"K": 1, "H2PO4": 1}},
    "Monoamonyum Fosfat": {"formul": "NH4H2PO4", "agirlik": 115.03, "tank": "B", "iyonlar": {"NH4": 1, "H2PO4": 1}},
    "Amonyum Sülfat": {"formul": "(NH4)2SO4", "agirlik": 132.14, "tank": "B", "iyonlar": {"NH4": 2, "SO4": 1}},
    "Potasyum Sülfat": {"formul": "K2SO4", "agirlik": 174.26, "tank": "B", "iyonlar": {"K": 2, "SO4": 1}}
}

# Mikro elementler
mikro_gubreler = {
    "Demir EDTA": {"formul": "Fe-EDTA", "agirlik": 346.0, "element": "Fe", "yuzde": 13},
    "Borik Asit": {"formul": "H3BO3", "agirlik": 61.83, "element": "B", "yuzde": 17.5},
    "Mangan Sülfat": {"formul": "MnSO4", "agirlik": 169.02, "element": "Mn", "yuzde": 32},
    "Çinko Sülfat": {"formul": "ZnSO4", "agirlik": 287.56, "element": "Zn", "yuzde": 23},
    "Bakır Sülfat": {"formul": "CuSO4", "agirlik": 249.68, "element": "Cu", "yuzde": 25},
    "Sodyum Molibdat": {"formul": "Na2MoO4", "agirlik": 241.95, "element": "Mo", "yuzde": 40}
}

# Element atomik kütleleri
element_atomik_kutle = {
    "Fe": 55.845, "B": 10.81, "Mn": 54.938, "Zn": 65.38, "Cu": 63.546, "Mo": 95.95
}

# Yardımcı Fonksiyonlar
def session_state_baslat():
    if 'recete' not in st.session_state:
        st.session_state.recete = {
            "NO3": 9.5, "H2PO4": 1.0, "SO4": 0.5, "NH4": 0.5, "K": 5.0, "Ca": 2.25, "Mg": 0.75,
            "Fe": 40.0, "B": 30.0, "Mn": 5.0, "Zn": 4.0, "Cu": 0.75, "Mo": 0.5
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
    if 'secilen_gubreler' not in st.session_state:
        st.session_state.secilen_gubreler = []
    if 'secilen_mikro_gubreler' not in st.session_state:
        st.session_state.secilen_mikro_gubreler = {
            "Fe": None, "B": None, "Mn": None, "Zn": None, "Cu": None, "Mo": None
        }
    if 'hesaplama_log' not in st.session_state:
        st.session_state.hesaplama_log = []
    if 'hesaplama_sonuclari' not in st.session_state:
        st.session_state.hesaplama_sonuclari = None

def iyon_dengesini_hesapla(recete, secilen_gubreler):
    makro_iyonlar = ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]
    net_ihtiyac = {ion: float(recete[ion]) for ion in makro_iyonlar}
    iyon_tuketim = {ion: 0.0 for ion in makro_iyonlar}

    for gubre in secilen_gubreler:
        if gubre in gubreler:
            for iyon, katsayi in gubreler[gubre]["iyonlar"].items():
                if iyon in iyon_tuketim:
                    if gubre == "Kalsiyum Nitrat" and iyon == "Ca":
                        iyon_tuketim["Ca"] += net_ihtiyac["Ca"]
                    elif gubre == "Kalsiyum Nitrat" and iyon == "NO3":
                        iyon_tuketim["NO3"] += 2 * net_ihtiyac["Ca"]
                    elif gubre == "Magnezyum Nitrat" and iyon == "Mg":
                        iyon_tuketim["Mg"] += net_ihtiyac["Mg"]
                    elif gubre == "Magnezyum Nitrat" and iyon == "NO3":
                        iyon_tuketim["NO3"] += 2 * net_ihtiyac["Mg"]
                    elif gubre == "Magnezyum Sülfat" and iyon == "Mg":
                        iyon_tuketim["Mg"] += net_ihtiyac["Mg"]
                    elif gubre == "Magnezyum Sülfat" and iyon == "SO4":
                        iyon_tuketim["SO4"] += net_ihtiyac["Mg"]
                    elif gubre == "Monopotasyum Fosfat" and iyon == "H2PO4":
                        iyon_tuketim["H2PO4"] += net_ihtiyac["H2PO4"]
                    elif gubre == "Monopotasyum Fosfat" and iyon == "K":
                        iyon_tuketim["K"] += net_ihtiyac["H2PO4"]
                    elif gubre == "Monoamonyum Fosfat" and iyon == "H2PO4":
                        iyon_tuketim["H2PO4"] += net_ihtiyac["H2PO4"]
                    elif gubre == "Monoamonyum Fosfat" and iyon == "NH4":
                        iyon_tuketim["NH4"] += net_ihtiyac["H2PO4"]
                    elif gubre == "Potasyum Nitrat" and iyon == "K" and net_ihtiyac["K"] > 0 and net_ihtiyac["NO3"] > 0:
                        kn_miktar = min(net_ihtiyac["K"], net_ihtiyac["NO3"])
                        iyon_tuketim["K"] += kn_miktar
                        iyon_tuketim["NO3"] += kn_miktar
                    elif gubre == "Potasyum Sülfat" and iyon == "K" and net_ihtiyac["K"] > 0:
                        iyon_tuketim["K"] += net_ihtiyac["K"]
                        iyon_tuketim["SO4"] += net_ihtiyac["K"] / 2
                    elif gubre == "Amonyum Sülfat" and iyon == "NH4" and net_ihtiyac["NH4"] > 0:
                        as_miktar = min(net_ihtiyac["NH4"] / 2, net_ihtiyac["SO4"])
                        iyon_tuketim["NH4"] += 2 * as_miktar
                        iyon_tuketim["SO4"] += as_miktar

    eksik_iyonlar = {}
    fazla_iyonlar = {}
    for iyon in makro_iyonlar:
        fark = net_ihtiyac[iyon] - iyon_tuketim[iyon]
        if fark > IYON_ESIK_DEGERI:
            eksik_iyonlar[iyon] = fark
        elif fark < -IYON_ESIK_DEGERI:
            fazla_iyonlar[iyon] = -fark

    return eksik_iyonlar, fazla_iyonlar

def gubre_onerileri_olustur(eksik_iyonlar, secilen_gubreler):
    oneriler = {}
    for iyon in eksik_iyonlar:
        iyon_onerileri = []
        for gubre, bilgi in gubreler.items():
            if iyon in bilgi["iyonlar"] and gubre not in secilen_gubreler:
                iyon_onerileri.append(f"{gubre} ({bilgi['formul']})")
        if iyon_onerileri:
            oneriler[iyon] = iyon_onerileri
    return oneriler

def hesapla_mikro_besinler(recete, secilen_mikro_gubreler, konsantrasyon, b_tank_hacmi):
    mikro_sonuc = []
    for element, label in [("Fe", "Demir"), ("B", "Bor"), ("Mn", "Mangan"), ("Zn", "Çinko"), ("Cu", "Bakır"), ("Mo", "Molibden")]:
        secilen_gubre = secilen_mikro_gubreler[element]
        if secilen_gubre and element in recete and float(recete[element]) > 0:
            try:
                mikromol = float(recete[element])
                gubre_bilgi = mikro_gubreler[secilen_gubre]
                mmol = mikromol / 1000
                element_mol_agirligi = element_atomik_kutle[element] * (100 / gubre_bilgi["yuzde"])
                mg_l = mmol * element_mol_agirligi
                g_tank = (mg_l * float(konsantrasyon) * float(b_tank_hacmi)) / 1000
                mikro_sonuc.append([secilen_gubre, gubre_bilgi["formul"], mikromol, mg_l, g_tank])
            except Exception as e:
                st.error(f"Mikro besin '{element}' hesaplanırken hata: {str(e)}")
    return mikro_sonuc

def hesapla_tank_gübreleri(tank_gubreleri, gubre_tipi, tank_hacmi, konsantrasyon):
    sonuclar = []
    toplam_agirlik = 0
    for gubre, mmol in tank_gubreleri.items():
        try:
            if gubre not in gubreler:
                continue
            formul = gubreler[gubre]["formul"]
            agirlik = float(gubreler[gubre]["agirlik"])
            mg_l = float(mmol) * agirlik
            g_tank = (mg_l * float(konsantrasyon) * float(tank_hacmi)) / 1000
            kg_tank = g_tank / 1000
            toplam_agirlik += g_tank
            sonuclar.append([gubre, formul, mmol, mg_l, kg_tank])
        except Exception as e:
            st.error(f"{gubre_tipi} Tankı gübresi '{gubre}' hesaplanırken hata: {str(e)}")
    return sonuclar, toplam_agirlik

def create_pdf(recete, a_tank_sonuc, b_tank_sonuc, mikro_sonuc, eksik_iyonlar, fazla_iyonlar, oneriler):
    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.set_font('Arial', '', 11)
    except:
        pdf.set_font('Helvetica', '', 11)

    pdf.set_font('', '', 16)
    pdf.cell(0, 10, 'HydroBuddy Türkçe - Hidroponik Besin Hesaplaması', 0, 1, 'C')
    pdf.set_font('', '', 12)
    pdf.cell(0, 10, f'Oluşturulma Tarihi: {datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}', 0, 1, 'C')
    pdf.ln(5)

    pdf.set_font('', '', 14)
    pdf.cell(0, 10, 'A Tankı Gübreleri', 0, 1, 'L')
    pdf.set_font('', '', 11)
    if a_tank_sonuc:
        pdf.cell(60, 7, 'Gübre', 1, 0, 'C')
        pdf.cell(35, 7, 'Formül', 1, 0, 'C')
        pdf.cell(30, 7, 'mmol/L', 1, 0, 'C')
        pdf.cell(30, 7, 'kg/Tank', 1, 1, 'C')
        for row in a_tank_sonuc:
            pdf.cell(60, 7, row[0], 1, 0, 'L')
            pdf.cell(35, 7, row[1], 1, 0, 'L')
            pdf.cell(30, 7, f"{row[2]:.2f}", 1, 0, 'R')
            pdf.cell(30, 7, f"{row[4]:.3f}", 1, 1, 'R')
    else:
        pdf.cell(0, 7, 'A Tankı için gübre eklenmedi.', 1, 1, 'L')

    pdf.ln(5)
    pdf.set_font('', '', 14)
    pdf.cell(0, 10, 'B Tankı Gübreleri', 0, 1, 'L')
    pdf.set_font('', '', 11)
    if b_tank_sonuc:
        pdf.cell(60, 7, 'Gübre', 1, 0, 'C')
        pdf.cell(35, 7, 'Formül', 1, 0, 'C')
        pdf.cell(30, 7, 'mmol/L', 1, 0, 'C')
        pdf.cell(30, 7, 'kg/Tank', 1, 1, 'C')
        for row in b_tank_sonuc:
            pdf.cell(60, 7, row[0], 1, 0, 'L')
            pdf.cell(35, 7, row[1], 1, 0, 'L')
            pdf.cell(30, 7, f"{row[2]:.2f}", 1, 0, 'R')
            pdf.cell(30, 7, f"{row[4]:.3f}", 1, 1, 'R')
    else:
        pdf.cell(0, 7, 'B Tankı için gübre eklenmedi.', 1, 1, 'L')

    pdf.ln(5)
    pdf.set_font('', '', 14)
    pdf.cell(0, 10, 'Mikro Besin Elementleri', 0, 1, 'L')
    pdf.set_font('', '', 11)
    if mikro_sonuc:
        pdf.cell(60, 7, 'Gübre', 1, 0, 'C')
        pdf.cell(35, 7, 'Formül', 1, 0, 'C')
        pdf.cell(30, 7, 'mikromol/L', 1, 0, 'C')
        pdf.cell(30, 7, 'gram/Tank', 1, 1, 'C')
        for row in mikro_sonuc:
            pdf.cell(60, 7, row[0], 1, 0, 'L')
            pdf.cell(35, 7, row[1], 1, 0, 'L')
            pdf.cell(30, 7, f"{row[2]:.2f}", 1, 0, 'R')
            pdf.cell(30, 7, f"{row[4]:.2f}", 1, 1, 'R')
    else:
        pdf.cell(0, 7, 'Mikro besin elementi eklenmedi.', 1, 1, 'L')

    if eksik_iyonlar:
        pdf.ln(5)
        pdf.set_font('', '', 14)
        pdf.cell(0, 10, 'Eksik İyonlar', 0, 1, 'L')
        pdf.set_font('', '', 11)
        for iyon, miktar in eksik_iyonlar.items():
            iyon_adi = iyon_bilgileri[iyon]["ad"]
            pdf.cell(0, 7, f"{iyon} ({iyon_adi}): {miktar:.2f} {iyon_bilgileri[iyon]['birim']} eksik", 0, 1, 'L')

    if fazla_iyonlar:
        pdf.ln(5)
        pdf.set_font('', '', 14)
        pdf.cell(0, 10, 'Fazla İyonlar', 0, 1, 'L')
        pdf.set_font('', '', 11)
        for iyon, miktar in fazla_iyonlar.items():
            iyon_adi = iyon_bilgileri[iyon]["ad"]
            pdf.cell(0, 7, f"{iyon} ({iyon_adi}): {miktar:.2f} {iyon_bilgileri[iyon]['birim']} fazla", 0, 1, 'L')

    pdf.ln(10)
    pdf.set_font('', '', 9)
    pdf.cell(0, 5, 'HydroBuddy Türkçe | Hidroponik besin çözeltisi hesaplama aracı', 0, 1, 'C')

    return pdf.output(dest='S').encode('latin1')

# Session state başlat
session_state_baslat()

# Ana düzen
tabs = st.tabs(["Reçete Oluşturma", "Kuyu Suyu", "Gübre Seçimi", "Gübre Hesaplama"])

# Tab 1: Reçete Oluşturma
with tabs[0]:
    st.header("Reçete Değerleri")
    st.subheader("Makro Besinler (mmol/L)")
    hedef_iyonlar = {}
    for iyon in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]:
        st.session_state.recete[iyon] = st.number_input(
            f"{iyon} ({iyon_bilgileri[iyon]['birim']})",
            value=float(st.session_state.recete[iyon]),
            min_value=0.0,
            max_value=30.0,
            step=0.1,
            format="%.2f",
            key=f"{iyon}_input"
        )
        hedef_iyonlar[iyon] = st.session_state.recete[iyon]

    st.subheader("Mikro Besinler (mikromol/L)")
    for iyon in ["Fe", "B", "Mn", "Zn", "Cu", "Mo"]:
        st.session_state.recete[iyon] = st.number_input(
            f"{iyon} ({iyon_bilgileri[iyon]['birim']})",
            value=float(st.session_state.recete[iyon]),
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            format="%.1f",
            key=f"{iyon}_input"
        )

# Tab 2: Kuyu Suyu
with tabs[1]:
    st.header("Kuyu Suyu Analizi")
    for iyon in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]:
        st.session_state.kuyu_suyu[iyon] = st.number_input(
            f"{iyon} ({iyon_bilgileri[iyon]['birim']})",
            value=float(st.session_state.kuyu_suyu[iyon]),
            min_value=0.0,
            max_value=10.0,
            step=0.05,
            format="%.2f",
            key=f"kuyu_{iyon}_input"
        )

# Tab 3: Gübre Seçimi
with tabs[2]:
    st.header("Gübre Seçimi")
    st.session_state.secilen_gubreler = st.multiselect(
        "Hangi fertilizatörleri kullanmak istiyorsunuz?",
        list(gubreler.keys())
    )

    st.subheader("Mikro Besin Gübreleri")
    for element in ["Fe", "B", "Mn", "Zn", "Cu", "Mo"]:
        options = ["Seçilmedi"] + [gubre for gubre, info in mikro_gubreler.items() if info["element"] == element]
        st.session_state.secilen_mikro_gubreler[element] = st.selectbox(
            f"{element} için gübre seçimi",
            options,
            index=0 if st.session_state.secilen_mikro_gubreler[element] not in options else options.index(st.session_state.secilen_mikro_gubreler[element]),
            key=f"mikro_{element}"
        )

# Tab 4: Gübre Hesaplama
with tabs[3]:
    st.header("Gübre Hesaplama")
    if st.button("Hesapla"):
        secilen_gubreler = st.session_state.secilen_gubreler
        if not secilen_gubreler:
            st.error("Lütfen en az bir fertilizatör seçin!")
        else:
            try:
                # Net ihtiyaç hesaplama (kuyu suyu değerlerini çıkararak)
                net_ihtiyac = {
                    iyon: max(0, float(st.session_state.recete[iyon]) - float(st.session_state.kuyu_suyu[iyon]))
                    for iyon in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]
                }

                # Hesaplama logunu başlat
                st.session_state.hesaplama_log = []
                st.session_state.hesaplama_log.append({
                    "adım": "Başlangıç",
                    "açıklama": "Kuyu suyu sonrası ihtiyaçlar",
                    "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                })

                # Tank gübreleri için sözlükler
                a_tank_gubreler = {}
                b_tank_gubreler = {}
                adim = 1

                # 1. Kalsiyum Nitrat
                if "Kalsiyum Nitrat" in secilen_gubreler and net_ihtiyac["Ca"] > 0:
                    ca_miktar = net_ihtiyac["Ca"]
                    a_tank_gubreler["Kalsiyum Nitrat"] = ca_miktar
                    net_ihtiyac["Ca"] = 0
                    net_ihtiyac["NO3"] -= 2 * ca_miktar
                    st.session_state.hesaplama_log.append({
                        "adım": f"Adım {adim}",
                        "açıklama": f"Kalsiyum Nitrat: {ca_miktar:.2f} mmol/L",
                        "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                    })
                    adim += 1

                # 2. Magnezyum Nitrat
                if "Magnezyum Nitrat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
                    mg_miktar = net_ihtiyac["Mg"]
                    a_tank_gubreler["Magnezyum Nitrat"] = mg_miktar
                    net_ihtiyac["Mg"] = 0
                    net_ihtiyac["NO3"] -= 2 * mg_miktar
                    st.session_state.hesaplama_log.append({
                        "adım": f"Adım {adim}",
                        "açıklama": f"Magnezyum Nitrat: {mg_miktar:.2f} mmol/L",
                        "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                    })
                    adim += 1

                # 3. Magnezyum Sülfat
                if "Magnezyum Sülfat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
                    mg_miktar = net_ihtiyac["Mg"]
                    b_tank_gubreler["Magnezyum Sülfat"] = mg_miktar
                    net_ihtiyac["Mg"] = 0
                    net_ihtiyac["SO4"] -= mg_miktar
                    st.session_state.hesaplama_log.append({
                        "adım": f"Adım {adim}",
                        "açıklama": f"Magnezyum Sülfat: {mg_miktar:.2f} mmol/L",
                        "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                    })
                    adim += 1

                # 4. Monopotasyum Fosfat
                if "Monopotasyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
                    mkp_miktar = net_ihtiyac["H2PO4"]
                    b_tank_gubreler["Monopotasyum Fosfat"] = mkp_miktar
                    net_ihtiyac["H2PO4"] = 0
                    net_ihtiyac["K"] -= mkp_miktar
                    st.session_state.hesaplama_log.append({
                        "adım": f"Adım {adim}",
                        "açıklama": f"Monopotasyum Fosfat: {mkp_miktar:.2f} mmol/L",
                        "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                    })
                    adim += 1

                # 5. Monoamonyum Fosfat
                if "Monoamonyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
                    map_miktar = net_ihtiyac["H2PO4"]
                    b_tank_gubreler["Monoamonyum Fosfat"] = map_miktar
                    net_ihtiyac["H2PO4"] = 0
                    net_ihtiyac["NH4"] -= map_miktar
                    st.session_state.hesaplama_log.append({
                        "adım": f"Adım {adim}",
                        "açıklama": f"Monoamonyum Fosfat: {map_miktar:.2f} mmol/L",
                        "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                    })
                    adim += 1

                # 6. Amonyum Sülfat
                if "Amonyum Sülfat" in secilen_gubreler and net_ihtiyac["NH4"] > 0:
                    as_miktar = net_ihtiyac["NH4"] / 2
                    b_tank_gubreler["Amonyum Sülfat"] = as_miktar
                    net_ihtiyac["NH4"] = 0
                    net_ihtiyac["SO4"] -= as_miktar
                    st.session_state.hesaplama_log.append({
                        "adım": f"Adım {adim}",
                        "açıklama": f"Amonyum Sülfat: {as_miktar:.2f} mmol/L",
                        "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                    })
                    adim += 1

                # 7. Potasyum Nitrat
                if "Potasyum Nitrat" in secilen_gubreler and net_ihtiyac["K"] > 0 and net_ihtiyac["NO3"] > 0:
                    kn_miktar = min(net_ihtiyac["K"], net_ihtiyac["NO3"])
                    a_tank_gubreler["Potasyum Nitrat"] = kn_miktar
                    net_ihtiyac["K"] -= kn_miktar
                    net_ihtiyac["NO3"] -= kn_miktar
                    st.session_state.hesaplama_log.append({
                        "adım": f"Adım {adim}",
                        "açıklama": f"Potasyum Nitrat: {kn_miktar:.2f} mmol/L",
                        "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                    })
                    adim += 1

                # 8. Potasyum Sülfat
                if "Potasyum Sülfat" in secilen_gubreler and net_ihtiyac["K"] > 0:
                    ks_miktar = net_ihtiyac["K"] / 2
                    b_tank_gubreler["Potasyum Sülfat"] = ks_miktar
                    net_ihtiyac["K"] = 0
                    net_ihtiyac["SO4"] -= ks_miktar
                    st.session_state.hesaplama_log.append({
                        "adım": f"Adım {adim}",
                        "açıklama": f"Potasyum Sülfat: {ks_miktar:.2f} mmol/L",
                        "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
                    })
                    adim += 1

                # Negatif ihtiyaçları sıfırla
                for iyon in net_ihtiyac:
                    if net_ihtiyac[iyon] < 0:
                        net_ihtiyac[iyon] = 0

                # İyon dengesini hesapla
                eksik_iyonlar, fazla_iyonlar = iyon_dengesini_hesapla(st.session_state.recete, secilen_gubreler)

                # Gübre önerilerini oluştur
                oneriler = gubre_onerileri_olustur(eksik_iyonlar, secilen_gubreler)

                # Mikro besin hesaplamaları
                mikro_sonuc = hesapla_mikro_besinler(
                    st.session_state.recete,
                    st.session_state.secilen_mikro_gubreler,
                    st.session_state.konsantrasyon,
                    st.session_state.b_tank
                )

                # A ve B tankı gübrelerinin kütle hesaplamaları
                a_tank_sonuc, a_tank_toplam = hesapla_tank_gübreleri(
                    a_tank_gubreler, "A", st.session_state.a_tank, st.session_state.konsantrasyon
                )

                b_tank_sonuc, b_tank_toplam = hesapla_tank_gübreleri(
                    b_tank_gubreler, "B", st.session_state.b_tank, st.session_state.konsantrasyon
                )

                # Sonuç bilgilerini saklama
                st.session_state.hesaplama_sonuclari = {
                    "a_tank_sonuc": a_tank_sonuc,
                    "b_tank_sonuc": b_tank_sonuc,
                    "mikro_sonuc": mikro_sonuc,
                    "eksik_iyonlar": eksik_iyonlar,
                    "fazla_iyonlar": fazla_iyonlar,
                    "oneriler": oneriler
                }

                # PDF oluşturma
                try:
                    pdf_bytes = create_pdf(
                        st.session_state.recete,
                        a_tank_sonuc,
                        b_tank_sonuc,
                        mikro_sonuc,
                        eksik_iyonlar,
                        fazla_iyonlar,
                        oneriler
                    )
                    st.download_button(
                        label="📄 Hesaplama Sonuçlarını PDF Olarak İndir",
                        data=pdf_bytes,
                        file_name=f"hydrobuddy_rapor_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.warning(f"PDF oluşturulurken hata: {str(e)}")

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
                else:
                    st.info("Mikro besin elementi eklenmedi.")

                # Eksik ve fazla iyonlar
                st.subheader("Besin Dengesi Değerlendirmesi")
                if eksik_iyonlar:
                    st.error("⚠️ **Eksik İyonlar**")
                    for iyon, miktar in eksik_iyonlar.items():
                        st.write(f"{iyon}: {miktar:.2f} {iyon_bilgileri[iyon]['birim']} eksik")
                if fazla_iyonlar:
                    st.warning("⚠️ **Fazla İyonlar**")
                    for iyon, miktar in fazla_iyonlar.items():
                        st.write(f"{iyon}: {miktar:.2f} {iyon_bilgileri[iyon]['birim']} fazla")
                if not eksik_iyonlar and not fazla_iyonlar:
                    st.success("✅ Tüm besinler ideal olarak karşılandı.")

            except Exception as e:
                st.error(f"Hesaplama sırasında hata: {str(e)}")

# Alt bilgi
st.markdown("---")
st.markdown("HydroBuddy Türkçe | Hidroponik besin çözeltisi hesaplama aracı")
