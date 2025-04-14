import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Sayfa ayarları
st.set_page_config(
    page_title="HydroBuddy Türkçe İyonik Hesaplayıcı",
    page_icon="🌱",
    layout="wide"
)

# Başlık ve açıklama
st.title("🌱 HydroBuddy Türkçe İyonik Hesaplayıcı")
st.markdown("Hidroponik besin çözeltilerinde anyon-katyon dengesi ve kimyasal hesaplamalar")

# Gübre bilgilerini içeren veritabanı
gubre_veritabani = {
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2.4H2O", "formul_agirligi": 236.15, 
                        "anyonlar": {"NO3": 2}, "katyonlar": {"Ca": 1}, "a_tank": True},
    "Potasyum Nitrat": {"formul": "KNO3", "formul_agirligi": 101.10, 
                        "anyonlar": {"NO3": 1}, "katyonlar": {"K": 1}, "a_tank": True},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "formul_agirligi": 136.09, 
                            "anyonlar": {"H2PO4": 1}, "katyonlar": {"K": 1}, "b_tank": True},
    "Potasyum Sülfat": {"formul": "K2SO4", "formul_agirligi": 174.26, 
                         "anyonlar": {"SO4": 1}, "katyonlar": {"K": 2}, "b_tank": True},
    "Magnezyum Sülfat": {"formul": "MgSO4.7H2O", "formul_agirligi": 246.51, 
                         "anyonlar": {"SO4": 1}, "katyonlar": {"Mg": 1}, "b_tank": True},
    "Monoamonyum Fosfat": {"formul": "NH4H2PO4", "formul_agirligi": 115.03, 
                           "anyonlar": {"H2PO4": 1}, "katyonlar": {"NH4": 1}, "b_tank": True},
    "Amonyum Sülfat": {"formul": "(NH4)2SO4", "formul_agirligi": 132.14, 
                       "anyonlar": {"SO4": 1}, "katyonlar": {"NH4": 2}, "b_tank": True},
    "Kalsiyum Klorür": {"formul": "CaCl2.2H2O", "formul_agirligi": 147.02, 
                        "anyonlar": {"Cl": 2}, "katyonlar": {"Ca": 1}, "a_tank": True},
    "Kalsiyum Hidroksit": {"formul": "Ca(OH)2", "formul_agirligi": 74.09, 
                           "anyonlar": {"OH": 2}, "katyonlar": {"Ca": 1}, "a_tank": True},
    "Fosforik Asit": {"formul": "H3PO4", "formul_agirligi": 97.99, 
                      "anyonlar": {"H2PO4": 1}, "katyonlar": {}, "b_tank": True},
    "Nitrik Asit": {"formul": "HNO3", "formul_agirligi": 63.01, 
                    "anyonlar": {"NO3": 1}, "katyonlar": {}, "b_tank": True}
}

# Mikro besin veritabanı
mikro_besin_veritabani = {
    "Demir EDDHA": {"formul": "Fe-EDDHA", "formul_agirligi": 435, "element": "Fe", "b_tank": True},
    "Borak": {"formul": "Na2B4O7.10H2O", "formul_agirligi": 381.37, "element": "B", "b_tank": True},
    "Mangan Sülfat": {"formul": "MnSO4.H2O", "formul_agirligi": 169.02, "element": "Mn", "b_tank": True},
    "Çinko Sülfat": {"formul": "ZnSO4.7H2O", "formul_agirligi": 287.56, "element": "Zn", "b_tank": True},
    "Bakır Sülfat": {"formul": "CuSO4.5H2O", "formul_agirligi": 249.68, "element": "Cu", "b_tank": True},
    "Sodyum Molibdat": {"formul": "Na2MoO4.2H2O", "formul_agirligi": 241.95, "element": "Mo", "b_tank": True}
}

