# -*- coding: utf-8 -*-
# HydroBuddy Türkçe Streamlit Versiyonu - Otomatik Formül Oluşturucu
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
from scipy.optimize import minimize

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

class OtomatikFormulOlusturucu:
    def __init__(self, veritabani, hedef_ppm, hacim_litre=20):
        self.veritabani = veritabani
        self.hedef_ppm = hedef_ppm
        self.hacim_litre = hacim_litre
        
    def formul_olustur(self, max_gubre_sayisi=6, min_miktar=0.1, max_miktar=50):
        """
        Otomatik formül oluşturur.
        
        Args:
            max_gubre_sayisi: Maksimum kullanılacak gübre sayısı
            min_miktar: Minimum gübre miktarı (gram)
            max_miktar: Maksimum gübre miktarı (gram)
            
        Returns:
            (secilen_gubreler, sonuc_ppm) tuple
            secilen_gubreler: [(gubre_id, gubre_ismi, miktar), ...]
            sonuc_ppm: {'N': değer, 'P': değer, ...}
        """
        # Tüm gübreleri al
        gubreler = self.veritabani.tum_gubre_bilgilerini_getir(sadece_turk=True)
        
        # Makro besinler ve mikro besinler için ayrı formül oluştur
        # 1. Makro besinler (N, P, K, Ca, Mg, S)
        makro_besinler = ['N', 'P', 'K', 'Ca', 'Mg', 'S']
        makro_hedefler = [self.hedef_ppm[b] for b in makro_besinler]
        
        # 2. Mikro besinler (Fe, Mn, Zn, B, Cu, Mo)
        mikro_besinler = ['Fe', 'Mn', 'Zn', 'B', 'Cu', 'Mo']
        mikro_hedefler = [self.hedef_ppm[b] for b in mikro_besinler]
        
        # Gübre verileri matris ve vektörlere dönüştür
        makro_matris = []
        mikro_matris = []
        gubre_isimleri = []
        gubre_idleri = []
        
        for gubre in gubreler:
            gubre_id = gubre[0]
            gubre_ismi = gubre[1]
            
            # Gübre içeriği (makro besinler)
            n_nitrat = gubre[2]
            n_amonyum = gubre[3]
            p = gubre[4]
            k = gubre[5]
            ca = gubre[6]
            mg = gubre[7]
            s = gubre[8]
            
            # Gübre içeriği (mikro besinler)
            fe = gubre[9]
            mn = gubre[10]
            zn = gubre[11]
            b = gubre[12]
            cu = gubre[13]
            mo = gubre[14]
            
            # Gübre bilgilerini matrise ekle
            makro_matris.append([n_nitrat + n_amonyum, p, k, ca, mg, s])
            mikro_matris.append([fe, mn, zn, b, cu, mo])
            gubre_isimleri.append(gubre_ismi)
            gubre_idleri.append(gubre_id)
        
        # Numpy dizilerine dönüştür
        makro_matris = np.array(makro_matris)
        mikro_matris = np.array(mikro_matris)
        makro_hedefler = np.array(makro_hedefler)
        mikro_hedefler = np.array(mikro_hedefler)
        
        # Gübre sayısına göre en iyi kombinasyonları bul
        en_iyi_kombinasyon = None
        en_iyi_hata = float('inf')
        
        # Bütün gübrelerden max_gubre_sayisi kadar gübre seç
        # ve en iyi kombinasyonu bul
        
        # Basitleştirilmiş yaklaşım: En önemli makro besin sağlayıcıları seç
        
        # 1. N için en iyi gübreler
        n_indeksleri = np.argsort(-makro_matris[:, 0])[:2]  # En yüksek N içeren 2 gübre
        
        # 2. P için en iyi gübreler
        p_indeksleri = np.argsort(-makro_matris[:, 1])[:2]  # En yüksek P içeren 2 gübre
        
        # 3. K için en iyi gübreler
        k_indeksleri = np.argsort(-makro_matris[:, 2])[:2]  # En yüksek K içeren 2 gübre
        
        # 4. Ca için en iyi gübreler
        ca_indeksleri = np.argsort(-makro_matris[:, 3])[:2]  # En yüksek Ca içeren 2 gübre
        
        # 5. Mg için en iyi gübreler
        mg_indeksleri = np.argsort(-makro_matris[:, 4])[:2]  # En yüksek Mg içeren 2 gübre
        
        # 6. Mikro element karışımı
        mikro_indeksleri = np.where(mikro_matris[:, 0] > 0)[0]  # Fe içeren gübreler
        
        # En iyi indeksleri birleştir ve tekrarları kaldır
        secilen_indeksler = list(set(list(n_indeksleri) + list(p_indeksleri) + list(k_indeksleri) + 
                                   list(ca_indeksleri) + list(mg_indeksleri) + list(mikro_indeksleri)))
        
        # Maksimum gübre sayısını sınırla
        if len(secilen_indeksler) > max_gubre_sayisi:
            # En önemli gübreleri tut
            secilen_indeksler = secilen_indeksler[:max_gubre_sayisi]
        
        # Seçilen gübrelerden alt matrisler oluştur
        secilen_makro_matris = makro_matris[secilen_indeksler]
        secilen_mikro_matris = mikro_matris[secilen_indeksler]
        secilen_gubre_isimleri = [gubre_isimleri[i] for i in secilen_indeksler]
        secilen_gubre_idleri = [gubre_idleri[i] for i in secilen_indeksler]
        
        # Optimizasyon problemi tanımla
        def hedef_fonksiyon(miktarlar):
            # Makro besin farkları
            makro_sonuc = np.dot(secilen_makro_matris.T, miktarlar) / self.hacim_litre
            makro_fark = (makro_sonuc - makro_hedefler) / makro_hedefler
            
            # Mikro besin farkları
            mikro_sonuc = np.dot(secilen_mikro_matris.T, miktarlar) / self.hacim_litre
            # Mikro besinlerde sıfıra bölme hatasını önle
            mikro_fark = np.zeros_like(mikro_hedefler)
            for i, hedef in enumerate(mikro_hedefler):
                if hedef > 0:
                    mikro_fark[i] = (mikro_sonuc[i] - hedef) / hedef
                else:
                    mikro_fark[i] = mikro_sonuc[i]  # Hedef sıfırsa, sonucu al
            
            # Toplam hata
            # Makro besinlere daha fazla ağırlık ver
            toplam_hata = np.sum(makro_fark**2) * 3 + np.sum(mikro_fark**2)
            
            return toplam_hata
        
        # Başlangıç değerleri (eşit miktarda)
        baslangic = np.ones(len(secilen_indeksler)) * 10
        
        # Sınırlar (her gübre için min_miktar ile max_miktar arası)
        sinirlar = [(min_miktar, max_miktar) for _ in range(len(secilen_indeksler))]
        
        # Optimizasyon
        sonuc = minimize(hedef_fonksiyon, baslangic, bounds=sinirlar, method='L-BFGS-B')
        
        # Optimum miktarlar
        optimum_miktarlar = sonuc.x
        
        # Sonuç formülü oluştur
        formul = []
        for i, miktar in enumerate(optimum_miktarlar):
            formul.append((secilen_gubre_idleri[i], secilen_gubre_isimleri[i], miktar))
        
        # Son sonuç ppm değerlerini hesapla
        hesaplayici = BesinHesaplayici(self.hacim_litre)
        
        for gubre_id, _, miktar in formul:
            hesaplayici.gubre_ekle(gubre_id, miktar)
        
        sonuc_ppm = hesaplayici.sonuc_hesapla(self.veritabani)
        
        return formul, sonuc_ppm

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
                st.success(f"{secili_profil} profili y
