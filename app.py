import streamlit as st
import pandas as pd
import numpy as np
import base64
from fpdf import FPDF
from io import BytesIO
import datetime

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

# İyon bilgileri ve etkileri 
iyon_bilgileri = {
    "NO3": {
        "ad": "Nitrat", 
        "eksik": "Yapraklarda sararma, bitki gelişiminde yavaşlama, protein sentezinde azalma", 
        "fazla": "Aşırı vejetatif büyüme, çiçeklenme ve meyve oluşumunda gecikme, nitrat birikimi"
    },
    "H2PO4": {
        "ad": "Fosfat", 
        "eksik": "Koyu yeşil/mor yapraklar, kök ve çiçek gelişiminde yavaşlama, zayıf kök sistemi", 
        "fazla": "Diğer besin elementlerinin (özellikle çinko ve demir) alımını engelleme"
    },
    "SO4": {
        "ad": "Sülfat", 
        "eksik": "Yeni yapraklarda sararma, protein sentezinde yavaşlama, enzim aktivitesinde azalma", 
        "fazla": "Yüksek tuzluluk, diğer elementlerin alımında azalma"
    },
    "NH4": {
        "ad": "Amonyum", 
        "eksik": "Protein sentezinde yavaşlama, büyümede durgunluk", 
        "fazla": "Kök gelişiminde zayıflama, toksik etki, hücre zarı hasarı, pH düşüşü"
    },
    "K": {
        "ad": "Potasyum", 
        "eksik": "Yaprak kenarlarında yanma, zayıf kök gelişimi, hastalıklara dayanıksızlık", 
        "fazla": "Magnezyum ve kalsiyum alımını engelleyebilir, tuzluluk artışı"
    },
    "Ca": {
        "ad": "Kalsiyum", 
        "eksik": "Çiçek ucu çürüklüğü, genç yapraklarda deformasyon, kök gelişiminde zayıflama", 
        "fazla": "Diğer minerallerin (özellikle fosfor) alımını engelleyebilir, pH yükselmesi"
    },
    "Mg": {
        "ad": "Magnezyum", 
        "eksik": "Yaşlı yapraklarda damarlar arasında sararma, klorofil azalması, fotosentez düşüşü", 
        "fazla": "Kalsiyum ve potasyum alımında azalma"
    },
    "Fe": {
        "ad": "Demir", 
        "eksik": "Genç yapraklarda damarlar arasında sararma (kloroz), yaprak solgunluğu", 
        "fazla": "Yapraklarda bronzlaşma, diğer mikro besinlerin alımını engelleme"
    },
    "B": {
        "ad": "Bor", 
        "eksik": "Büyüme noktalarında ölüm, çiçeklenmede problemler, kalın ve kırılgan gövde", 
        "fazla": "Yaprak kenarlarında yanma, nekroz, toksik etki"
    },
    "Mn": {
        "ad": "Mangan", 
        "eksik": "Yapraklarda damarlar arasında sararma, yavaş büyüme", 
        "fazla": "Yaşlı yapraklarda nekroz, demir eksikliği belirtileri"
    },
    "Zn": {
        "ad": "Çinko", 
        "eksik": "Yapraklarda kloroz, bodur büyüme, küçük yapraklar", 
        "fazla": "Demir ve mangan alımının engellenmesi, toksik etki"
    },
    "Cu": {
        "ad": "Bakır", 
        "eksik": "Yapraklarda solgunluk, büyüme noktalarında ölüm", 
        "fazla": "Kök gelişiminde inhibisyon, kloroz, diğer mikro besinlerin alımında azalma"
    },
    "Mo": {
        "ad": "Molibden", 
        "eksik": "Azot eksikliğine benzer belirtiler, yapraklarda sararma", 
        "fazla": "Nadiren görülür, aşırı alımı hayvanlarda toksik etki yapabilir"
    }
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

# PDF oluşturma fonksiyonu
def create_pdf(recete, a_tank_sonuc, b_tank_sonuc, mikro_sonuc, eksik_iyonlar, fazla_iyonlar, oneriler):
    pdf = FPDF()
    pdf.add_page()
    
    # Unicode Türkçe karakter desteği için font
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 11)
    
    # Başlık
    pdf.set_font('DejaVu', '', 16)
    pdf.cell(0, 10, 'HydroBuddy Türkçe - Hidroponik Besin Hesaplaması', 0, 1, 'C')
    pdf.set_font('DejaVu', '', 12)
    pdf.cell(0, 10, f'Oluşturulma Tarihi: {datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}', 0, 1, 'C')
    pdf.ln(5)
    
    # Reçete bilgisi
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(0, 10, 'Reçete Değerleri', 0, 1, 'L')
    pdf.set_font('DejaVu', '', 11)
    
    # Anyonlar ve Katyonlar
    pdf.cell(90, 7, 'Anyon (mmol/L)', 1, 0, 'C')
    pdf.cell(90, 7, 'Katyon (mmol/L)', 1, 1, 'C')
    
    max_lines = max(len(["NO3", "H2PO4", "SO4"]), len(["NH4", "K", "Ca", "Mg"]))
    for i in range(max_lines):
        if i < len(["NO3", "H2PO4", "SO4"]):
            ion = ["NO3", "H2PO4", "SO4"][i]
            pdf.cell(45, 7, f"{ion}:", 1, 0, 'L')
            pdf.cell(45, 7, f"{recete[ion]:.2f}", 1, 0, 'R')
        else:
            pdf.cell(45, 7, "", 1, 0, 'L')
            pdf.cell(45, 7, "", 1, 0, 'R')
            
        if i < len(["NH4", "K", "Ca", "Mg"]):
            ion = ["NH4", "K", "Ca", "Mg"][i]
            pdf.cell(45, 7, f"{ion}:", 1, 0, 'L')
            pdf.cell(45, 7, f"{recete[ion]:.2f}", 1, 1, 'R')
        else:
            pdf.cell(45, 7, "", 1, 0, 'L')
            pdf.cell(45, 7, "", 1, 1, 'R')
    
    # Mikro besinler
    pdf.ln(5)
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(0, 10, 'Mikro Besinler (mikromol/L)', 0, 1, 'L')
    pdf.set_font('DejaVu', '', 11)
    
    mikro_elements = ["Fe", "B", "Mn", "Zn", "Cu", "Mo"]
    for i in range(0, len(mikro_elements), 3):
        for j in range(3):
            if i+j < len(mikro_elements):
                element = mikro_elements[i+j]
                pdf.cell(60, 7, f"{element}: {recete.get(element, 0):.1f}", 1, 0, 'L')
            else:
                pdf.cell(60, 7, "", 1, 0, 'L')
        pdf.ln()
    
    # Hesaplanmış gübreler
    pdf.ln(10)
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(0, 10, 'A Tankı Gübreleri', 0, 1, 'L')
    pdf.set_font('DejaVu', '', 11)
    
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
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(0, 10, 'B Tankı Gübreleri', 0, 1, 'L')
    pdf.set_font('DejaVu', '', 11)
    
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
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(0, 10, 'Mikro Besin Elementleri', 0, 1, 'L')
    pdf.set_font('DejaVu', '', 11)
    
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
    
    # Eksik iyonlar
    if eksik_iyonlar:
        pdf.ln(10)
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 10, 'Eksik İyonlar ve Olası Etkileri', 0, 1, 'L')
        pdf.set_font('DejaVu', '', 11)
        
        for iyon, miktar in eksik_iyonlar.items():
            iyon_adi = iyon_bilgileri[iyon]["ad"] if iyon in iyon_bilgileri else iyon
            pdf.multi_cell(0, 7, f"{iyon} ({iyon_adi}) - {miktar:.2f} mmol/L eksik", 0, 'L')
            
            if iyon in iyon_bilgileri:
                pdf.set_font('DejaVu', '', 10)
                pdf.multi_cell(0, 6, f"Olası etkiler: {iyon_bilgileri[iyon]['eksik']}", 0, 'L')
                pdf.set_font('DejaVu', '', 11)
            pdf.ln(2)
    
    # Fazla iyonlar
    if fazla_iyonlar:
        pdf.ln(5)
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 10, 'Fazla İyonlar ve Olası Etkileri', 0, 1, 'L')
        pdf.set_font('DejaVu', '', 11)
        
        for iyon, miktar in fazla_iyonlar.items():
            iyon_adi = iyon_bilgileri[iyon]["ad"] if iyon in iyon_bilgileri else iyon
            pdf.multi_cell(0, 7, f"{iyon} ({iyon_adi}) - {miktar:.2f} mmol/L fazla", 0, 'L')
            
            if iyon in iyon_bilgileri:
                pdf.set_font('DejaVu', '', 10)
                pdf.multi_cell(0, 6, f"Olası etkiler: {iyon_bilgileri[iyon]['fazla']}", 0, 'L')
                pdf.set_font('DejaVu', '', 11)
            pdf.ln(2)
    
    # Gübre önerileri
    if oneriler:
        pdf.ln(5)
        pdf.set_font('DejaVu', '', 14)
        pdf.cell(0, 10, 'Gübre Önerileri', 0, 1, 'L')
        pdf.set_font('DejaVu', '', 11)
        
        for iyon, gubre_listesi in oneriler.items():
            iyon_adi = iyon_bilgileri[iyon]["ad"] if iyon in iyon_bilgileri else iyon
            pdf.multi_cell(0, 7, f"{iyon} ({iyon_adi}) için önerilen gübreler:", 0, 'L')
            
            for gubre in gubre_listesi:
                pdf.multi_cell(0, 6, f"• {gubre}", 0, 'L')
            pdf.ln(2)
    
    pdf.ln(10)
    pdf.set_font('DejaVu', '', 9)
    pdf.cell(0, 5, 'HydroBuddy Türkçe | Hidroponik besin çözeltisi hesaplama aracı', 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin1')

# Session state başlatma fonksiyonu
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

# Session state başlat
session_state_baslat()

# Session state sıfırlama fonksiyonu
def session_state_sifirla():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    session_state_baslat()
    st.success("Session state sıfırlandı!")

# İyonik denge hesaplama fonksiyonu
def hesapla_iyonik_denge(recete):
    anyon_toplam = sum(float(recete[ion]) * abs(iyon_degerlikleri[ion]) for ion in ["NO3", "H2PO4", "SO4"])
    katyon_toplam = sum(float(recete[ion]) * abs(iyon_degerlikleri[ion]) for ion in ["NH4", "K", "Ca", "Mg"])
    return anyon_toplam, katyon_toplam

# Gübre seçimini güncelleme fonksiyonu
def gubre_secimini_guncelle(gubre, secildi):
    if secildi:
        if gubre not in st.session_state.secilen_gubreler:
            st.session_state.secilen_gubreler.append(gubre)
    else:
        if gubre in st.session_state.secilen_gubreler:
            st.session_state.secilen_gubreler.remove(gubre)

# Mikrobesin seçimini güncelleme fonksiyonu
def mikro_gubre_sec(element, secilen_gubre):
    st.session_state.secilen_mikro_gubreler[element] = None if secilen_gubre == "Seçilmedi" else secilen_gubre

# Simulasyon ile besinlerin karşılanıp karşılanamayacağını kontrol etme
def karsilanabilirlik_kontrolu(recete, secilen_gubreler):
    net_ihtiyac = {ion: max(0, float(recete[ion])) for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]}
    
    if "Kalsiyum Nitrat" in secilen_gubreler and net_ihtiyac["Ca"] > 0:
        net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Ca"]
        net_ihtiyac["Ca"] = 0
    if "Magnezyum Nitrat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Mg"]
        net_ihtiyac["Mg"] = 0
    elif "Magnezyum Sülfat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        net_ihtiyac["SO4"] -= net_ihtiyac["Mg"]
        net_ihtiyac["Mg"] = 0
    if "Monopotasyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        net_ihtiyac["K"] -= net_ihtiyac["H2PO4"]
        net_ihtiyac["H2PO4"] = 0
    elif "Monoamonyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        net_ihtiyac["NH4"] -= net_ihtiyac["H2PO4"]
        net_ihtiyac["H2PO4"] = 0
    if "Amonyum Sülfat" in secilen_gubreler and net_ihtiyac["NH4"] > 0:
        as_miktar = min(net_ihtiyac["NH4"] / 2, net_ihtiyac["SO4"])
        net_ihtiyac["NH4"] -= 2 * as_miktar
        net_ihtiyac["SO4"] -= as_miktar
    if "Potasyum Nitrat" in secilen_gubreler and net_ihtiyac["K"] > 0 and net_ihtiyac["NO3"] > 0:
        kn_miktar = min(net_ihtiyac["K"], net_ihtiyac["NO3"])
        net_ihtiyac["K"] -= kn_miktar
        net_ihtiyac["NO3"] -= kn_miktar
    if "Potasyum Sülfat" in secilen_gubreler and net_ihtiyac
