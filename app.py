# -*- coding: utf-8 -*-
# HydroBuddy Türkçe Streamlit Versiyonu - Basit Otomatik Formül Oluşturucu
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
    page_title="HydroBuddy Türkçe - Otomatik Formül",
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
            ("Sodyum Molibdat", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 39, 1),
            ("Amonyum Nitrat", 17, 17, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
            ("Üre", 0, 46, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
            ("Süper Fosfat", 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
            ("Potasyum Sülfat", 0, 0, 0, 42, 0, 0, 18, 0, 0, 0, 0, 0, 0, 1),
            ("Mikro Element Karışımı", 0, 0, 0, 0, 0, 0, 0, 7, 2, 0.4, 1.5, 0.1, 0.06, 1)
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
            ("Çilek", 140, 55, 220, 180, 45, 55, 3.5, 0.6, 0.25, 0.6, 0.12, 0.08),
            ("Biber", 170, 50, 280, 180, 45, 65, 3.5, 0.7, 0.2, 0.6, 0.15, 0.1),
            ("Patlıcan", 160, 50, 250, 190, 50, 60, 3, 0.6, 0.2, 0.6, 0.15, 0.1),
            ("Çiçekli Bitkiler", 120, 60, 240, 170, 40, 55, 3, 0.5, 0.2, 0.5, 0.1, 0.05),
            ("Yapraklı Sebzeler", 140, 40, 150, 140, 40, 50, 2.5, 0.4, 0.15, 0.4, 0.1, 0.05),
            ("Fide Evresi", 100, 60, 150, 120, 30, 40, 2, 0.3, 0.1, 0.3, 0.1, 0.05)
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
    
    def tum_gubre_bilgilerini_getir(self, sadece_turk=True):
        """Tüm gübrelerin detaylarını içeren bir liste döndürür"""
        if sadece_turk:
            self.cursor.execute("""
            SELECT id, isim, n_nitrat, n_amonyum, p, k, ca, mg, s, fe, mn, zn, b, cu, mo
            FROM gubreler WHERE turk_market=1
            """)
        else:
            self.cursor.execute("""
            SELECT id, isim, n_nitrat, n_amonyum, p, k, ca, mg, s, fe, mn, zn, b, cu, mo
            FROM gubreler
            """)
        return self.cursor.fetchall()
    
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

class BasitFormulOlusturucu:
    def __init__(self, veritabani, hedef_ppm, hacim_litre=20):
        self.veritabani = veritabani
        self.hedef_ppm = hedef_ppm
        self.hacim_litre = hacim_litre
        
    def formul_olustur(self):
        """
        Basit bir formül oluşturur.
        
        Returns:
            (secilen_gubreler, sonuc_ppm) tuple
            secilen_gubreler: [(gubre_id, gubre_ismi, miktar), ...]
            sonuc_ppm: {'N': değer, 'P': değer, ...}
        """
        # Tüm gübreleri al
        gubreler = self.veritabani.tum_gubre_bilgilerini_getir(sadece_turk=True)
        
        # Formülümüzde kullanılacak ortak gübreler
        temel_formul = []
        
        # 1. N kaynağı: Kalsiyum Nitrat (yaklaşık 10g)
        kalsiyum_nitrat_id = None
        for gubre in gubreler:
            if "Kalsiyum Nitrat" in gubre[1]:
                kalsiyum_nitrat_id = gubre[0]
                temel_formul.append((gubre[0], gubre[1], 10.0))
                break
        
        # 2. P kaynağı: Mono Potasyum Fosfat (yaklaşık 2g)
        mpf_id = None
        for gubre in gubreler:
            if "Mono Potasyum Fosfat" in gubre[1]:
                mpf_id = gubre[0]
                temel_formul.append((gubre[0], gubre[1], 2.0))
                break
        
        # 3. K kaynağı: Potasyum Nitrat (yaklaşık 5g)
        potasyum_nitrat_id = None
        for gubre in gubreler:
            if "Potasyum Nitrat" in gubre[1]:
                potasyum_nitrat_id = gubre[0]
                temel_formul.append((gubre[0], gubre[1], 5.0))
                break
        
        # 4. Mg kaynağı: Magnezyum Sülfat (yaklaşık 5g)
        magnezyum_sulfat_id = None
        for gubre in gubreler:
            if "Magnezyum Sülfat" in gubre[1]:
                magnezyum_sulfat_id = gubre[0]
                temel_formul.append((gubre[0], gubre[1], 5.0))
                break
        
        # 5. Mikro elementler (yaklaşık 2g)
        mikro_id = None
        for gubre in gubreler:
            if "Mikro Element" in gubre[1]:
                mikro_id = gubre[0]
                temel_formul.append((gubre[0], gubre[1], 2.0))
                break
        
        # Eğer mikro element karışımı bulunamazsa, demir şelat ekle
        if mikro_id is None:
            for gubre in gubreler:
                if "Demir" in gubre[1]:
                    temel_formul.append((gubre[0], gubre[1], 1.0))
                    break
        
        # Profil tipine göre miktarları ayarla
        # Örneğin domates için daha fazla K, marul için daha fazla N
        for besin, hedef in self.hedef_ppm.items():
            if besin == 'K' and hedef > 250:  # Yüksek K ihtiyacı (domates, biber gibi)
                for i, (gid, isim, miktar) in enumerate(temel_formul):
                    if potasyum_nitrat_id and gid == potasyum_nitrat_id:
                        temel_formul[i] = (gid, isim, miktar * 1.3)  # %30 daha fazla K
            
            elif besin == 'N' and hedef > 170:  # Yüksek N ihtiyacı
                for i, (gid, isim, miktar) in enumerate(temel_formul):
                    if kalsiyum_nitrat_id and gid == kalsiyum_nitrat_id:
                        temel_formul[i] = (gid, isim, miktar * 1.2)  # %20 daha fazla N
            
            elif besin == 'P' and hedef > 55:  # Yüksek P ihtiyacı
                for i, (gid, isim, miktar) in enumerate(temel_formul):
                    if mpf_id and gid == mpf_id:
                        temel_formul[i] = (gid, isim, miktar * 1.3)  # %30 daha fazla P
        
        # Son sonuç ppm değerlerini hesapla
        hesaplayici = BesinHesaplayici(self.hacim_litre)
        
        for gubre_id, _, miktar in temel_formul:
            hesaplayici.gubre_ekle(gubre_id, miktar)
        
        sonuc_ppm = hesaplayici.sonuc_hesapla(self.veritabani)
        
        return temel_formul, sonuc_ppm

def main():
    # Uygulama başlığı
    st.title("🌱 HydroBuddy Türkçe - Otomatik Formül")
    st.markdown("**Hidroponik Besin Çözeltisi Otomatik Hesaplayıcı**")
    
    # Veritabanı ve hesaplayıcı nesnelerini oluştur
    veritabani = Veritabani()
    
    # Session state ile hesaplayıcı ve formül verilerini kaydet
    if 'hesaplayici' not in st.session_state:
        st.session_state.hesaplayici = BesinHesaplayici()
    
    if 'eklenen_gubreler' not in st.session_state:
        st.session_state.eklenen_gubreler = []  # [(isim, id, miktar)]
    
    if 'otomatik_formul' not in st.session_state:
        st.session_state.otomatik_formul = []  # [(id, isim, miktar)]
    
    if 'otomatik_sonuc' not in st.session_state:
        st.session_state.otomatik_sonuc = {}
    
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
    
    # İki moda ayır: Manuel ve Otomatik
    tab1, tab2 = st.tabs(["Manuel Formül", "Otomatik Formül"])
    
    with tab1:
        # Manuel formül oluşturma ekranı
        st.header("Manuel Formül Oluşturma")
        
        # Gübre ekleme ve listeleme kısmını iki sütuna böl
        col1, col2 = st.columns([1, 1])
        
        # 1. Sütun: Gübre ekleme
        with col1:
            st.subheader("Gübre Ekle")
            
            # Gübre seçimi
            gubreler = veritabani.gubre_listesi_getir(sadece_turk=True)
            gubre_secenekler = [g[1] for g in gubreler]
            secili_gubre = st.selectbox("Gübre seçin:", gubre_secenekler, key="manuel_gubre")
            
            secili_index = gubre_secenekler.index(secili_gubre)
            secili_id = gubreler[secili_index][0]
            
            # Gübre miktarı
            miktar = st.number_input(
                "Miktar (gram):",
                min_value=0.1,
                max_value=1000.0,
                value=1.0,
                step=0.1,
                format="%.1f",
                key="manuel_miktar"
            )
            
            # Ekleme butonu
            if st.button("Gübre Ekle", key="manuel_ekle"):
                # Hesaplayıcıya ekle
                st.session_state.hesaplayici.gubre_ekle(secili_id, miktar)
                
                # Görüntüleme için listeye ekle
                st.session_state.eklenen_gubreler.append((secili_gubre, secili_id, miktar))
                
                st.success(f"{secili_gubre} ({miktar}g) eklendi!")
        
        # 2. Sütun: Eklenen gü
