import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import datetime
import logging

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sabitler
PDF_FONT_PATH = "DejaVuSansCondensed.ttf"
IYON_ESIK_DEGERI = 0.05  # mmol/L cinsinden eşik değeri
TANK_HACMI = 1000  # litre cinsinden varsayılan tank hacmi
KONSANTRASYON = 100  # Varsayılan konsantrasyon faktörü

# Hazır reçete şablonları
RECETE_SABLONLARI = {
    "Marul": {
        "NO3": 9.0, "H2PO4": 1.5, "SO4": 1.25, "NH4": 1.0,
        "K": 5.0, "Ca": 3.75, "Mg": 1.5,
        "Fe": 20.0, "Mn": 5.0, "B": 20.0, "Zn": 3.0, "Cu": 0.5, "Mo": 0.5
    },
    "Domates": {
        "NO3": 12.0, "H2PO4": 2.0, "SO4": 2.0, "NH4": 1.5,
        "K": 8.0, "Ca": 4.5, "Mg": 2.0,
        "Fe": 25.0, "Mn": 6.0, "B": 25.0, "Zn": 4.0, "Cu": 0.7, "Mo": 0.6
    }
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

# Tanımlı gübreler ve iyon katkıları
GUBRE_BILGILERI = {
    "Kalsiyum Nitrat": {"Ca": 1, "NO3": 2, "tank": "A", "molekul_agirligi": 236.15},
    "Potasyum Nitrat": {"K": 1, "NO3": 1, "tank": "A", "molekul_agirligi": 101.10},
    "Monopotasyum Fosfat": {"H2PO4": 1, "K": 1, "tank": "B", "molekul_agirligi": 136.09},
    "Magnezyum Sülfat": {"Mg": 1, "SO4": 1, "tank": "B", "molekul_agirligi": 120.37},
    "Monoamonyum Fosfat": {"H2PO4": 1, "NH4": 1, "tank": "B", "molekul_agirligi": 115.03}
}

# Mikro besin gübreleri
MIKRO_GUBRE_BILGILERI = {
    "Demir Şelat": {"Fe": 1, "molekul_agirligi": 344.05},
    "Manganez Sülfat": {"Mn": 1, "molekul_agirligi": 151.00},
    "Borik Asit": {"B": 1, "molekul_agirligi": 61.83},
    "Çinko Sülfat": {"Zn": 1, "molekul_agirligi": 161.47},
    "Bakır Sülfat": {"Cu": 1, "molekul_agirligi": 159.61},
    "Amonyum Molibdat": {"Mo": 1, "molekul_agirligi": 195.94}
}

# Anyon ve katyon yükleri
IYON_YUKLERI = {
    "NO3": -1, "H2PO4": -1, "SO4": -2,
    "NH4": 1, "K": 1, "Ca": 2, "Mg": 2
}

def kontrol_anyon_katyon_dengesi(recete):
    """Anyon ve katyon yük dengesini kontrol eder."""
    anyon_yuku = sum(recete[ion] * IYON_YUKLERI[ion] for ion in ["NO3", "H2PO4", "SO4"])
    katyon_yuku = sum(recete[ion] * IYON_YUKLERI[ion] for ion in ["NH4", "K", "Ca", "Mg"])
    return abs(anyon_yuku + katyon_yuku) < IYON_ESIK_DEGERI, anyon_yuku, katyon_yuku

def hesapla_gubre_miktarlari(recete, kuyu_suyu, tank_hacmi, konsantrasyon):
    """Gübre miktarlarını lineer denklem sistemi ile hesaplar."""
    makro_iyonlar = ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]
    mikro_iyonlar = ["Fe", "Mn", "B", "Zn", "Cu", "Mo"]

    # Net ihtiyacı hesapla
    net_ihtiyac = {
        ion: max(0, recete[ion] - kuyu_suyu.get(ion, 0))
        for ion in makro_iyonlar + mikro_iyonlar
    }

    # Makro gübre hesaplama
    a_tank_gubreler = {}
    b_tank_gubreler = {}
    log = []

    # Makro iyonlar için lineer denklem sistemi
    gubreler = list(GUBRE_BILGILERI.keys())
    katsayi_matrisi = np.zeros((len(makro_iyonlar), len(gubreler)))
    hedef_vektoru = np.array([net_ihtiyac[ion] for ion in makro_iyonlar])

    for j, gubre in enumerate(gubreler):
        for i, ion in enumerate(makro_iyonlar):
            katsayi_matrisi[i, j] = GUBRE_BILGILERI[gubre].get(ion, 0)

    # Lineer sistemi çöz
    try:
        gubre_miktarlari = np.linalg.lstsq(katsayi_matrisi, hedef_vektoru, rcond=None)[0]
        gubre_miktarlari = np.maximum(gubre_miktarlari, 0)  # Negatif miktarları sıfırla
    except np.linalg.LinAlgError:
        return None, None, None, "Lineer denklem sistemi çözülemedi. Gübre kombinasyonu uygun değil."

    # Tanklara ayır
    for gubre, miktar in zip(gubreler, gubre_miktarlari):
        if miktar > IYON_ESIK_DEGERI:
            tank = GUBRE_BILGILERI[gubre]["tank"]
            if tank == "A":
                a_tank_gubreler[gubre] = miktar
            else:
                b_tank_gubreler[gubre] = miktar

    # Gerçekleşen iyon miktarlarını hesapla
    gerceklesen_iyonlar = {ion: kuyu_suyu.get(ion, 0) for ion in makro_iyonlar}
    for gubre, miktar in a_tank_gubreler.items():
        for ion, katsayi in GUBRE_BILGILERI[gubre].items():
            if ion in makro_iyonlar:
                gerceklesen_iyonlar[ion] += miktar * katsayi
    for gubre, miktar in b_tank_gubreler.items():
        for ion, katsayi in GUBRE_BILGILERI[gubre].items():
            if ion in makro_iyonlar:
                gerceklesen_iyonlar[ion] += miktar * katsayi

    # Eksik ve fazla iyonları kontrol et
    eksik_iyonlar = {
        ion: recete[ion] - gerceklesen_iyonlar[ion]
        for ion in makro_iyonlar if recete[ion] - gerceklesen_iyonlar[ion] > IYON_ESIK_DEGERI
    }
    fazla_iyonlar = {
        ion: gerceklesen_iyonlar[ion] - recete[ion]
        for ion in makro_iyonlar if gerceklesen_iyonlar[ion] - recete[ion] > IYON_ESIK_DEGERI
    }

    if eksik_iyonlar or fazla_iyonlar:
        return None, None, None, f"Eksik iyonlar: {eksik_iyonlar}, Fazla iyonlar: {fazla_iyonlar}"

    # Tank gübre kütlelerini hesapla
    a_tank_sonuc = []
    a_tank_toplam = 0
    for gubre, miktar in a_tank_gubreler.items():
        molekul_agirligi = GUBRE_BILGILERI[gubre]["molekul_agirligi"]
        mg_L = miktar * molekul_agirligi
        kg_tank = mg_L * tank_hacmi * konsantrasyon / 1_000_000
        a_tank_sonuc.append([gubre, gubre, miktar, mg_L, kg_tank])
        a_tank_toplam += kg_tank

    b_tank_sonuc = []
    b_tank_toplam = 0
    for gubre, miktar in b_tank_gubreler.items():
        molekul_agirligi = GUBRE_BILGILERI[gubre]["molekul_agirligi"]
        mg_L = miktar * molekul_agirligi
        kg_tank = mg_L * tank_hacmi * konsantrasyon / 1_000_000
        b_tank_sonuc.append([gubre, gubre, miktar, mg_L, kg_tank])
        b_tank_toplam += kg_tank

    # Mikro besin hesaplama
    mikro_sonuc = []
    mikro_toplam = 0
    for ion in mikro_iyonlar:
        if net_ihtiyac[ion] > 0:
            gubre = [k for k, v in MIKRO_GUBRE_BILGILERI.items() if ion in v][0]
            miktar = net_ihtiyac[ion] / 1000  # mikro mol/L
            molekul_agirligi = MIKRO_GUBRE_BILGILERI[gubre]["molekul_agirligi"]
            mg_L = miktar * molekul_agirligi
            gram_tank = mg_L * tank_hacmi * konsantrasyon / 1_000
            mikro_sonuc.append([gubre, gubre, miktar * 1000, mg_L, gram_tank])
            mikro_toplam += gram_tank

    log.append({
        "adım": "Sonuç",
        "açıklama": "Makro ve mikro besinler hesaplandı",
        "ihtiyac": {k: round(v, 2) for k, v in gerceklesen_iyonlar.items()}
    })

    return (a_tank_sonuc, a_tank_toplam), (b_tank_sonuc, b_tank_toplam), mikro_sonuc, log