# Hazır reçeteler
hazir_receteler = {
    "Genel Amaçlı": {
        "anyon_katyon": {
            "NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0,
            "NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0
        },
        "mikro": {
            "Fe": 40, "B": 30, "Mn": 5, "Zn": 4, "Cu": 0.75, "Mo": 0.5
        }
    },
    "Domates": {
        "anyon_katyon": {
            "NO3": 14.0, "H2PO4": 1.5, "SO4": 1.5,
            "NH4": 1.2, "K": 7.0, "Ca": 4.0, "Mg": 1.5
        },
        "mikro": {
            "Fe": 50, "B": 40, "Mn": 8, "Zn": 4, "Cu": 0.8, "Mo": 0.5
        }
    },
    "Salatalık": {
        "anyon_katyon": {
            "NO3": 12.0, "H2PO4": 1.3, "SO4": 1.2,
            "NH4": 1.1, "K": 5.8, "Ca": 3.5, "Mg": 1.2
        },
        "mikro": {
            "Fe": 45, "B": 35, "Mn": 6, "Zn": 4, "Cu": 0.75, "Mo": 0.5
        }
    },
    "Marul": {
        "anyon_katyon": {
            "NO3": 10.0, "H2PO4": 1.0, "SO4": 0.8,
            "NH4": 0.8, "K": 4.5, "Ca": 3.0, "Mg": 0.8
        },
        "mikro": {
            "Fe": 35, "B": 25, "Mn": 4, "Zn": 3, "Cu": 0.5, "Mo": 0.4
        }
    },
    "Çilek": {
        "anyon_katyon": {
            "NO3": 11.0, "H2PO4": 1.2, "SO4": 1.0,
            "NH4": 0.9, "K": 5.0, "Ca": 3.2, "Mg": 1.0
        },
        "mikro": {
            "Fe": 40, "B": 30, "Mn": 5, "Zn": 4, "Cu": 0.6, "Mo": 0.4
        }
    }
}

# İyon değerlikleri
iyon_degerlikleri = {
    "NO3": -1, "H2PO4": -1, "SO4": -2, "Cl": -1, "OH": -1,
    "NH4": 1, "K": 1, "Ca": 2, "Mg": 2
}

# Session state başlatma
if 'recete_secimleri' not in st.session_state:
    st.session_state.recete_secimleri = {
        "NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0,
        "NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0
    }

if 'mikro_secimleri' not in st.session_state:
    st.session_state.mikro_secimleri = {
        "Fe": 40, "B": 30, "Mn": 5, "Zn": 4, "Cu": 0.75, "Mo": 0.5
    }

if 'a_tank_hacmi' not in st.session_state:
    st.session_state.a_tank_hacmi = 10  # litre

if 'b_tank_hacmi' not in st.session_state:
    st.session_state.b_tank_hacmi = 10  # litre

if 'konsantrasyon_orani' not in st.session_state:
    st.session_state.konsantrasyon_orani = 100  # 100x

if 'hesaplanmis_gubreler' not in st.session_state:
    st.session_state.hesaplanmis_gubreler = {
        'a_tank': {},
        'b_tank': {},
        'mikro': {}
    }

if 'toplam_gubreler' not in st.session_state:
    st.session_state.toplam_gubreler = {
        'a_tank': 0,  # gram
        'b_tank': 0   # gram
    }

