import streamlit as st
import pandas as pd
import datetime
import logging
from fpdf import FPDF
from io import BytesIO

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

# Negatif ihtiyaçları sıfırla ve fazla besinleri kaydet
negatif_ihtiyaclar = {iyon: miktar for iyon, miktar in net_ihtiyac.items() if miktar < -IYON_ESIK_DEGERI}
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

# PDF indirme butonu
st.download_button(
label="📄 Hesaplama Sonuçlarını PDF Olarak İndir",
data=pdf_bytes,
file_name=f"hydrobuddy_rapor_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
mime="application/pdf"
)
except Exception as e:
logger.error(f"PDF oluşturma hatası: {str(e)}")
st.warning(f"PDF oluşturulurken hata: {str(e)}\nPDF indirme özelliği için fpdf kütüphanesi ve DejaVuSansCondensed.ttf fontu gereklidir.")

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
mikro_toplam = sum(sonuc[4] for sonuc in mikro_sonuc)
st.write(f"**Toplam mikro besin gübresi:** {mikro_toplam:.2f} gram")
else:
st.info("Mikro besin elementi eklenmedi.")
st.warning("""
**Mikro besin hesaplanmama nedenleri:**
1. Mikro besin için uygun kaynak seçilmemiş olabilir.
2. Reçetede mikro besin değeri 0 olabilir.
3. Seçilen mikro besin elementlerinden bazılarının değerleri düşük olabilir.

Mikro besinler (Fe, Mn, B, Zn, Cu, Mo) için 'Gübre Seçimi' sekmesinden kaynak seçtiğinizden ve 
'Reçete Oluşturma' sekmesinde mikro besin değerlerinin sıfırdan büyük olduğundan emin olun.
""")

# Kuyu suyu uyarısı
if any(st.session_state.kuyu_suyu.values()):
st.success("✅ Kuyu suyu analiziniz hesaplamada dikkate alındı.")

# Eksik ve fazla besin değerlendirmesi
st.subheader("Besin Dengesi Değerlendirmesi")

# Eksik iyonlar
if eksik_iyonlar:
st.error("⚠️ **Eksik İyonlar ve Olası Etkileri**")
for iyon, miktar in eksik_iyonlar.items():
col1, col2 = st.columns([1, 3])
with col1:
iyon_adi = iyon_bilgileri[iyon]["ad"] if iyon in iyon_bilgileri else iyon
st.markdown(f"**{iyon} ({iyon_adi}):**")
st.markdown(f"{miktar:.2f} mmol/L eksik")
with col2:
if iyon in iyon_bilgileri:
st.markdown(f"**Olası etkiler:** {iyon_bilgileri[iyon]['eksik']}")

# Gübre önerileri
if oneriler:
st.warning("**Önerilen Gübreler:**")
for iyon, gubre_listesi in oneriler.items():
iyon_adi = iyon_bilgileri[iyon]["ad"] if iyon in iyon_bilgileri else iyon
st.markdown(f"**{iyon} ({iyon_adi}) için:**")
for gubre in gubre_listesi:
st.markdown(f"• {gubre}")

# Fazla iyonlar
if fazla_iyonlar:
st.warning("⚠️ **Fazla İyonlar ve Olası Etkileri**")
for iyon, miktar in fazla_iyonlar.items():
col1, col2 = st.columns([1, 3])
with col1:
iyon_adi = iyon_bilgileri[iyon]["ad"] if iyon in iyon_bilgileri else iyon
st.markdown(f"**{iyon} ({iyon_adi}):**")
st.markdown(f"{miktar:.2f} mmol/L fazla")
with col2:
if iyon in iyon_bilgileri:
st.markdown(f"**Olası etkiler:** {iyon_bilgileri[iyon]['fazla']}")

if not eksik_iyonlar and not fazla_iyonlar:
st.success("✅ Seçilen gübrelerle tüm besinler ideal olarak karşılandı.")

# Hesaplama adımları
with st.expander("Hesaplama Adımları"):
for log in st.session_state.hesaplama_log:
st.write(f"**{log['adım']}:** {log['açıklama']}")
if log["ihtiyac"]:
ihtiyac_df = pd.DataFrame([[k, v] for k, v in log["ihtiyac"].items()], columns=["İyon", "İhtiyaç (mmol/L)"])
st.dataframe(ihtiyac_df.style.format({"İhtiyaç (mmol/L)": "{:.2f}"}))
st.markdown("---")