def create_pdf(recete, a_tank_sonuc, b_tank_sonuc, mikro_sonuc):
    """Hesaplama sonuçlarını PDF olarak oluşturur."""
    class PDF(FPDF):
        def header(self):
            self.set_font("DejaVu", "B", 12)
            self.cell(0, 10, "Hidroponik Gübre Hesaplama Raporu", 0, 1, "C")

        def footer(self):
            self.set_y(-15)
            self.set_font("DejaVu", "I", 8)
            self.cell(0, 10, f"Sayfa {self.page_no()}", 0, 0, "C")

    pdf = PDF()
    pdf.add_font("DejaVu", "", PDF_FONT_PATH, uni=True)
    pdf.add_font("DejaVu", "B", PDF_FONT_PATH, uni=True)
    pdf.add_page()
    pdf.set_font("DejaVu", "", 10)

    # Reçete
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(0, 10, "Reçete", 0, 1)
    pdf.set_font("DejaVu", "", 10)
    for ion, miktar in recete.items():
        iyon_adi = iyon_bilgileri[ion]["ad"] if ion in iyon_bilgileri else ion
        birim = "µmol/L" if ion in ["Fe", "Mn", "B", "Zn", "Cu", "Mo"] else "mmol/L"
        pdf.cell(0, 8, f"{ion} ({iyon_adi}): {miktar:.2f} {birim}", 0, 1)

    # A Tankı
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(0, 10, "A Tankı Gübreleri", 0, 1)
    pdf.set_font("DejaVu", "", 10)
    for gubre, _, miktar, mg_L, kg_tank in a_tank_sonuc or []:
        pdf.cell(0, 8, f"{gubre}: {miktar:.2f} mmol/L, {kg_tank:.3f} kg/tank", 0, 1)

    # B Tankı
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(0, 10, "B Tankı Gübreleri", 0, 1)
    pdf.set_font("DejaVu", "", 10)
    for gubre, _, miktar, mg_L, kg_tank in b_tank_sonuc or []:
        pdf.cell(0, 8, f"{gubre}: {miktar:.2f} mmol/L, {kg_tank:.3f} kg/tank", 0, 1)

    # Mikro Besinler
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(0, 10, "Mikro Besinler", 0, 1)
    pdf.set_font("DejaVu", "", 10)
    for gubre, _, miktar, mg_L, gram_tank in mikro_sonuc or []:
        pdf.cell(0, 8, f"{gubre}: {miktar:.2f} µmol/L, {gram_tank:.2f} g/tank", 0, 1)

    return pdf.output(dest="S").encode("latin1")

