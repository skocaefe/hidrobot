import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Sayfa ayarları
st.set_page_config(
    page_title="HydroBuddy Türkçe",
    page_icon="🌱",
    layout="wide"
)

# Uygulama başlığı
st.title("🌱 HydroBuddy Türkçe")
st.markdown("**Hidroponik Besin Çözeltisi Hesaplayıcı**")

# Bitki profilleri sabit verisi
bitki_profilleri = {
    "Genel Amaçlı": {"N": 150, "P": 50, "K": 210, "Ca": 200, "Mg": 50, "S": 65, "Fe": 3, "Mn": 0.5, "Zn": 0.15, "B": 0.5, "Cu": 0.15, "Mo": 0.1},
    "Domates": {"N": 180, "P": 45, "K": 300, "Ca": 190, "Mg": 50, "S": 70, "Fe": 4, "Mn": 0.8, "Zn": 0.3, "B": 0.7, "Cu": 0.15, "Mo": 0.1},
    "Salatalık": {"N": 160, "P": 60, "K": 230, "Ca": 170, "Mg": 45, "S": 60, "Fe": 3, "Mn": 0.5, "Zn": 0.2, "B": 0.5, "Cu": 0.1, "Mo": 0.05},
    "Marul": {"N": 120, "P": 40, "K": 180, "Ca": 150, "Mg": 40, "S": 50, "Fe": 2.5, "Mn": 0.4, "Zn": 0.1, "B": 0.4, "Cu": 0.1, "Mo": 0.05},
    "Çilek": {"N": 140, "P": 55, "K": 220, "Ca": 180, "Mg": 45, "S": 55, "Fe": 3.5, "Mn": 0.6, "Zn": 0.25, "B": 0.6, "Cu": 0.12, "Mo": 0.08}
}

# Gübre verileri sabit olarak tanımlanır
gubreler = {
    "Kalsiyum Nitrat": {"N_nitrat": 14.4, "N_amonyum": 1.1, "P": 0, "K": 0, "Ca": 19, "Mg": 0, "S": 0, "Fe": 0, "Mn": 0, "Zn": 0, "B": 0, "Cu": 0, "Mo": 0},
    "Potasyum Nitrat": {"N_nitrat": 13, "N_amonyum": 0, "P": 0, "K": 38, "Ca": 0, "Mg": 0, "S": 0, "Fe": 0, "Mn": 0, "Zn": 0, "B": 0, "Cu": 0, "Mo": 0},
    "Magnezyum Sülfat": {"N_nitrat": 0, "N_amonyum": 0, "P": 0, "K": 0, "Ca": 0, "Mg": 9.9, "S": 13, "Fe": 0, "Mn": 0, "Zn": 0, "B": 0, "Cu": 0, "Mo": 0},
    "Mono Potasyum Fosfat": {"N_nitrat": 0, "N_amonyum": 0, "P": 22.3, "K": 28.2, "Ca": 0, "Mg": 0, "S": 0, "Fe": 0, "Mn": 0, "Zn": 0, "B": 0, "Cu": 0, "Mo": 0},
    "Demir Şelat (EDTA)": {"N_nitrat": 0, "N_amonyum": 0, "P": 0, "K": 0, "Ca": 0, "Mg": 0, "S": 0, "Fe": 13, "Mn": 0, "Zn": 0, "B": 0, "Cu": 0, "Mo": 0},
    "Mikro Element Karışımı": {"N_nitrat": 0, "N_amonyum": 0, "P": 0, "K": 0, "Ca": 0, "Mg": 0, "S": 0, "Fe": 7, "Mn": 2, "Zn": 0.4, "B": 1.5, "Cu": 0.1, "Mo": 0.06}
}

# Oturum durumu (session state) başlatma
if 'hedef_ppm' not in st.session_state:
    st.session_state.hedef_ppm = bitki_profilleri["Genel Amaçlı"].copy()

if 'eklenen_gubreler' not in st.session_state:
    st.session_state.eklenen_gubreler = []  # [(isim, miktar), ...]