except Exception as e:
logger.error(f"Hesaplama hatası: {str(e)}")
st.error(f"Hesaplama sırasında bir hata oluştu: {str(e)}")
st.info("Lütfen girdileri kontrol edip tekrar deneyin veya hatayı raporlayın.")

# Alt bilgi
st.markdown("---")
st.markdown("HydroBuddy Türkçe | Hidroponik besin çözeltisi hesaplama aracı")# Tab 4: Gübre Hesaplama
with tabs[3]:
st.header("Gübre Hesaplama")

if st.button("Gübre Hesapla", type="primary"):
secilen_gubreler = st.session_state.secilen_gubreler

if not secilen_gubreler:
st.error("Lütfen 'Gübre Seçimi' sekmesinden en az bir makro gübre seçin!")
else:
try:
# Net ihtiyaç hesaplama (kuyu suyu değerlerini çıkararak)
net_ihtiyac = {
ion: max(0, float(st.session_state.recete[ion]) - float(st.session_state.kuyu_suyu[ion]))
for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]
}

# Hesaplama logunu başlat
st.session_state.hesaplama_log = []
st.session_state.hesaplama_log.append({
"adım": "Başlangıç", 
"açıklama": f"Kuyu suyu sonrası ihtiyaçlar",
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

# 3.            if gubre not in gubreler:
logger.warning(f"{gubre_tipi} Tankı - '{gubre}' gübresi tanımlı değil")
continue

formul = gubreler[gubre]["formul"]
agirlik = float(gubreler[gubre]["agirlik"])
mg_l = float(mmol) * agirlik
g_tank = (mg_l * float(konsantrasyon) * float(tank_hacmi)) / 1000
kg_tank = g_tank / 1000
toplam_agirlik += g_tank
sonuclar.append([gubre, formul, mmol, mg_l, kg_tank])

logger.info(f"{gubre_tipi} Tankı - {gubre}: {mmol:.2f} mmol/L, {kg_tank:.3f} kg")
except Exception as e:
hata_mesaji = f"{gubre_tipi} Tankı gübresi '{gubre}' hesaplanırken hata: {str(e)}"
logger.error(hata_mesaji)
st.error(hata_mesaji)

return sonuclar, toplam_agirlik

def create_pdf(recete, a_tank_sonuc, b_tank_sonuc, mikro_sonuc, eksik_iyonlar, fazla_iyonlar, oneriler):
"""Hesaplama sonuçlarını PDF formatında oluşturur.

Args:
recete (dict): Reçete değerleri
a_tank_sonuc (list): A tankı gübre sonuçları
b_tank_sonuc (list): B tankı gübre sonuçları
mikro_sonuc (list): Mikro besin sonuçları
eksik_iyonlar (dict): Eksik iyonlar ve miktarları
fazla_iyonlar (dict): Fazla iyonlar ve miktarları
oneriler (dict): Gübre önerileri

Returns:
bytes: PDF dosyasının binary içeriği
"""
try:
pdf = FPDF()
pdf.add_page()

# Unicode Türkçe karakter desteği için font
try:
pdf.add_font('DejaVu', '', PDF_FONT_PATH, uni=True)
pdf.set_font('DejaVu', '', 11)
except Exception as e:
logger.warning(f"DejaVu fontu yüklenemedi: {str(e)}. Varsayılan font kullanılıyor.")
pdf.set_font('Arial', '', 11)

# Başlık
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 16)
pdf.cell(0, 10, 'HydroBuddy Turkce - Hidroponik Besin Hesaplamasi', 0, 1, 'C')
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 12)
pdf.cell(0, 10, f'Olusturulma Tarihi: {datetime.datetime.now().strftime("%d.%m.%Y %H:%M")}', 0, 1, 'C')
pdf.ln(5)

# Reçete bilgisi
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 14)
pdf.cell(0, 10, 'Recete Degerleri', 0, 1, 'L')
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 11)

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
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 14)
pdf.cell(0, 10, 'Mikro Besinler (mikromol/L)', 0, 1, 'L')
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 11)

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
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 14)
pdf.cell(0, 10, 'A Tanki Gubreleri', 0, 1, 'L')
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 11)

