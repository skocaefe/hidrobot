# --- Reçete Girişi ---
st.header("🧪 Reçete Girişi")

st.subheader("Makro İyonlar (mmol/L)")
makro_input = {}
cols = st.columns(4)
for i, ion in enumerate(makro_iyonlar):
    with cols[i%4]:
        makro_input[ion] = st.number_input(f"{ion}", min_value=0.0, value=5.0, step=0.1, key=f"makro_{ion}")

st.subheader("Mikro Elementler (µmol/L)")
mikro_input = {}
cols2 = st.columns(3)
for i, element in enumerate(mikro_elementler):
    with cols2[i%3]:
        mikro_input[element] = st.number_input(f"{element}", min_value=0.0, value=25.0, step=1.0, key=f"mikro_{element}")

# --- Gübre Seçimi ---
st.header("🧪 Gübre Seçimi")

st.subheader("Makro Gübreler")
secilen_makro = []
for gubre in makro_gubreler.keys():
    if st.checkbox(f"{gubre} ({makro_gubreler[gubre]['formul']})", key=f"sec_{gubre}"):
        secilen_makro.append(gubre)

st.subheader("Mikro Gübreler")
secilen_mikro = {}
for element in mikro_elementler:
    uygunlar = [gubre for gubre, bilgi in mikro_gubreler.items() if bilgi["element"] == element]
    secim = st.radio(f"{element} için Gübre Seçimi", ["Seçilmedi"]+uygunlar, horizontal=True, key=f"sec_micro_{element}")
    if secim != "Seçilmedi":
        secilen_mikro[element] = secim

# --- Hesaplama Butonu ---
if st.button("🚀 Hesapla"):
    hedef = np.array([makro_input[ion] for ion in makro_iyonlar])
    A = []
    for gubre in secilen_makro:
        kolon = []
        for ion in makro_iyonlar:
            kolon.append(makro_gubreler[gubre]["iyonlar"].get(ion,0))
        A.append(kolon)
    A = np.array(A).T

    sonuc, residuals, rank, s = np.linalg.lstsq(A, hedef, rcond=None)

    mevcut = A @ sonuc
    fark = mevcut - hedef

    st.success("✅ Hesaplama Başarılı!")

    st.subheader("📦 A ve B Tankı Gübreleri")
    a_tank = []
    b_tank = []
    for idx, gubre in enumerate(secilen_makro):
        mmol = sonuc[idx]
        mg_per_l = mmol * makro_gubreler[gubre]["molar_agirlik"]
        toplam_gram = mg_per_l * konsantrasyon_orani * tank_hacmi / 1000
        if makro_gubreler[gubre]["tank"] == "A":
            a_tank.append((gubre, toplam_gram/1000))
        else:
            b_tank.append((gubre, toplam_gram/1000))

    st.write("### A Tankı")
    if a_tank:
        st.dataframe(pd.DataFrame(a_tank, columns=["Gübre","Kg"]))

    st.write("### B Tankı")
    if b_tank:
        st.dataframe(pd.DataFrame(b_tank, columns=["Gübre","Kg"]))

    st.subheader("🌱 Mikro Gübreler")
    mikro_sonuc = []
    for element, gubre in secilen_mikro.items():
        hedef_umol = mikro_input[element]
        if gubre:
            yuzde = mikro_gubreler[gubre]["yuzde"]
            element_agirlik = element_atom_agirlik[element]
            mg_l = (hedef_umol/1000)*element_agirlik
            toplam_mg = mg_l * konsantrasyon_orani * tank_hacmi
            mikro_sonuc.append((gubre, toplam_mg*100/yuzde/1000))

    if mikro_sonuc:
        st.dataframe(pd.DataFrame(mikro_sonuc, columns=["Mikro Gübre","Gram"]))

    toplam_mmol = sum(makro_input.values())
    tahmini_ec = toplam_mmol * 0.64
    st.metric("Tahmini EC", f"{tahmini_ec:.2f} dS/m")

    # --- Eksik Fazla Analiz ---
    st.header("🔎 İyon Denge Analizi")

    analiz = []
    for idx, ion in enumerate(makro_iyonlar):
        if abs(fark[idx]) > 0.1:
            durum = "Fazla" if fark[idx] > 0 else "Eksik"
            etkiler = ""
            oneriler = ""

            if ion == "NO3":
                etkiler = "Nitrat fazla ➔ pH artar. Eksik ➔ Azot yetersizliği."
                oneriler = "Kalsiyum Nitrat, Potasyum Nitrat"
            elif ion == "H2PO4":
                etkiler = "Fosfor fazla ➔ Lüks tüketim. Eksik ➔ Zayıf kök gelişimi."
                oneriler = "Monopotasyum Fosfat, Monoamonyum Fosfat"
            elif ion == "SO4":
                etkiler = "Sülfat fazla ➔ Tuzluluk artışı. Eksik ➔ Kükürt eksikliği."
                oneriler = "Magnezyum Sülfat, Potasyum Sülfat"
            elif ion == "NH4":
                etkiler = "Amonyum fazla ➔ pH düşer, toksisite. Eksik ➔ pH yükselir."
                oneriler = "Amonyum Sülfat, Monoamonyum Fosfat"
            elif ion == "K":
                etkiler = "Potasyum fazla ➔ Tuzluluk artar. Eksik ➔ Meyve kalitesi düşer."
                oneriler = "Potasyum Nitrat, Potasyum Sülfat"
            elif ion == "Ca":
                etkiler = "Kalsiyum fazla ➔ Magnezyum alımı düşer. Eksik ➔ Çiçek ucu çürümesi."
                oneriler = "Kalsiyum Nitrat"
            elif ion == "Mg":
                etkiler = "Magnezyum fazla ➔ Kalsiyum alımı düşer. Eksik ➔ Sararma."
                oneriler = "Magnezyum Sülfat, Magnezyum Nitrat"

            analiz.append((ion, durum, round(fark[idx],2), etkiler, oneriler))

    if analiz:
        df_analiz = pd.DataFrame(analiz, columns=["İyon","Durum","Fark (mmol/L)","Etkisi","Tavsiye Edilen Gübreler"])
        st.dataframe(df_analiz)
    else:
        st.success("✅ İyon dengesi çok iyi!")

# --- Nasıl Hazırlanır ---
with st.expander("🧴 Çözelti Nasıl Hazırlanır?"):
    st.markdown("""
    1. Her tank için ayrı kaplar hazırlayın.
    2. Önce suyun %70'ini ekleyin.
    3. Seçilen gübreleri sırayla karıştırarak çözündürün.
    4. Tamamen çözündükten sonra suyu tamamlayın.
    5. Karışımı tanklara alın.
    6. EC ve pH kontrolü yaparak sisteme verin.
    7. Su sıcaklığı 20°C civarında olmalıdır.
    """)