if 'hacim_litre' not in st.session_state:
    st.session_state.hacim_litre = 20

if 'otomatik_formul' not in st.session_state:
    st.session_state.otomatik_formul = []

# Sidebar: Bitki profili ve hacim ayarları
with st.sidebar:
    st.header("Ayarlar")
    
    # Bitki profili seçimi
    st.subheader("Bitki Profili")
    
    secili_profil = st.selectbox("Profil seçin:", list(bitki_profilleri.keys()))
    
    if st.button("Profili Yükle"):
        st.session_state.hedef_ppm = bitki_profilleri[secili_profil].copy()
        st.success(f"{secili_profil} profili yüklendi!")
    
    # Hacim ayarı
    st.subheader("Su Hacmi")
    
    yeni_hacim = st.number_input(
        "Çözelti hacmi (litre):",
        min_value=1,
        max_value=1000,
        value=st.session_state.hacim_litre
    )
    
    if st.button("Hacmi Güncelle"):
        st.session_state.hacim_litre = yeni_hacim
        st.success(f"Hacim {yeni_hacim} litre olarak güncellendi!")

# İki moda ayır: Manuel ve Otomatik
tab1, tab2 = st.tabs(["Manuel Formül", "Otomatik Formül"])

# Manuel Formül Sekmesi
with tab1:
    # Manuel formül oluşturma ekranı
    st.header("Manuel Formül Oluşturma")
    
    # Gübre ekleme ve listeleme kısmını iki sütuna böl
    col1, col2 = st.columns([1, 1])
    
    # 1. Sütun: Gübre ekleme
    with col1:
        st.subheader("Gübre Ekle")
        
        # Gübre seçimi
        secili_gubre = st.selectbox("Gübre seçin:", list(gubreler.keys()), key="manuel_gubre")
        
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
            st.session_state.eklenen_gubreler.append((secili_gubre, miktar))
            st.success(f"{secili_gubre} ({miktar}g) eklendi!")
    
    # 2. Sütun: Eklenen gübreler
    with col2:
        st.subheader("Eklenen Gübreler")
        
        if not st.session_state.eklenen_gubreler:
            st.info("Henüz gübre eklenmedi.")
        else:
            # Gübre listesini tablo olarak göster
            gubre_df = pd.DataFrame(
                [(i+1, g[0], g[1]) for i, g in enumerate(st.session_state.eklenen_gubreler)],
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
                silinen = st.session_state.eklenen_gubreler.pop(indeks)
                st.warning(f"{silinen[0]} silindi!")
        
        # Tümünü temizle
        if st.button("Tüm Gübreleri Temizle"):
            st.session_state.eklenen_gubreler = []
            st.warning("Tüm gübreler temizlendi!")
    
    # Besin sonuçlarını hesaplama fonksiyonu
    def sonuc_hesapla(eklenen_gubreler, hacim_litre):
        sonuc = {
            'N': 0, 'P': 0, 'K': 0, 'Ca': 0, 'Mg': 0, 'S': 0,
            'Fe': 0, 'Mn': 0, 'Zn': 0, 'B': 0, 'Cu': 0, 'Mo': 0
        }
        
        for gubre_adi, miktar_gram in eklenen_gubreler:
            gubre_info = gubreler[gubre_adi]
            
            # N (nitrat + amonyum)
            sonuc['N'] += (gubre_info['N_nitrat'] + gubre_info['N_amonyum']) * miktar_gram / hacim_litre
            # P
            sonuc['P'] += gubre_info['P'] * miktar_gram / hacim_litre
            # K
            sonuc['K'] += gubre_info['K'] * miktar_gram / hacim_litre
            # Ca
            sonuc['Ca'] += gubre_info['Ca'] * miktar_gram / hacim_litre
            # Mg
            sonuc['Mg'] += gubre_info['Mg'] * miktar_gram / hacim_litre
            # S
            sonuc['S'] += gubre_info['S'] * miktar_gram / hacim_litre
            # Fe
            sonuc['Fe'] += gubre_info['Fe'] * miktar_gram / hacim_litre
            # Mn
            sonuc['Mn'] += gubre_info['Mn'] * miktar_gram / hacim_litre
            # Zn
            sonuc['Zn'] += gubre_info['Zn'] * miktar_gram / hacim_litre
            # B
            sonuc['B'] += gubre_info['B'] * miktar_gram / hacim_litre
            # Cu
            sonuc['Cu'] += gubre_info['Cu'] * miktar_gram / hacim_litre
            # Mo
            sonuc['Mo'] += gubre_info['Mo'] * miktar_gram / hacim_litre
        
        return sonuc
    
    # Hesaplama butonu
    if st.button("HESAPLA", key="manuel_hesapla"):
        if not st.session_state.eklenen_gubreler:
            st.error("Lütfen önce gübre ekleyin.")
        else:
            # Sonuçları hesapla
            sonuclar = sonuc_hesapla(st.session_state.eklenen_gubreler, st.session_state.hacim_litre)
            hedefler = st.session_state.hedef_ppm
            
            # Sonuçları göster
            st.subheader("Sonuçlar")
            
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
            
            # Grafik gösterimi
            st.subheader("Grafik")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            makrolar = ['N', 'P', 'K', 'Ca', 'Mg', 'S']
            hedef_degerler = [hedefler[b] for b in makrolar]
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
            
            st.pyplot(fig)

# Otomatik Formül Sekmesi
with tab2:
    st.header("Otomatik Formül Oluşturma")
    
    st.write("""
    Bu özellik, seçilen bitki profiline göre otomatik olarak optimum gübre formülü oluşturur.
    Profili seçtikten sonra "Otomatik Formül Oluştur" butonuna tıklayın.
    """)
    
    if st.button("Otomatik Formül Oluştur"):
        # Bitki profiline göre basit bir formül oluştur
        otomatik_formul = []
        
        # Seçilen profilin ihtiyaçlarına göre gübre formülü belirle
        hedefler = st.session_state.hedef_ppm
        
        # 1. Temel formül bileşenleri
        otomatik_formul.append(("Kalsiyum Nitrat", 10.0))  # N ve Ca kaynağı
        otomatik_formul.append(("Mono Potasyum Fosfat", 2.0))  # P ve K kaynağı
        otomatik_formul.append(("Potasyum Nitrat", 5.0))  # K ve N kaynağı
        otomatik_formul.append(("Magnezyum Sülfat", 5.0))  # Mg ve S kaynağı
        otomatik_formul.append(("Mikro Element Karışımı", 2.0))  # Mikro besinler
        
        # 2. Profil tipine göre ayarlamalar
        # Domates/Biber (yüksek K ihtiyacı)
        if hedefler['K'] > 250:
            otomatik_formul = [(g, m * 1.3 if g == "Potasyum Nitrat" else m) for g, m in otomatik_formul]
        
        # Yapraklı (yüksek N ihtiyacı)
        if hedefler['N'] > 170:
            otomatik_formul = [(g, m * 1.2 if g == "Kalsiyum Nitrat" else m) for g, m in otomatik_formul]
        
        # Fide veya çiçekli (yüksek P ihtiyacı)
        if hedefler['P'] > 55:
            otomatik_formul = [(g, m * 1.3 if g == "Mono Potasyum Fosfat" else m) for g, m in otomatik_formul]
        
        # Formülü session state'e kaydet
        st.session_state.otomatik_formul = otomatik_formul
        
        # Sonuçları hesapla
        sonuclar = sonuc_hesapla(otomatik_formul, st.session_state.hacim_litre)
        hedefler = st.session_state.hedef_ppm
        
        # Formülü göster
        st.subheader("Önerilen Formül")
        
        formul_df = pd.DataFrame(
            [(i+1, g[0], f"{g[1]:.1f}") for i, g in enumerate(otomatik_formul)],
            columns=["#", "Gübre Adı", "Miktar (g)"]
        )
        st.table(formul_df)
        
        # Sonuçları göster
        st.subheader("Beklenen Sonuçlar")
        
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
        
        # Grafik gösterimi
        st.subheader("Grafik")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        makrolar = ['N', 'P', 'K', 'Ca', 'Mg', 'S']
        hedef_degerler = [hedefler[b] for b in makrolar]
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
        
        st.pyplot(fig)
        
        # Formül iyileştirme önerileri
        st.subheader("Formül İyileştirme Önerileri")
        
        # Hedef ve sonuç değerlerini karşılaştır ve öneriler sun
        oneriler = []
        for besin in ['N', 'P', 'K', 'Ca', 'Mg', 'S', 'Fe', 'Mn', 'Zn', 'B', 'Cu', 'Mo']:
            hedef = hedefler[besin]
            sonuc = sonuclar[besin]
            
            if sonuc < hedef * 0.8:
                if besin == 'N':
                    oneriler.append(f"🔹 N seviyesi düşük. Kalsiyum Nitrat veya Potasyum Nitrat miktarını artırın.")
                elif besin == 'P':
                    oneriler.append(f"🔹 P seviyesi düşük. Mono Potasyum Fosfat miktarını artırın.")
                elif besin == 'K':
                    oneriler.append(f"🔹 K seviyesi düşük. Potasyum Nitrat miktarını artırın.")
                elif besin == 'Ca':
                    oneriler.append(f"🔹 Ca seviyesi düşük. Kalsiyum Nitrat miktarını artırın.")
                elif besin == 'Mg':
                    oneriler.append(f"🔹 Mg seviyesi düşük. Magnezyum Sülfat miktarını artırın.")
                elif besin in ['Fe', 'Mn', 'Zn', 'B', 'Cu', 'Mo']:
                    oneriler.append(f"🔹 {besin} seviyesi düşük. Mikro Element Karışımı miktarını artırın.")
            
            elif sonuc > hedef * 1.2:
                if besin == 'N':
                    oneriler.append(f"🔹 N seviyesi yüksek. Kalsiyum Nitrat veya Potasyum Nitrat miktarını azaltın.")
                elif besin == 'P':
                    oneriler.append(f"🔹 P seviyesi yüksek. Mono Potasyum Fosfat miktarını azaltın.")
                elif besin == 'K':
                    oneriler.append(f"🔹 K seviyesi yüksek. Potasyum Nitrat miktarını azaltın.")
                elif besin == 'Ca':
                    oneriler.append(f"🔹 Ca seviyesi yüksek. Kalsiyum Nitrat miktarını azaltın.")
                elif besin == 'Mg':
                    oneriler.append(f"🔹 Mg seviyesi yüksek. Magnezyum Sülfat miktarını azaltın.")
                elif besin in ['Fe', 'Mn', 'Zn', 'B', 'Cu', 'Mo']:
                    oneriler.append(f"🔹 {besin} seviyesi yüksek. Mikro Element Karışımı miktarını azaltın.")
        
        if oneriler:
            for oneri in oneriler:
                st.write(oneri)
        else:
            st.success("✅ Formül oldukça dengeli görünüyor. İyileştirme önerisi bulunmuyor.")
        
        # Manuel formüle aktarma seçeneği
        if st.button("Bu Formülü Manuel Formüle Aktar"):
            st.session_state.eklenen_gubreler = otomatik_formul.copy()
            st.success("Formül manuel formüle aktarıldı. 'Manuel Formül' sekmesine geçerek düzenleyebilirsiniz.")

# Alt bilgi
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 10px;">
    <p>HydroBuddy Türkçe Versiyonu</p>
    <p>Orijinal: <a href="https://github.com/danielfppps/hydrobuddy">Daniel Fernandez</a> • Türkçe uyarlama: [Sizin Adınız]</p>
</div>
""", unsafe_allow_html=True)