if a_tank_sonuc:
pdf.cell(60, 7, 'Gubre', 1, 0, 'C')
pdf.cell(35, 7, 'Formul', 1, 0, 'C')
pdf.cell(30, 7, 'mmol/L', 1, 0, 'C')
pdf.cell(30, 7, 'kg/Tank', 1, 1, 'C')

for row in a_tank_sonuc:
pdf.cell(60, 7, row[0], 1, 0, 'L')
pdf.cell(35, 7, row[1], 1, 0, 'L')
pdf.cell(30, 7, f"{row[2]:.2f}", 1, 0, 'R')
pdf.cell(30, 7, f"{row[4]:.3f}", 1, 1, 'R')
else:
pdf.cell(0, 7, 'A Tanki icin gubre eklenmedi.', 1, 1, 'L')

pdf.ln(5)
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 14)
pdf.cell(0, 10, 'B Tanki Gubreleri', 0, 1, 'L')
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 11)

if b_tank_sonuc:
pdf.cell(60, 7, 'Gubre', 1, 0, 'C')
pdf.cell(35, 7, 'Formul', 1, 0, 'C')
pdf.cell(30, 7, 'mmol/L', 1, 0, 'C')
pdf.cell(30, 7, 'kg/Tank', 1, 1, 'C')

for row in b_tank_sonuc:
pdf.cell(60, 7, row[0], 1, 0, 'L')
pdf.cell(35, 7, row[1], 1, 0, 'L')
pdf.cell(30, 7, f"{row[2]:.2f}", 1, 0, 'R')
pdf.cell(30, 7, f"{row[4]:.3f}", 1, 1, 'R')
else:
pdf.cell(0, 7, 'B Tanki icin gubre eklenmedi.', 1, 1, 'L')

pdf.ln(5)
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 14)
pdf.cell(0, 10, 'Mikro Besin Elementleri', 0, 1, 'L')
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 11)

if mikro_sonuc:
pdf.cell(60, 7, 'Gubre', 1, 0, 'C')
pdf.cell(35, 7, 'Formul', 1, 0, 'C')
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
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 14)
pdf.cell(0, 10, 'Eksik Iyonlar ve Olasi Etkileri', 0, 1, 'L')
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 11)

for iyon, miktar in eksik_iyonlar.items():
iyon_adi = iyon_bilgileri[iyon]["ad"] if iyon in iyon_bilgileri else iyon
pdf.multi_cell(0, 7, f"{iyon} ({iyon_adi}) - {miktar:.2f} mmol/L eksik", 0, 'L')

if iyon in iyon_bilgileri:
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 10)
pdf.multi_cell(0, 6, f"Olasi etkiler: {iyon_bilgileri[iyon]['eksik']}", 0, 'L')
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 11)
pdf.ln(2)

# Fazla iyonlar
if fazla_iyonlar:
pdf.ln(5)
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 14)
pdf.cell(0, 10, 'Fazla Iyonlar ve Olasi Etkileri', 0, 1, 'L')
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 11)

for iyon, miktar in fazla_iyonlar.items():
iyon_adi = iyon_bilgileri[iyon]["ad"] if iyon in iyon_bilgileri else iyon
pdf.multi_cell(0, 7, f"{iyon} ({iyon_adi}) - {miktar:.2f} mmol/L fazla", 0, 'L')

if iyon in iyon_bilgileri:
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 10)
pdf.multi_cell(0, 6, f"Olasi etkiler: {iyon_bilgileri[iyon]['fazla']}", 0, 'L')
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 11)
pdf.ln(2)

# Gübre önerileri
if oneriler:
pdf.ln(5)
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 14)
pdf.cell(0, 10, 'Gubre Onerileri', 0, 1, 'L')
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 11)

for iyon, gubre_listesi in oneriler.items():
iyon_adi = iyon_bilgileri[iyon]["ad"] if iyon in iyon_bilgileri else iyon
pdf.multi_cell(0, 7, f"{iyon} ({iyon_adi}) icin onerilen gubreler:", 0, 'L')

for gubre in gubre_listesi:
pdf.multi_cell(0, 6, f"• {gubre}", 0, 'L')
pdf.ln(2)

pdf.ln(10)
pdf.set_font('DejaVu' if 'DejaVu' in pdf.fonts else 'Arial', '', 9)
pdf.cell(0, 5, 'HydroBuddy Turkce | Hidroponik besin cozeltisi hesaplama araci', 0, 1, 'C')

