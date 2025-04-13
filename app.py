# -*- coding: utf-8 -*-
# HydroBuddy Türkçe Streamlit Versiyonu
# Orijinal: Daniel Fernandez
# Streamlit uyarlaması: [Sizin Adınız]

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import os
import base64
from io import BytesIO

# Sayfa ayarları
st.set_page_config(
    page_title="HydroBuddy Türkçe",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile bazı özelleştirmeler
st.markdown("""
    <style>
    .main {
        background-color: #f0f8ff;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #2E8B57;
    }
    .warning {
        color: #FF5733;
    }
    .success {
        color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

# Veritabanı işlemleri için sınıf
class Veritabani:
    def __init__(self, db_yolu="hidroponik.db"):
        # Veritabanı oluştur (eğer yoksa)
        self.baglanti = sqlite3.connect(db_yolu)
        self.cursor = self.baglanti.cursor()
        self.veritabani_olustur()
    
    def veritabani_olustur(self):
        """Veritabanı tablolarını oluşturur (eğer yoksa)"""
        
        # Gübreler tablosu
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS gubreler (
            id INTEGER PRIMARY KEY,
            isim TEXT,
            n_nitrat REAL,
            n_amonyum REAL,
            p REAL,
            k REAL,
            ca REAL,
            mg REAL,
            s REAL,
            fe REAL,
            mn REAL,
            zn REAL,
            b REAL,
            cu REAL,
            mo REAL,
            turk_market INTEGER
        )
        ''')
        
        # Bitki profilleri tablosu
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS bitki_profilleri (
            id INTEGER PRIMARY KEY,
            isim TEXT,
            n REAL,
            p REAL,
            k REAL,
            ca REAL,
            mg REAL,
            s REAL,
            fe REAL,
            mn REAL,
            zn REAL,
            b REAL,
            cu REAL,
            mo REAL
        )
        ''')
        
        # Türkiye'de yaygın bulunan birkaç gübre ekleyelim
        self.turkiye_gubreleri_ekle()
        
        # Örnek bitki profilleri ekleyelim
        self.ornek_profiller_ekle()
        
        self.baglanti.commit()
    
    def turkiye_gubreleri_ekle(self):
        """Türkiye'de yaygın olarak bulunan gübreleri veritabanına ekler"""
        
        # Önce tabloda veri var mı kontrol edelim
        self.cursor.execute("SELECT COUNT(*) FROM gubreler WHERE turk_market=1")
        if self.cursor.fetchone()[0] > 0:
            return  # Zaten eklenmiş
        
        # Türkiye'de yaygın bulunan gübreler
        gubreler = [
            ("Kalsiyum Nitrat", 14.4, 1.1, 0, 0, 19, 0, 0, 0, 0, 0, 0, 0, 0, 1),
            ("Potasyum Nitrat", 13, 0, 0, 38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
            ("Magnezyum Sülfat (Epsom Tuzu)", 0, 0, 0, 0, 0, 9.9, 13, 0, 0, 0, 0, 0, 0, 1),
            ("Mono Potasyum Fosfat", 0, 0, 22.3, 28.2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
            ("Demir Şelat (EDTA)", 0, 0, 0, 0, 0, 0, 0, 13, 0, 0, 0, 0, 0, 1),
            ("Mangan Sülfat", 0, 0, 0, 0, 0, 0, 0, 0, 32, 0, 0, 0, 0, 1),
            ("Çinko Sülfat", 0, 0, 0, 0, 0, 0, 0, 0, 0, 23, 0, 0, 0, 1),
            ("Borik Asit", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 17, 0, 0, 1),
            ("Bakır Sülfat", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 25, 0, 1),
            ("Sodyum Molibdat", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 39, 1)
        ]
        
        for gubre in gubreler:
            self.cursor.execute("""
            INSERT INTO gubreler (
                isim, n_nitrat, n_amonyum, p, k, ca, mg, s, fe, mn, zn, b, cu, mo, turk_market
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, gubre)
        
        self.baglanti.commit()
    
    def ornek_profiller_ekle(self):
        """Örnek bitki profillerini veritabanına ekler"""
        
        # Önce tabloda veri var mı kontrol edelim
        self.cursor.execute("SELECT COUNT(*) FROM bitki_profilleri")
        if self.cursor.fetchone()[0] > 0:
            return  # Zaten eklenmiş
        
        # Örnek bitki profilleri
        profiller = [
            ("Genel Amaçlı", 150, 50, 210, 200, 50, 65, 3, 0.5, 0.15, 0.5, 0.15, 0.1),
            ("Domates", 180, 45, 300, 190, 50, 70, 4, 0.8, 0.3, 0.7, 0.15, 0.1),
            ("Salatalık", 160, 60, 230, 170, 45, 60, 3, 0.5, 0.2, 0.5, 0.1, 0.05),
            ("Marul", 120, 40, 180, 150, 40, 50, 2.5, 0.4, 0.1, 0.4, 0.1, 0.05),
            ("Çilek", 140, 55, 220, 180, 45, 55, 3.5, 0.6, 0.25, 0.6, 0.12, 0.08)
        ]
        
        for profil in profiller:
            self.cursor.execute("""
            INSERT INTO bitki_profilleri (
                isim, n, p, k, ca, mg, s, fe, mn, zn, b, cu, mo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, profil)
        
        self.baglanti.commit()
    
    def gubre_listesi_getir(self, sadece_turk=True):
        """Gübre listesini döndürür"""
        if sadece_turk:
            self.cursor.execute("SELECT id, isim FROM gubreler WHERE turk_market=1")
        else:
            self.cursor.execute("SELECT id, isim FROM gubreler")
        return self.cursor.fetchall()
    
    def gubre_bilgilerini_getir(self, gubre_id):
        """Belirli bir gübrenin detaylarını getirir"""
        self.cursor.execute("""
        SELECT isim, n_nitrat, n_amonyum, p, k, ca, mg, s, fe, mn, zn, b, cu, mo
        FROM gubreler WHERE id=?
        """, (gubre_id,))
        return self.cursor.fetchone()
    
    def bitki_profilleri_getir(self):
        """Kayıtlı bitki profillerini döndürür"""
        self.cursor.execute("SELECT id, isim FROM bitki_profilleri")
        return self.cursor.fetchall()
    
    def profil_detaylarini_getir(self, profil_id):
        """Belirli bir bitki profilinin detaylarını getirir"""
        self.cursor.execute("""
        SELECT isim, n, p, k, ca, mg, s, fe, mn, zn, b, cu, mo
        FROM bitki_profilleri WHERE id=?
        """, (profil_id,))
        return self.cursor.fetchone()
    
    def kapat(self):
        """Veritabanı bağlantısını kapatır"""
        self.baglanti.close()

# Besin çözeltisi hesaplama sınıfı
class BesinHesaplayici:
    def __init__(self, hacim_litre=20):
        self.hacim_litre = hacim_litre
        self.hedef_ppm = {
            'N': 150,
            'P': 50,
            'K': 210,
            'Ca': 200,
            'Mg': 50,
            'S': 65,
            'Fe': 3,
            'Mn': 0.5,
            'Zn': 0.15,
            'B': 0.5,
            'Cu': 0.15,
            'Mo': 0.1
        }
        self.secilen_gubreler = []  # (gubre_id, miktar_gram) tuple'larını içerecek
    
    def hacim_ayarla(self, yeni_hacim):
        """Su hacmini değiştirir"""
        self.hacim_litre = yeni_hacim
    
    def hedef_degeri_ayarla(self, besin, deger):
        """Hedef ppm değerini değiştirir"""
        if besin in self.hedef_ppm:
            self.hedef_ppm[besin] = deger
    
    def gubre_ekle(self, gubre_id, miktar_gram):
        """Karışıma gübre ekler"""
        self.secilen_gubreler.append((gubre_id, miktar_gram))
    
    def gubre_cikar(self, index):
        """Karışımdan gübre çıkarır"""
        if 0 <= index < len(self.secilen_gubreler):
            self.secilen_gubreler.pop(index)
    
    def tum_gubreleri_temizle(self):
        """Tüm gübreleri temizler"""
        self.secilen_gubreler = []
    
    def sonuc_hesapla(self, veritabani):
        """Seçilen gübrelerle elde edilecek besin değerlerini hesaplar"""
        sonuc = {
            'N': 0,
            'P': 0,
            'K': 0,
            'Ca': 0,
            'Mg': 0,
            'S': 0,
            'Fe': 0,
            'Mn': 0,
            'Zn': 0,
            'B': 0,
            'Cu': 0,
            'Mo': 0
        }
        
        for gubre_id, miktar_gram in self.secilen_gubreler:
            gubre_bilgi = veritabani.gubre_bilgilerini_getir(gubre_id)
            if gubre_bilgi:
                # N (nitrat + amonyum)
                sonuc['N'] += (gubre_bilgi[1] + gubre_bilgi[2]) * miktar_gram / self.hacim_litre
                # P
                sonuc['P'] += gubre_bilgi[3] * miktar_gram / self.hacim_litre
                # K
                sonuc['K'] += gubre_bilgi[4] * miktar_gram / self.hacim_litre
                # Ca
                sonuc['Ca'] += gubre_bilgi[5] * miktar_gram / self.hacim_litre
                # Mg
                sonuc['Mg'] += gubre_bilgi[6] * miktar_gram / self.hacim_litre
                # S
                sonuc['S'] += gubre_bilgi[7] * miktar_gram / self.hacim_litre
                # Fe
                sonuc['Fe'] += gubre_bilgi[8] * miktar_gram / self.hacim_litre
                # Mn
                sonuc['Mn'] += gubre_bilgi[9] * miktar_gram / self.hacim_litre
                # Zn
                sonuc['Zn'] += gubre_bilgi[10] * miktar_gram / self.hacim_litre
                # B
                sonuc['B'] += gubre_bilgi[11] * miktar_gram / self.hacim_litre
                # Cu
                sonuc['Cu'] += gubre_bilgi[12] * miktar_gram / self.hacim_litre
                # Mo
                sonuc['Mo'] += gubre_bilgi[13] * miktar_gram / self.hacim_litre
        
        return sonuc
    
    def profil_yukle(self, veritabani, profil_id):
        """Bitki profiline göre hedef değerleri ayarlar"""
        profil = veritabani.profil_detaylarini_getir(profil_id)
        if profil:
            self.hedef_ppm['N'] = profil[1]
            self.hedef_ppm['P'] = profil[2]
            self.hedef_ppm['K'] = profil[3]
            self.hedef_ppm['Ca'] = profil[4]
            self.hedef_ppm['Mg'] = profil[5]
            self.hedef_ppm['S'] = profil[6]
            self.hedef_ppm['Fe'] = profil[7]
            self.hedef_ppm['Mn'] = profil[8]
            self.hedef_ppm['Zn'] = profil[9]
            self.hedef_ppm['B'] = profil[10]
            self.hedef_ppm['Cu'] = profil[11]
            self.hedef_ppm['Mo'] = profil[12]
            return True
        return False

def main():
    # Uygulama başlığı
    st.title("🌱 HydroBuddy Türkçe")
    st.markdown("**Hidroponik Besin Çözeltisi Hesaplayıcı**")
    
    # Veritabanı ve hesaplayıcı nesnelerini oluştur
    veritabani = Veritabani()
    
    # Session state ile hesaplayıcı ve formül verilerini kaydet
    if 'hesaplayici' not in st.session_state:
        st.session_state.hesaplayici = BesinHesaplayici()
    
    if 'eklenen_gubreler' not in st.session_state:
        st.session_state.eklenen_gubreler = []  # [(isim, id, miktar)]
    
    # Sidebar: Bitki profili ve hacim ayarları
    with st.sidebar:
        st.header("Ayarlar")
        
        # Bitki profili seçimi
        st.subheader("Bitki Profili")
        
        profiller = veritabani.bitki_profilleri_getir()
        profil_secenekler = [p[1] for p in profiller]
        secili_profil = st.selectbox("Profil seçin:", profil_secenekler, index=0)
        
        if st.button("Profili Yükle"):
            secili_index = profil_secenekler.index(secili_profil)
            profil_id = profiller[secili_index][0]
            
            if st.session_state.hesaplayici.profil_yukle(veritabani, profil_id):
                st.success(f"{secili_profil} profili yüklendi!")
            else:
                st.error("Profil yüklenirken bir sorun oluştu.")
        
        # Hacim ayarı
        st.subheader("Su Hacmi")
        yeni_hacim = st.number_input(
            "Çözelti hacmi (litre):",
            min_value=1,
            max_value=1000,
            value=int(st.session_state.hesaplayici.hacim_litre)
        )
        
        if st.button("Hacmi Güncelle"):
            st.session_state.hesaplayici.hacim_ayarla(yeni_hacim)
            st.success(f"Hacim {yeni_hacim} litre olarak güncellendi!")
        
        # Bilgi kutusu
        st.info("""
        **Gübre Önerileri:**
        
        Genel Hidroponik için:
        - Kalsiyum Nitrat
        - Potasyum Nitrat
        - Mono Potasyum Fosfat
        - Magnezyum Sülfat
        - Mikro element karışımı
        
        Domates/Biber için K değerini artırın.
        Yapraklı bitkiler için N değerini artırın.
        """)
    
    # Ana bölüm: 3 sütuna böl
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # 1. Sütun: Gübre ekleme
    with col1:
        st.header("Gübre Ekle")
        
        # Gübre seçimi
        gubreler = veritabani.gubre_listesi_getir(sadece_turk=True)
        gubre_secenekler = [g[1] for g in gubreler]
        secili_gubre = st.selectbox("Gübre seçin:", gubre_secenekler)
        
        secili_index = gubre_secenekler.index(secili_gubre)
        secili_id = gubreler[secili_index][0]
        
        # Gübre miktarı
        miktar = st.number_input(
            "Miktar (gram):",
            min_value=0.1,
            max_value=1000.0,
            value=1.0,
            step=0.1,
            format="%.1f"
        )
        
        # Ekleme butonu
        if st.button("Gübre Ekle"):
            # Hesaplayıcıya ekle
            st.session_state.hesaplayici.gubre_ekle(secili_id, miktar)
            
            # Görüntüleme için listeye ekle
            st.session_state.eklenen_gubreler.append((secili_gubre, secili_id, miktar))
            
            st.success(f"{secili_gubre} ({miktar}g) eklendi!")
    
    # 2. Sütun: Eklenen gübreler ve hesaplama
    with col2:
        st.header("Eklenen Gübreler")
        
        if not st.session_state.eklenen_gubreler:
            st.info("Henüz gübre eklenmedi.")
        else:
            # Gübre listesini tablo olarak göster
            gubre_df = pd.DataFrame(
                [(i+1, g[0], g[2]) for i, g in enumerate(st.session_state.eklenen_gubreler)],
                columns=["#", "Gübre Adı", "Miktar (g)"]
            )
            st.table(gubre_df)
            
            # Gübre silme
            silinecek = st.number_input(
                "Silmek istediğiniz gübrenin numarası:",
                min_value=1,
                max_value=len(st.session_state.eklenen_gubreler),
                value=1
            )
            
            if st.button("Seçili Gübreyi Sil"):
                indeks = silinecek - 1
                st.session_state.hesaplayici.gubre_cikar(indeks)
                silinen = st.session_state.eklenen_gubreler.pop(indeks)
                st.warning(f"{silinen[0]} silindi!")
        
        # Tümünü temizle
        if st.button("Tüm Gübreleri Temizle"):
            st.session_state.hesaplayici.tum_gubreleri_temizle()
            st.session_state.eklenen_gubreler = []
            st.warning("Tüm gübreler temizlendi!")
        
        # Hesaplama butonu
        st.markdown("---")
        if st.button("HESAPLA", use_container_width=True):
            st.session_state.hesaplayici.hacim_ayarla(yeni_hacim)  # Son hacim değerini kullan
            st.success("Hesaplama tamamlandı!")
    
    # 3. Sütun: Sonuçlar
    with col3:
        st.header("Sonuçlar")
        
        # Hesaplama sonuçları
        sonuclar = st.session_state.hesaplayici.sonuc_hesapla(veritabani)
        hedefler = st.session_state.hesaplayici.hedef_ppm
        
        # Tabloya dönüştür
        sonuc_data = []
        for besin in ['N', 'P', 'K', 'Ca', 'Mg', 'S', 'Fe', 'Mn', 'Zn', 'B', 'Cu', 'Mo']:
            hedef = hedefler[besin]
            sonuc = sonuclar[besin]
            
            # Durum hesapla (Düşük, İyi, Yüksek)
            if sonuc < hedef * 0.8:
                durum = "⚠️ Düşük"
            elif sonuc > hedef * 1.2:
                durum = "⚠️ Yüksek"
            else:
                durum = "✅ İyi"
            
            sonuc_data.append([besin, f"{hedef:.2f}", f"{sonuc:.2f}", durum])
        
        sonuc_df = pd.DataFrame(sonuc_data, columns=["Besin", "Hedef (ppm)", "Sonuç (ppm)", "Durum"])
        st.table(sonuc_df)
    
    # Grafik gösterimi (tüm genişliği kullan)
    st.markdown("---")
    st.header("Grafik Gösterimi")
    
    # Makro ve mikro besinleri ayrı ayrı göster
    col_makro, col_mikro = st.columns(2)
    
    with col_makro:
        st.subheader("Makro Besinler")
        
        makro_fig, ax = plt.subplots(figsize=(10, 6))
        
        makrolar = ['N', 'P', 'K', 'Ca', 'Mg', 'S']
        hedef_degerler = [st.session_state.hesaplayici.hedef_ppm[b] for b in makrolar]
        sonuc_degerler = [sonuclar[b] for b in makrolar]
        
        x = range(len(makrolar))
        width = 0.35
        
        ax.bar(np.array(x) - width/2, hedef_degerler, width, label='Hedef', color='blue', alpha=0.6)
        ax.bar(np.array(x) + width/2, sonuc_degerler, width, label='Sonuç', color='green', alpha=0.6)
        
        ax.set_ylabel('ppm')
        ax.set_title('Makro Besinler Karşılaştırma')
        ax.set_xticks(x)
        ax.set_xticklabels(makrolar)
        ax.legend()
        
        st.pyplot(makro_fig)
    
    with col_mikro:
        st.subheader("Mikro Besinler")
        
        mikro_fig, ax = plt.subplots(figsize=(10, 6))
        
        mikrolar = ['Fe', 'Mn', 'Zn', 'B', 'Cu', 'Mo']
        hedef_degerler = [st.session_state.hesaplayici.hedef_ppm[b] for b in mikrolar]
        sonuc_degerler = [sonuclar[b] for b in mikrolar]
        
        x = range(len(mikrolar))
        width = 0.35
        
        ax.bar(np.array(x) - width/2, hedef_degerler, width, label='Hedef', color='blue', alpha=0.6)
        ax.bar(np.array(x) + width/2, sonuc_degerler, width, label='Sonuç', color='green', alpha=0.6)
        
        ax.set_ylabel('ppm')
        ax.set_title('Mikro Besinler Karşılaştırma')
        ax.set_xticks(x)
        ax.set_xticklabels(mikrolar)
        ax.legend()
        
        st.pyplot(mikro_fig)
    
    # Rapor indirme
    st.markdown("---")
    
    def create_download_report():
        # Rapor içeriği
        buffer = BytesIO()
        
        # Besin sonuçları
        sonuclar = st.session_state.hesaplayici.sonuc_hesapla(veritabani)
        
        # Pandas DataFrame kullanarak PDF raporu oluştur
        sonuc_data = []
        for besin in ['N', 'P', 'K', 'Ca', 'Mg', 'S', 'Fe', 'Mn', 'Zn', 'B', 'Cu', 'Mo']:
            hedef = st.session_state.hesaplayici.hedef_ppm[besin]
            sonuc = sonuclar[besin]
            
            if sonuc < hedef * 0.8:
                durum = "Düşük"
            elif sonuc > hedef * 1.2:
                durum = "Yüksek"
            else:
                durum = "İyi"
            
            sonuc_data.append([besin, f"{hedef:.2f}", f"{sonuc:.2f}", durum])
        
        sonuc_df = pd.DataFrame(sonuc_data, columns=["Besin", "Hedef (ppm)", "Sonuç (ppm)", "Durum"])
        
        # Excel dosyası oluştur
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Gübre listesi
            gubre_data = [(g[0], g[2]) for g in st.session_state.eklenen_gubreler]
            gubre_df = pd.DataFrame(gubre_data, columns=["Gübre Adı", "Miktar (g)"])
            gubre_df.to_excel(writer, sheet_name='Gübreler', index=False)
            
            # Sonuç tablosu
            sonuc_df.to_excel(writer, sheet_name='Sonuçlar', index=False)
            
            # Ayarlar
            ayarlar_data = [
                ["Hacim (litre)", st.session_state.hesaplayici.hacim_litre],
                ["Bitki Profili", secili_profil]
            ]
            ayarlar_df = pd.DataFrame(ayarlar_data, columns=["Ayar", "Değer"])
            ayarlar_df.to_excel(writer, sheet_name='Ayarlar', index=False)
        
        return buffer
    
    if st.download_button(
        label="Raporu İndir (Excel)",
        data=create_download_report().getvalue(),
        file_name="HydroBuddy_Rapor.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ):
        st.success("Rapor başarıyla indirildi!")
    
    # Alt bilgi
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <p>HydroBuddy Türkçe Versiyonu</p>
        <p>Orijinal: <a href="https://github.com/danielfppps/hydrobuddy">Daniel Fernandez</a> • Türkçe uyarlama: [Sizin Adınız]</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