# PDF oluşturma fonksiyonu
def olustur_pdf(a_tank_df, b_tank_df, mikro_df, iyonik_denge_df):
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Başlık
    elements.append(Paragraph("HydroBuddy Türkçe - Gübre Reçetesi", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Tarih
    import datetime
    tarih = datetime.datetime.now().strftime("%d/%m/%Y")
    elements.append(Paragraph(f"Oluşturulma Tarihi: {tarih}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Tank Bilgileri
    elements.append(Paragraph("Tank Bilgileri:", styles['Heading2']))
    tank_data = [
        ["Parametre", "Değer"],
        ["A Tankı Hacmi", f"{st.session_state.a_tank_hacmi} litre"],
        ["B Tankı Hacmi", f"{st.session_state.b_tank_hacmi} litre"],
        ["Konsantrasyon Oranı", f"{st.session_state.konsantrasyon_orani}x"]
    ]
    
    tank_table = Table(tank_data, colWidths=[200, 200])
    tank_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    elements.append(tank_table)
    elements.append(Spacer(1, 12))
    
    # İyonik Denge
    elements.append(Paragraph("İyonik Denge:", styles['Heading2']))
    
    # DataFrame'den liste oluşturma
    iyonik_data = [list(iyonik_denge_df.columns)]
    for row in iyonik_denge_df.values:
        iyonik_data.append(list(row))
    
    iyonik_table = Table(iyonik_data, colWidths=[100, 100, 100])
    iyonik_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    elements.append(iyonik_table)
    elements.append(Spacer(1, 20))
    
    # A Tankı
    elements.append(Paragraph("A Tankı Gübreleri:", styles['Heading2']))
    
    # DataFrame'den liste oluşturma
    if not a_tank_df.empty:
        a_tank_data = [list(a_tank_df.columns)]
        for row in a_tank_df.values:
            a_tank_data.append(list(row))
    else:
        a_tank_data = [["Gübre Adı", "Formül", "mmol/L", "mg/L", "g/Tank"], ["Gübre yok", "-", "-", "-", "-"]]
    
    a_tank_table = Table(a_tank_data, colWidths=[120, 120, 80, 80, 80])
    a_tank_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    elements.append(a_tank_table)
    elements.append(Spacer(1, 20))
    
    # B Tankı
    elements.append(Paragraph("B Tankı Gübreleri:", styles['Heading2']))
    
    # DataFrame'den liste oluşturma
    if not b_tank_df.empty:
        b_tank_data = [list(b_tank_df.columns)]
        for row in b_tank_df.values:
            b_tank_data.append(list(row))
    else:
        b_tank_data = [["Gübre Adı", "Formül", "mmol/L", "mg/L", "g/Tank"], ["Gübre yok", "-", "-", "-", "-"]]
    
    b_tank_table = Table(b_tank_data, colWidths=[120, 120, 80, 80, 80])
    b_tank_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    elements.append(b_tank_table)
    elements.append(Spacer(1, 20))
    
    # Mikro Elementler
    elements.append(Paragraph("Mikro Besin Elementleri:", styles['Heading2']))
    
    # DataFrame'den liste oluşturma
    if not mikro_df.empty:
        mikro_data = [list(mikro_df.columns)]
        for row in mikro_df.values:
            mikro_data.append(list(row))
    else:
        mikro_data = [["Gübre Adı", "Formül", "mikromol/L", "mg/L", "g/Tank"], ["Gübre yok", "-", "-", "-", "-"]]
    
    mikro_table = Table(mikro_data, colWidths=[120, 120, 80, 80, 80])
    mikro_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    elements.append(mikro_table)
    
    # Alt bilgi
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("HydroBuddy Türkçe İyonik Hesaplayıcı ile oluşturulmuştur.", styles['Normal']))
    
    # PDF oluşturma
    doc.build(elements)
    buffer.seek(0)
    
    return buffer

# Tek sayfa düzeni
st.markdown("---")

# Üç sütun oluştur
col1, col2 = st.columns([1, 1])

# Sol sütun: Reçete ve tank ayarları
with col1:
    # Reçete seçimi
    st.subheader("Reçete Seçimi")
    
    secilen_recete = st.selectbox(
        "Hazır reçete seçin:",
        options=list(hazir_receteler.keys()),
        index=0
    )
    
    if st.button("Hazır Reçeteyi Yükle"):
        st.session_state.recete_secimleri = hazir_receteler[secilen_recete]["anyon_katyon"].copy()
        st.session_state.mikro_secimleri = hazir_receteler[secilen_recete]["mikro"].copy()
        st.success(f"{secilen_recete} reçetesi yüklendi!")
    
    # Tank ayarları
    st.subheader("Tank Ayarları")
    
    col_tank1, col_tank2, col_tank3 = st.columns(3)
    
    with col_tank1:
        a_tank_hacmi = st.number_input("A Tankı Hacmi (litre):", 
                                       min_value=1, max_value=1000, 
                                       value=st.session_state.a_tank_hacmi)
        st.session_state.a_tank_hacmi = a_tank_hacmi
    
    with col_tank2:
        b_tank_hacmi = st.number_input("B Tankı Hacmi (litre):", 
                                       min_value=1, max_value=1000, 
                                       value=st.session_state.b_tank_hacmi)
        st.session_state.b_tank_hacmi = b_tank_hacmi
    
    with col_tank3:
        konsantrasyon_orani = st.number_input("Konsantrasyon Oranı:", 
                                             min_value=1, max_value=1000, 
                                             value=st.session_state.konsantrasyon_orani)
        st.session_state.konsantrasyon_orani = konsantrasyon_orani
    
    # Anyon/Katyon değerleri
    st.subheader("Anyon/Katyon Değerleri")
    
    st.write("**Anyon Değerleri (mmol/L)**")
    col_anyon1, col_anyon2, col_anyon3 = st.columns(3)
    
    with col_anyon1:
        no3_value = st.number_input("NO3 (Nitrat)", 
                           min_value=0.0, max_value=30.0, 
                           value=float(st.session_state.recete_secimleri["NO3"]), 
                           step=0.1, format="%.2f")
        st.session_state.recete_secimleri["NO3"] = no3_value
    
    with col_anyon2:
        h2po4_value = st.number_input("H2PO4 (Fosfat)", 
                           min_value=0.0, max_value=10.0, 
                           value=float(st.session_state.recete_secimleri["H2PO4"]), 
                           step=0.1, format="%.2f")
        st.session_state.recete_secimleri["H2PO4"] = h2po4_value
    
    with col_anyon3:
        so4_value = st.number_input("SO4 (Sülfat)", 
                           min_value=0.0, max_value=10.0, 
                           value=float(st.session_state.recete_secimleri["SO4"]), 
                           step=0.1, format="%.2f")
        st.session_state.recete_secimleri["SO4"] = so4_value
    
    st.write("**Katyon Değerleri (mmol/L)**")
    col_kat1, col_kat2, col_kat3, col_kat4 = st.columns(4)
    
    with col_kat1:
        nh4_value = st.number_input("NH4 (Amonyum)", 
                           min_value=0.0, max_value=10.0, 
                           value=float(st.session_state.recete_secimleri["NH4"]), 
                           step=0.1, format="%.2f")
        st.session_state.recete_secimleri["NH4"] = nh4_value
    
    with col_kat2:
        k_value = st.number_input("K (Potasyum)", 
                           min_value=0.0, max_value=20.0, 
                           value=float(st.session_state.recete_secimleri["K"]), 
                           step=0.1, format="%.2f")
        st.session_state.recete_secimleri["K"] = k_value
    
    with col_kat3:
        ca_value = st.number_input("Ca (Kalsiyum)", 
                           min_value=0.0, max_value=15.0, 
                           value=float(st.session_state.recete_secimleri["Ca"]), 
                           step=0.1, format="%.2f")
        st.session_state.recete_secimleri["Ca"] = ca_value
    
    with col_kat4:
        mg_value = st.number_input("Mg (Magnezyum)", 
                           min_value=0.0, max_value=10.0, 
                           value=float(st.session_state.recete_secimleri["Mg"]), 
                           step=0.1, format="%.2f")
        st.session_state.recete_secimleri["Mg"] = mg_value
    
    # Mikro besin elementleri
    st.subheader("Mikro Besin Elementleri (mikromol/L)")
    
    col_mikro1, col_mikro2, col_mikro3 = st.columns(3)
    col_mikro4, col_mikro5, col_mikro6 = st.columns(3)
    
    with col_mikro1:
        fe_value = st.number_input("Fe (Demir)", 
                           min_value=0.0, max_value=100.0, 
                           value=float(st.session_state.mikro_secimleri["Fe"]), 
                           step=1.0, format="%.1f")
        st.session_state.mikro_secimleri["Fe"] = fe_value
    
    with col_mikro2:
        b_value = st.number_input("B (Bor)", 
                           min_value=0.0, max_value=100.0, 
                           value=float(st.session_state.mikro_secimleri["B"]), 
                           step=1.0, format="%.1f")
        st.session_state.mikro_secimleri["B"] = b_value
    
    with col_mikro3:
        mn_value = st.number_input("Mn (Mangan)", 
                           min_value=0.0, max_value=50.0, 
                           value=float(st.session_state.mikro_secimleri["Mn"]), 
                           step=0.5, format="%.1f")
        st.session_state.mikro_secimleri["Mn"] = mn_value
    
    with col_mikro4:
        zn_value = st.number_input("Zn (Çinko)", 
                           min_value=0.0, max_value=50.0, 
                           value=float(st.session_state.mikro_secimleri["Zn"]), 
                           step=0.5, format="%.1f")
        st.session_state.mikro_secimleri["Zn"] = zn_value
    
    with col_mikro5:
        cu_value = st.number_input("Cu (Bakır)", 
                           min_value=0.0, max_value=10.0, 
                           value=float(st.session_state.mikro_secimleri["Cu"]), 
                           step=0.05, format="%.2f")
        st.session_state.mikro_secimleri["Cu"] = cu_value
    
    with col_mikro6:
        mo_value = st.number_input("Mo (Molibden)", 
                           min_value=0.0, max_value=10.0, 
                           value=float(st.session_state.mikro_secimleri["Mo"]), 
                           step=0.05, format="%.2f")
        st.session_state.mikro_secimleri["Mo"] = mo_value

# Sağ sütun: İyonik denge ve gübre hesaplama
with col2:
    # İyonik denge hesaplama fonksiyonu
    def hesapla_iyonik_denge(recete):
        anyon_toplam_me = 0
        katyon_toplam_me = 0
        
        # Anyonlar
        for anyon in ["NO3", "H2PO4", "SO4"]:
            if anyon in recete:
                deger = recete[anyon]
                valens = abs(iyon_degerlikleri[anyon])
                anyon_toplam_me += deger * valens
        
        # Katyonlar
        for katyon in ["NH4", "K", "Ca", "Mg"]:
            if katyon in recete:
                deger = recete[katyon]
                valens = abs(iyon_degerlikleri[katyon])
                katyon_toplam_me += deger * valens
        
        return anyon_toplam_me, katyon_toplam_me
    
    # İyonik denge değerlerini hesapla
    anyon_me, katyon_me = hesapla_iyonik_denge(st.session_state.recete_secimleri)
    
    # İyonik Denge Tablosu
    st.subheader("İyonik Denge Tablosu")
    
    # Anyon tablosu
    anyon_data = []
    for anyon in ["NO3", "H2PO4", "SO4"]:
        deger = st.session_state.recete_secimleri[anyon]
        valens = abs(iyon_degerlikleri[anyon])
        me = deger * valens
        anyon_data.append([anyon, f"{deger:.2f}", f"{me:.2f}"])
    
    anyon_df = pd.DataFrame(anyon_data, columns=["Anyon", "mmol/L", "me/L"])
    
    # Katyon tablosu
    katyon_data = []
    for katyon in ["NH4", "K", "Ca", "Mg"]:
        deger = st.session_state.recete_secimleri[katyon]
        valens = abs(iyon_degerlikleri[katyon])
        me = deger * valens
        katyon_data.append([katyon, f"{deger:.2f}", f"{me:.2f}"])
    
    katyon_df = pd.DataFrame(katyon_data, columns=["Katyon", "mmol/L", "me/L"])
    
    # İki tabloyu yan yana göster
    col_tablo1, col_tablo2 = st.columns(2)
    
    with col_tablo1:
        st.dataframe(anyon_df)
        anyon_toplam_mm