return pdf.output(dest='S').encode('latin1')
except Exception as e:
logger.error(f"PDF oluşturma hatası: {str(e)}")
raise e

# ---------------------------------------------------
# Ana Uygulama
# ---------------------------------------------------

# Session state başlat
session_state_baslat()

# Sidebar
with st.sidebar:
st.header("Ayarlar")
if st.button("Session State'i Sıfırla"):
session_state_sifirla()

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
- **A Tankı**: Kalsiyum içeren gübreler (örn. kalsiyum nitrat) için.
- **B Tankı**: Fosfat ve sülfat içeren gübreler için.
- **Konsantrasyon Oranı**: Stok çözeltinin son kullanım konsantrasyonundan kaç kat daha konsantre olduğunu belirtir.
""")

with col2:
st.header("Reçete Değerleri")
col_a, col_b = st.columns(2)
with col_a:
st.subheader("Anyonlar (mmol/L)")
for ion in ["NO3", "H2PO4", "SO4"]:
st.session_state.recete[ion] = st.number_input(
f"{ion}:", value=float(st.session_state.recete[ion]), min_value=0.0, max_value=30.0, step=0.1, format="%.2f", key=f"{ion}_input"
)
with col_b:
st.subheader("Katyonlar (mmol/L)")
for ion in ["NH4", "K", "Ca", "Mg"]:
st.session_state.recete[ion] = st.number_input(
f"{ion}:", value=float(st.session_state.recete[ion]), min_value=0.0, max_value=20.0, step=0.1, format="%.2f", key=f"{ion}_input"
)

st.subheader("Mikro Besinler (mikromol/L)")
col_m1, col_m2, col_m3 = st.columns(3)
for col, elements in [(col_m1, ["Fe", "Mn"]), (col_m2, ["B", "Zn"]), (col_m3, ["Cu", "Mo"])]:
with col:
for element in elements:
st.session_state.recete[element] = st.number_input(
f"{element}:", value=float(st.session_state.recete.get(element, 0.0)), min_value=0.0, max_value=100.0, step=0.1, format="%.1f", key=f"{element}_input"
)

st.subheader("İyonik Denge")
anyon_toplam, katyon_toplam = hesapla_iyonik_denge(st.session_state.recete)
col_denge1, col_denge2 = st.columns(2)

with col_denge1:
anyon_df = pd.DataFrame(
[[ion, st.session_state.recete[ion], st.session_state.recete[ion] * abs(iyon_degerlikleri[ion])] for ion in ["NO3", "H2PO4", "SO4"]],
columns=["Anyon", "mmol/L", "me/L"]
)
st.write("**Anyonlar:**")
st.dataframe(anyon_df.style.format({"mmol/L": "{:.2f}", "me/L": "{:.2f}"}))
st.write(f"**Toplam:** {anyon_toplam:.2f} me/L")

with col_denge2:
katyon_df = pd.DataFrame(
[[ion, st.session_state.recete[ion], st.session_state.recete[ion] * abs(iyon_degerlikleri[ion])] for ion in ["NH4", "K", "Ca", "Mg"]],
columns=["Katyon", "mmol/L", "me/L"]
)
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
st.markdown("**İyileştirme Önerisi:** " + ("Anyon fazlası var. Daha fazla katyon ekleyin." if anyon_toplam > katyon_toplam else "Katyon fazlası var. Daha fazla anyon ekleyin."))

# Tab 2: Kuyu Suyu
with tabs[1]:
st.header("Kuyu Suyu Analizi")
st.info("Kuyu suyu kullanıyorsanız, içindeki iyonları girerek hesaplamada dikkate alınmasını sağlayabilirsiniz.")

col1, col2 = st.columns(2)
for col, ions in [(col1, ["NO3", "H2PO4", "SO4"]), (col2, ["NH4", "K", "Ca", "Mg"])]:
with col:
st.subheader(f"{'Anyonlar' if col == col1 else 'Katyonlar'} (mmol/L)")
for ion in ions:
st.session_state.kuyu_suyu[ion] = st.number_input(
f"{ion}:", value=float(st.session_state.kuyu_suyu[ion]), min_value=0.0, max_value=10.0, step=0.05, format="%.2f", key=f"kuyu_{ion}_input"
)

if sum(st.session_state.kuyu_suyu.values()) > 0:
st.success("✅ Kuyu suyu değerleri kaydedildi ve hesaplamalarda dikkate alınacak.")
else:
st.info("ℹ️ Şu anda kuyu suyu değeri girilmemiş. Saf su varsayılacak.")

# Tab 3: Gübre Seçimi
with tabs[2]:
st.header("Elimdeki Gübreler")
st.info("Kullanmak istediğiniz gübreleri seçin. Hesaplamalar sadece seçilen gübrelerle yapılır.")

col1, col2 = st.columns(2)

with col1:
st.subheader("Makro Gübreler")
a_tank_gubreler = [gubre for gubre in gubreler.keys() if gubreler[gubre]["tank"] == "A"]
b_tank_gubreler = [gubre for gubre in gubreler.keys() if gubreler[gubre]["tank"] == "B"]

st.markdown("**A Tankı Gübreleri**")
for gubre in a_tank_gubreler:
secildi = st.checkbox(
f"☐ {gubre} ({gubreler[gubre]['formul']})",
value=gubre in st.session_state.secilen_gubreler,
key=f"checkbox_{gubre}"
)
gubre_secimini_guncelle(gubre, secildi)

st.markdown("**B Tankı Gübreleri**")
for gubre in b_tank_gubreler:
secildi = st.checkbox(
f"☐ {gubre} ({gubreler[gubre]['formul']})",
value=gubre in st.session_state.secilen_gubreler,
key=f"checkbox_b_{gubre}"
)
gubre_secimini_guncelle(gubre, secildi)

with col2:
st.subheader("Mikro Gübreler")
mikro_element_gruplari = {}
for gubre, bilgi in mikro_gubreler.items():
mikro_element_gruplari.setdefault(bilgi["element"], []).append(gubre)

for element, gubreler_listesi in mikro_element_gruplari.items():
st.markdown(f"**{element} Kaynağı**")
secilen_gubre = st.radio(
f"{element} için gübre seçimi",
options=["Seçilmedi"] + gubreler_listesi,
index=0 if st.session_state.secilen_mikro_gubreler[element] not in gubreler_listesi else gubreler_listesi.index(st.session_state.secilen_mikro_gubreler[element]) + 1,
key=f"radio_{element}"
)
mikro_gubre_sec(element, secilen_gubre)

# Karşılanabilirlik analizi
secilen_gubreler = st.session_state.secilen_gubreler

if secilen_gubreler:
eksik_besinler = karsilanabilirlik_kontrolu(st.session_state.recete, secilen_gubreler)
if eksik_besinler:
st.error(f"⚠️ Seçilen gübrelerle karşılanamayan besinler: {', '.join(eksik_besinler)}")
else:
st.success("✅ Seçilen gübrelerle tüm besinler karşılanabilir.")

# Tab 4: Gübre Hesaplamaimport streamlit as st
import pandas as pd
import numpy as np
import base64
from fpdf import FPDF
from io import BytesIO
import datetime
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HydroBuddy")

# Yapılandırma sabitleri
IYON_ESIK_DEGERI = 0.1  # mmol/L
MIKRO_GUBRE_G_CARPANI = 1000  # g/kg
PDF_FONT_PATH = 'DejaVuSansCondensed.ttf'  # PDF için Türkçe karakter fontu

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

# ---------------------------------------------------
# Yardımcı Fonksiyonlar
# ---------------------------------------------------

def session_state_baslat():
"""Session state değişkenlerini başlatır veya varsayılan değerlerle oluşturur."""
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

def session_state_sifirla():
"""Tüm session state değişkenlerini sıfırlar."""
for key in list(st.session_state.keys()):
del st.session_state[key]
session_state_baslat()
st.success("Session state sıfırlandı!")

def hesapla_iyonik_denge(recete):
"""Reçetedeki anyon ve katyon dengesini hesaplar.