def main():
    st.set_page_config(page_title="Hidroponik Gübre Hesaplama", layout="wide")
    st.title("Hidroponik Gübre Hesaplama")

    # Session state başlatma
    if "recete" not in st.session_state:
        st.session_state.recete = {
            ion: 0.0 for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg", "Fe", "Mn", "B", "Zn", "Cu", "Mo"]
        }
    if "kuyu_suyu" not in st.session_state:
        st.session_state.kuyu_suyu = {ion: 0.0 for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]}
    if "tank_hacmi" not in st.session_state:
        st.session_state.tank_hacmi = TANK_HACMI
    if "konsantrasyon" not in st.session_state:
        st.session_state.konsantrasyon = KONSANTRASYON

    # Sekmeler
    tabs = st.tabs(["Reçete Oluşturma", "Sulama Suyu Analizi", "Gübre Hesaplama"])

    # Reçete Oluşturma
    with tabs[0]:
        st.header("Reçete Oluşturma")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Hazır Reçete Seç")
            secilen_recete = st.selectbox("Bitki seçin", ["Seçiniz"] + list(RECETE_SABLONLARI.keys()))
            if secilen_recete != "Seçiniz":
                st.session_state.recete = RECETE_SABLONLARI[secilen_recete].copy()
                st.success(f"{secilen_recete} reçetesi yüklendi.")

        with col2:
            st.subheader("Manuel Reçete Girişi")
            for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]:
                iyon_adi = iyon_bilgileri[ion]["ad"]
                st.session_state.recete[ion] = st.number_input(
                    f"{ion} ({iyon_adi}) (mmol/L)", min_value=0.0, max_value=50.0, value=float(st.session_state.recete[ion]), step=0.1, format="%.2f", key=f"recete_{ion}"
                )
            for ion in ["Fe", "Mn", "B", "Zn", "Cu", "Mo"]:
                iyon_adi = iyon_bilgileri[ion]["ad"]
                st.session_state.recete[ion] = st.number_input(
                    f"{ion} ({iyon_adi}) (µmol/L)", min_value=0.0, max_value=100.0, value=float(st.session_state.recete[ion]), step=0.1, format="%.2f", key=f"recete_{ion}"
                )

        # Anyon ve katyon dengesi kontrolü
        dengeli, anyon_yuku, katyon_yuku = kontrol_anyon_katyon_dengesi(st.session_state.recete)
        if not dengeli:
            st.error(
                f"Anyon ve katyon dengesi sağlanamadı!\n"
                f"Anyon yükü: {anyon_yuku:.2f}, Katyon yükü: {katyon_yuku:.2f}\n"
                f"Lütfen reçete değerlerini ayarlayarak dengeyi sağlayın."
            )
        else:
            st.success("✅ Anyon ve katyon dengesi sağlandı.")

    # Sulama Suyu Analizi
    with tabs[1]:
        st.header("Sulama Suyu Analizi")
        st.info("Ters osmos su varsayılır. Sulama suyu analiziniz varsa iyon değerlerini girin.")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Anyonlar")
            for ion in ["NO3", "H2PO4", "SO4"]:
                iyon_adi = iyon_bilgileri[ion]["ad"]
                st.session_state.kuyu_suyu[ion] = st.number_input(
                    f"{ion} ({iyon_adi}) (mmol/L)", min_value=0.0, max_value=10.0, value=float(st.session_state.kuyu_suyu[ion]), step=0.05, format="%.2f", key=f"kuyu_{ion}"
                )

        with col2:
            st.subheader("Katyonlar")
            for ion in ["NH4", "K", "Ca", "Mg"]:
                iyon_adi = iyon_bilgileri[ion]["ad"]
                st.session_state.kuyu_suyu[ion] = st.number_input(
                    f"{ion} ({iyon_adi}) (mmol/L)", min_value=0.0, max_value=10.0, value=float(st.session_state.kuyu_suyu[ion]), step=0.05, format="%.2f", key=f"kuyu_{ion}"
                )

        if any(st.session_state.kuyu_suyu.values()):
            st.success("✅ Sulama suyu değerleri kaydedildi ve hesaplamalarda dikkate alınacak.")
        else:
            st.info("ℹ️ Sulama suyu girilmemiş. Ters osmos su varsayılacak.")

    # Gübre Hesaplama
    with tabs[2]:
        st.header("Gübre Hesaplama")
        st.session_state.tank_hacmi = st.number_input(
            "Tank Hacmi (litre)", min_value=100.0, max_value=10000.0, value=float(st.session_state.tank_hacmi), step=100.0
        )
        st.session_state.konsantrasyon = st.number_input(
            "Konsantrasyon Faktörü", min_value=10.0, max_value=1000.0, value=float(st.session_state.konsantrasyon), step=10.0
        )

        if st.button("Gübre Hesapla", type="primary"):
            # Anyon ve katyon dengesi kontrolü
            dengeli, _, _ = kontrol_anyon_katyon_dengesi(st.session_state.recete)
            if not dengeli:
                st.error("Anyon ve katyon dengesi sağlanmadı. Lütfen reçete sekmesinde dengeyi sağlayın.")
            else:
                try:
                    (a_tank_sonuc, a_tank_toplam), (b_tank_sonuc, b_tank_toplam), mikro_sonuc, log = hesapla_gubre_miktarlari(
                        st.session_state.recete, st.session_state.kuyu_suyu, st.session_state.tank_hacmi, st.session_state.konsantrasyon
                    )

                    if isinstance(log, str):
                        st.error(f"Hesaplama hatası: {log}")
                    else:
                        # Sonuçları sakla
                        st.session_state.hesaplama_sonuclari = {
                            "a_tank_sonuc": a_tank_sonuc,
                            "b_tank_sonuc": b_tank_sonuc,
                            "mikro_sonuc": mikro_sonuc
                        }

                        # PDF oluştur
                        try:
                            pdf_bytes = create_pdf(st.session_state.recete, a_tank_sonuc, b_tank_sonuc, mikro_sonuc)
                            st.download_button(
                                label="📄 Hesaplama Sonuçlarını PDF Olarak İndir",
                                data=pdf_bytes,
                                file_name=f"hydrobuddy_rapor_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                mime="application/pdf"
                            )
                        except Exception as e:
                            logger.error(f"PDF oluşturma hatası: {str(e)}")
                            st.warning(f"PDF oluşturulurken hata: {str(e)}")

                        # Sonuçları göster
                        col_sonuc1, col_sonuc2 = st.columns(2)
                        with col_sonuc1:
                            st.subheader("A Tankı (Kalsiyum içeren)")
                            if a_tank_sonuc:
                                a_tank_df = pd.DataFrame(a_tank_sonuc, columns=["Gübre Adı", "Formül", "mmol/L", "mg/L", "kg/Tank"])
                                st.dataframe(a_tank_df.style.format({"mmol/L": "{:.2f}", "mg/L": "{:.2f}", "kg/Tank": "{:.3f}"}))
                                st.write(f"**Toplam A Tankı gübresi:** {a_tank_toplam:.3f} kg")
                            else:
                                st.info("A Tankı için gübre eklenmedi.")

                        with col_sonuc2:
                            st.subheader("B Tankı (Fosfat, Sülfat ve Amonyum)")
                            if b_tank_sonuc:
                                b_tank_df = pd.DataFrame(b_tank_sonuc, columns=["Gübre Adı", "Formül", "mmol/L", "mg/L", "kg/Tank"])
                                st.dataframe(b_tank_df.style.format({"mmol/L": "{:.2f}", "mg/L": "{:.2f}", "kg/Tank": "{:.3f}"}))
                                st.write(f"**Toplam B Tankı gübresi:** {b_tank_toplam:.3f} kg")
                            else:
                                st.info("B Tankı için gübre eklenmedi.")

                        # Mikro besinler
                        st.subheader("Mikro Besin Elementleri")
                        if mikro_sonuc:
                            mikro_df = pd.DataFrame(mikro_sonuc, columns=["Gübre Adı", "Formül", "µmol/L", "mg/L", "g/Tank"])
                            st.dataframe(mikro_df.style.format({"µmol/L": "{:.2f}", "mg/L": "{:.4f}", "g/Tank": "{:.2f}"}))
                            mikro_toplam = sum(sonuc[4] for sonuc in mikro_sonuc)
                            st.write(f"**Toplam mikro besin gübresi:** {mikro_toplam:.2f} gram")
                        else:
                            st.info("Mikro besin elementi eklenmedi.")

                        # Hesaplama adımları
                        with st.expander("Hesaplama Adımları"):
                            for entry in log:
                                st.write(f"**{entry['adım']}:** {entry['açıklama']}")
                                if entry["ihtiyac"]:
                                    ihtiyac_df = pd.DataFrame([[k, v] for k, v in entry["ihtiyac"].items()], columns=["İyon", "İhtiyaç (mmol/L)"])
                                    st.dataframe(ihtiyac_df.style.format({"İhtiyaç (mmol/L)": "{:.2f}"}))
                                st.markdown("---")

                        st.success("✅ Hesaplama tamamlandı. Çözelti dengeli!")

                except Exception as e:
                    logger.error(f"Hesaplama hatası: {str(e)}")
                    st.error(f"Hesaplama sırasında bir hata oluştu: {str(e)}")

if __name__ == "__main__":
    main()
