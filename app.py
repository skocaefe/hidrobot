import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import base64

# Sayfa ayarları
st.set_page_config(
    page_title="HydroBuddy İyonik Denge Hesaplayıcı",
    page_icon="🌱",
    layout="wide"
)

# Başlık ve açıklama
st.title("🌱 HydroBuddy İyonik Denge Hesaplayıcı")
st.markdown("Hidroponik besin çözeltilerinde anyon-katyon dengesi ve kimyasal hesaplamalar")

# Gübre bilgilerini içeren veritabanı (Fosforik asit ve nitrik asit çıkarıldı)
gubre_veritabani = {
    "Ca(NO3)2.4H2O": {"formul": "Ca(NO3)2.4H2O", "formul_agirligi": 236.15, 
                      "anyonlar": {"NO3": 2}, "katyonlar": {"Ca": 1}, "a_tank": True},
    "KNO3": {"formul": "KNO3", "formul_agirligi": 101.10, 
             "anyonlar": {"NO3": 1}, "katyonlar": {"K": 1}},
    "NH4NO3": {"formul": "NH4NO3", "formul_agirligi": 80.04, 
               "anyonlar": {"NO3": 1}, "katyonlar": {"NH4": 1}},
    "KH2PO4": {"formul": "KH2PO4", "formul_agirligi": 136.09, 
               "anyonlar": {"H2PO4": 1}, "katyonlar": {"K": 1}, "b_tank": True},
    "K2SO4": {"formul": "K2SO4", "formul_agirligi": 174.26, 
              "anyonlar": {"SO4": 1}, "katyonlar": {"K": 2}},
    "MgSO4.7H2O": {"formul": "MgSO4.7H2O", "formul_agirligi": 246.51, 
                   "anyonlar": {"SO4": 1}, "katyonlar": {"Mg": 1}}
}

# [Mikro besin veritabanı aynı kalacak]

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
    # [Diğer reçeteler aynı kalacak]
}

# EC ve pH hesaplama fonksiyonları
def hesapla_ec(recete):
    # Basit EC hesaplama (yaklaşık değer)
    toplam_iyon = sum(recete.values())
    return round(toplam_iyon * 0.1, 2)  # Her 10 mmol/L için yaklaşık 1 mS/cm

def hesapla_ph(recete):
    # Basit pH hesaplama (yaklaşık değer)
    nh4_orani = recete["NH4"] / (recete["NO3"] + recete["NH4"])
    return round(6.5 - nh4_orani, 1)

# Tank hacmi kontrolü
def kontrol_tank_hacmi(gubreler, tank_hacmi, konsantrasyon):
    toplam_hacim = 0
    for gubre, miktar in gubreler.items():
        hacim = (miktar * gubre_veritabani[gubre]["formul_agirligi"] * konsantrasyon) / 1000
        toplam_hacim += hacim
    return toplam_hacim <= tank_hacmi

# PDF oluşturma fonksiyonu
def olustur_pdf(recete, tank_a, tank_b, konsantrasyon, gubreler):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, f"Gübre Reçetesi")
    c.drawString(100, 720, f"Tank A Kapasitesi: {tank_a} L")
    c.drawString(100, 700, f"Tank B Kapasitesi: {tank_b} L")
    c.drawString(100, 680, f"Konsantrasyon: {konsantrasyon}x")
    
    y = 650
    for gubre, miktar in gubreler.items():
        c.drawString(100, y, f"{gubre}: {miktar:.2f} g")
        y -= 20
    
    c.drawString(100, y-20, f"pH: {hesapla_ph(recete)}")
    c.drawString(100, y-40, f"EC: {hesapla_ec(recete)} mS/cm")
    
    c.save()
    buffer.seek(0)
    return buffer

# Ana uygulama
def main():
    # Tek sayfa tasarımı
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Reçete Seçimi ve Tank Ayarları")
        secilen_recete = st.selectbox("Hazır reçete seçin:", options=list(hazir_receteler.keys()))
        
        col_tank1, col_tank2, col_tank3 = st.columns(3)
        with col_tank1:
            tank_a = st.number_input("A Tankı Hacmi (L):", min_value=1, max_value=1000, value=10)
        with col_tank2:
            tank_b = st.number_input("B Tankı Hacmi (L):", min_value=1, max_value=1000, value=10)
        with col_tank3:
            konsantrasyon = st.number_input("Konsantrasyon Oranı:", min_value=1, max_value=1000, value=100)
    
    # Gübre hesaplama ve sonuçlar
    if st.button("Hesapla"):
        recete = hazir_receteler[secilen_recete]["anyon_katyon"]
        
        # EC ve pH hesaplama
        ec = hesapla_ec(recete)
        ph = hesapla_ph(recete)
        
        # Gübre hesaplama
        gubreler = hesapla_gubreler(recete)
        
        # Tank hacmi kontrolü
        if not kontrol_tank_hacmi(gubreler["a_tank"], tank_a, konsantrasyon):
            st.error("⚠️ A Tankı hacmi yetersiz!")
            return
        
        if not kontrol_tank_hacmi(gubreler["b_tank"], tank_b, konsantrasyon):
            st.error("⚠️ B Tankı hacmi yetersiz!")
            return
        
        # Sonuçları göster
        st.subheader("Sonuçlar")
        col_sonuc1, col_sonuc2 = st.columns(2)
        
        with col_sonuc1:
            st.metric("EC Değeri", f"{ec} mS/cm")
        with col_sonuc2:
            st.metric("pH Değeri", f"{ph}")
        
        # Gübre tabloları
        st.table(pd.DataFrame(gubreler))
        
        # PDF indirme butonu
        pdf = olustur_pdf(recete, tank_a, tank_b, konsantrasyon, gubreler)
        st.download_button(
            label="PDF İndir",
            data=pdf,
            file_name="gubre_recetesi.pdf",
            mime="application/pdf"
        )
    
    # Karışım hazırlama talimatları
    with st.expander("Nasıl Hazırlanır?"):
        st.markdown("""
        1. **A Tankı Hazırlama:**
           - Tank hacminin yarısı kadar su ekleyin
           - Kalsiyum nitratı yavaşça ekleyip karıştırın
           
        2. **B Tankı Hazırlama:**
           - Tank hacminin yarısı kadar su kullanın
           - Sırasıyla potasyum nitrat, magnezyum sülfat ve diğer gübreleri ekleyin
           - Her gübreyi ekledikten sonra tamamen çözünmesini bekleyin
           
        3. **Son İşlemler:**
           - Mikro elementleri en son ekleyin
           - Her iki tankı da son hacimlerine tamamlayın
        """)

if __name__ == "__main__":
    main()