Args:
recete (dict): İyon değerlerini içeren reçete sözlüğü

Returns:
tuple: (anyon_toplam, katyon_toplam) değerlerini içeren tuple
"""
anyon_toplam = sum(float(recete[ion]) * abs(iyon_degerlikleri[ion]) for ion in ["NO3", "H2PO4", "SO4"])
katyon_toplam = sum(float(recete[ion]) * abs(iyon_degerlikleri[ion]) for ion in ["NH4", "K", "Ca", "Mg"])
return anyon_toplam, katyon_toplam

def gubre_secimini_guncelle(gubre, secildi):
"""Gübre seçimini session state içinde günceller.

Args:
gubre (str): Gübre adı
secildi (bool): Seçilme durumu
"""
if secildi:
if gubre not in st.session_state.secilen_gubreler:
st.session_state.secilen_gubreler.append(gubre)
else:
if gubre in st.session_state.secilen_gubreler:
st.session_state.secilen_gubreler.remove(gubre)

def mikro_gubre_sec(element, secilen_gubre):
"""Mikro besin için gübre seçimini günceller.

Args:
element (str): Element sembolü (Fe, B, vb.)
secilen_gubre (str): Seçilen gübre adı
"""
st.session_state.secilen_mikro_gubreler[element] = None if secilen_gubre == "Seçilmedi" else secilen_gubre

def karsilanabilirlik_kontrolu(recete, secilen_gubreler):
"""Reçetedeki besinlerin seçilen gübrelerle karşılanabilirliğini kontrol eder.

Args:
recete (dict): İyon değerlerini içeren reçete sözlüğü
secilen_gubreler (list): Seçilen gübrelerin listesi

Returns:
list: Karşılanamayan besinlerin listesi
"""
# Makro iyonlar için net ihtiyaç hesaplanır
net_ihtiyac = {ion: max(0, float(recete[ion])) for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]}

# Gübre kullanım simülasyonu
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
if "Potasyum Sülfat" in secilen_gubreler and net_ihtiyac["K"] > 0:
ks_miktar = net_ihtiyac["K"] / 2
net_ihtiyac["SO4"] -= ks_miktar
net_ihtiyac["K"] = 0

# Negatif değerleri sıfırla
for iyon in net_ihtiyac:
if net_ihtiyac[iyon] < 0:
net_ihtiyac[iyon] = 0

# Belirli bir eşikten büyük ihtiyaçları karşılanmamış olarak döndür
return [iyon for iyon, miktar in net_ihtiyac.items() if miktar > IYON_ESIK_DEGERI]

def iyon_dengesini_hesapla(recete, secilen_gubreler):
"""İyon dengesini hesaplar ve eksik/fazla iyonları belirler.

Args:
recete (dict): İyon değerlerini içeren reçete sözlüğü
secilen_gubreler (list): Seçilen gübrelerin listesi

Returns:
tuple: (eksik_iyonlar, fazla_iyonlar) sözlüklerini içeren tuple
"""
makro_iyonlar = ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]
net_ihtiyac = {ion: float(recete[ion]) for ion in makro_iyonlar}
iyon_tüketim = {ion: 0.0 for ion in makro_iyonlar}

# Gübrelerden gelecek iyon katkılarını hesapla
for gubre in secilen_gubreler:
if gubre in gubreler:
for iyon, katsayi in gubreler[gubre]["iyonlar"].items():
if iyon in iyon_tüketim:
if gubre == "Kalsiyum Nitrat" and iyon == "Ca":
iyon_tüketim["Ca"] += net_ihtiyac["Ca"]
elif gubre == "Kalsiyum Nitrat" and iyon == "NO3":
iyon_tüketim["NO3"] += 2 * net_ihtiyac["Ca"]
elif gubre == "Magnezyum Nitrat" and iyon == "Mg":
iyon_tüketim["Mg"] += net_ihtiyac["Mg"]
elif gubre == "Magnezyum Nitrat" and iyon == "NO3":
iyon_tüketim["NO3"] += 2 * net_ihtiyac["Mg"]
elif gubre == "Magnezyum Sülfat" and iyon == "Mg":
iyon_tüketim["Mg"] += net_ihtiyac["Mg"]
elif gubre == "Magnezyum Sülfat" and iyon == "SO4":
iyon_tüketim["SO4"] += net_ihtiyac["Mg"]
elif gubre == "Monopotasyum Fosfat" and iyon == "H2PO4":
iyon_tüketim["H2PO4"] += net_ihtiyac["H2PO4"]
elif gubre == "Monopotasyum Fosfat" and iyon == "K":
iyon_tüketim["K"] += net_ihtiyac["H2PO4"]
elif gubre == "Monoamonyum Fosfat" and iyon == "H2PO4":
iyon_tüketim["H2PO4"] += net_ihtiyac["H2PO4"]
elif gubre == "Monoamonyum Fosfat" and iyon == "NH4":
iyon_tüketim["NH4"] += net_ihtiyac["H2PO4"]
elif gubre == "Potasyum Nitrat" and iyon == "K" and net_ihtiyac["K"] > 0 and net_ihtiyac["NO3"] > 0:
kn_miktar = min(net_ihtiyac["K"], net_ihtiyac["NO3"])
iyon_tüketim["K"] += kn_miktar
iyon_tüketim["NO3"] += kn_miktar
elif gubre == "Potasyum Sülfat" and iyon == "K" and net_ihtiyac["K"] > 0:
iyon_tüketim["K"] += net_ihtiyac["K"]
iyon_tüketim["SO4"] += net_ihtiyac["K"] / 2
elif gubre == "Amonyum Sülfat" and iyon == "NH4" and net_ihtiyac["NH4"] > 0:
as_miktar = min(net_ihtiyac["NH4"] / 2, net_ihtiyac["SO4"])
iyon_tüketim["NH4"] += 2 * as_miktar
iyon_tüketim["SO4"] += as_miktar

# Eksik ve fazla iyonları hesapla
eksik_iyonlar = {}
fazla_iyonlar = {}

for iyon in makro_iyonlar:
fark = net_ihtiyac[iyon] - iyon_tüketim[iyon]
if fark > IYON_ESIK_DEGERI:  # Eşikten fazla eksikse
eksik_iyonlar[iyon] = fark
elif fark < -IYON_ESIK_DEGERI:  # Eşikten fazla fazlaysa
fazla_iyonlar[iyon] = -fark

return eksik_iyonlar, fazla_iyonlar

def gubre_onerileri_olustur(eksik_iyonlar, secilen_gubreler):
"""Eksik iyonlar için gübre önerileri oluşturur.

Args:
eksik_iyonlar (dict): Eksik iyonlar ve miktarları
secilen_gubreler (list): Şu an seçilmiş gübreler

Returns:
dict: Her eksik iyon için önerilen gübre listelerini içeren sözlük
"""
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
"""Mikro besin hesaplamalarını yapar.

Args:
recete (dict): Reçete değerleri
secilen_mikro_gubreler (dict): Seçilen mikro gübreler
konsantrasyon (float): Konsantrasyon oranı
b_tank_hacmi (float): B tankı hacmi

Returns:
list: Mikro besin sonuçlarını içeren liste
"""
mikro_sonuc = []

for element, label in [("Fe", "Demir"), ("B", "Bor"), ("Mn", "Mangan"), ("Zn", "Çinko"), ("Cu", "Bakır"), ("Mo", "Molibden")]:
secilen_gubre = secilen_mikro_gubreler[element]

# Element seçilmiş ve reçetede değeri varsa hesapla
if secilen_gubre and element in recete and float(recete[element]) > 0:
try:
mikromol = float(recete[element])
gubre_bilgi = mikro_gubreler[secilen_gubre]
mmol = mikromol / 1000  # mikromol -> mmol dönüşümü
element_mol_agirligi = element_atomik_kutle[element] * (100 / gubre_bilgi["yuzde"])
mg_l = mmol * element_mol_agirligi
g_tank = (mg_l * float(konsantrasyon) * float(b_tank_hacmi)) / 1000
mikro_sonuc.append([secilen_gubre, gubre_bilgi["formul"], mikromol, mg_l, g_tank])

logger.info(f"Mikro besin hesaplandı: {element} - {mikromol} mikromol/L - {g_tank:.2f} gram")
except Exception as e:
logger.error(f"Mikro besin hesaplama hatası ({element}): {str(e)}")
st.error(f"Mikro besin '{element}' hesaplanırken hata: {str(e)}")

return mikro_sonuc

def hesapla_tank_gübreleri(tank_gübreleri, gubre_tipi, tank_hacmi, konsantrasyon):
"""Tank gübreleri için kütle hesaplamasını yapar.

Args:
tank_gübreleri (dict): Gübre adı ve mmol/L değerlerini içeren sözlük
gubre_tipi (str): "A" veya "B" tank gübre tipi
tank_hacmi (float): Tank hacmi (litre)
konsantrasyon (float): Konsantrasyon oranı

Returns:
tuple: (sonuçlar_listesi, toplam_ağırlık)
"""
sonuclar = []
toplam_agirlik = 0

for gubre, mmol in tank_gübreleri.items():
try:
if gubre not in gubreler:
logger.warning(f"{gubre_tipi} Tankı - '{gubre}' gübresi tanımlı değil
