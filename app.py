gozden gecirin.'}")
            else:
                st.success("Tum besinler secilen gubrelerle karsilanabilir.")

    # Tab 4: Gubre Hesaplama
    with tabs[3]:
        st.header("Gubre Hesaplama")
        if st.button("Gubre Hesapla", type="primary"):
            # Hesaplamayi yap ve sonucu kaydet
            st.session_state.hesaplama_sonucu = gubre_hesapla()
            
            # Hesaplama sonucunu goster
            if st.session_state.hesaplama_sonucu:
                goster_hesaplama_sonucu(st.session_state.hesaplama_sonucu)

    # Alt bilgi
    st.markdown("---")
    st.markdown("HydroBuddy Turkce | Hidroponik besin cozeltisi hesaplama araci")

# Uygulamayi calistir
if __name__ == "__main__":
    main().items():
        if miktar > 0.1:
            eksik_var = True
            uyari += f" {iyon}: {miktar:.2f} mmol/L,"

    if eksik_var:
        st.warning(f"Secilen gubrelerle karsilanamayan besinler:{uyari[:-1]}")
        st.markdown("**Onerilen Gubreler:**")
        for iyon, miktar in hesaplama_sonucu["net_ihtiyac"].items():
            if miktar > 0.1:
                oneriler = [f"☐ {gubre} ({bilgi['formul']})" for gubre, bilgi in gubreler.items() if iyon in bilgi["iyonlar"] and gubre not in secilen_gubreler]
                st.markdown(f"- {iyon} icin: {', '.join(oneriler) if oneriler else 'Receteyi gozden gecirin.'}")
    else:
        st.success("Tum besinler secilen gubrelerle karsilandi.")

    # Hesaplama adimlari
    with st.expander("Hesaplama Adimlari"):
        for log in st.session_state.hesaplama_log:
            st.write(f"**{log['adim']}:** {log['aciklama']}")
            if log["ihtiyac"]:
                ihtiyac_df = pd.DataFrame([[k, v] for k, v in log["ihtiyac"].items()], columns=["Iyon", "Ihtiyac (mmol/L)"])
                st.dataframe(ihtiyac_df.style.format({"Ihtiyac (mmol/L)": "{:.2f}"}))
            st.markdown("---")

# Ana uygulama
def main():
    # Session state'i baslat
    initialize_session_state()

    # Ana duzeni olustur
    tabs = st.tabs(["Recete Olusturma", "Kuyu Suyu", "Gubre Secimi", "Gubre Hesaplama"])

    # Tab 1: Recete Olusturma
    with tabs[0]:
        col1, col2 = st.columns([1, 2])

        with col1:
            st.header("Recete ve Tank Ayarlari")
            secilen_recete = st.selectbox("Hazir Recete:", options=list(hazir_receteler.keys()))

            if st.button("Receteyi Yukle"):
                st.session_state.recete = hazir_receteler[secilen_recete].copy()
                st.success(f"{secilen_recete} recetesi yuklendi!")

            st.subheader("Tank Ayarlari")
            st.session_state.a_tank = st.number_input("A Tanki Hacmi (litre):", min_value=1, max_value=1000, value=st.session_state.a_tank)
            st.session_state.b_tank = st.number_input("B Tanki Hacmi (litre):", min_value=1, max_value=1000, value=st.session_state.b_tank)
            st.session_state.konsantrasyon = st.number_input("Konsantrasyon Orani:", min_value=1, max_value=1000, value=st.session_state.konsantrasyon)

            st.info("""
            **Tank Ayarlari Bilgisi:**
            - **A Tanki**: Kalsiyum iceren gubreler (orn. kalsiyum nitrat) icin.
            - **B Tanki**: Fosfat ve sulfat iceren gubreler icin.
            - **Konsantrasyon Orani**: Stok cozelti son kullanim konsantrasyonundan kac kat daha konsantre oldugunu belirtir.
            """)

        with col2:
            st.header("Recete Degerleri")
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

            st.subheader("Iyonik Denge")
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
                st.success(f"Iyonik denge iyi durumda! (Fark: {fark:.2f} me/L)")
            elif fark < 1.0:
                st.warning(f"Iyonik denge kabul edilebilir sinirda. (Fark: {fark:.2f} me/L)")
            else:
                st.error(f"Iyonik denge bozuk! (Fark: {fark:.2f} me/L)")
                st.markdown("**Iyilestirme Onerisi:** " + ("Anyon fazlasi var. Daha fazla katyon ekleyin." if anyon_toplam > katyon_toplam else "Katyon fazlasi var. Daha fazla anyon ekleyin."))

    # Tab 2: Kuyu Suyu
    with tabs[1]:
        st.header("Kuyu Suyu Analizi")
        st.info("Kuyu suyu kullaniyorsaniz, icindeki iyonlari girerek hesaplamada dikkate alinmasini sagayabilirsiniz.")

        col1, col2 = st.columns(2)
        for col, ions in [(col1, ["NO3", "H2PO4", "SO4"]), (col2, ["NH4", "K", "Ca", "Mg"])]:
            with col:
                st.subheader(f"{'Anyonlar' if col == col1 else 'Katyonlar'} (mmol/L)")
                for ion in ions:
                    st.session_state.kuyu_suyu[ion] = st.number_input(
                        f"{ion}:", value=float(st.session_state.kuyu_suyu[ion]), min_value=0.0, max_value=10.0, step=0.05, format="%.2f", key=f"kuyu_{ion}_input"
                    )

        if sum(st.session_state.kuyu_suyu.values()) > 0:
            st.success("Kuyu suyu degerleri kaydedildi ve hesaplamalarda dikkate alinacak.")
        else:
            st.info("Su anda kuyu suyu degeri girilmemis. Saf su varsayilacak.")

    # Tab 3: Gubre Secimi
    with tabs[2]:
        st.header("Elimdeki Gubreler")
        st.info("Kullanmak istediginiz gübreleri secin. Hesaplamalar sadece secilen gübrelerle yapilir.")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Makro Gubreler")
            a_tank_gubreler = [gubre for gubre, bilgi in gubreler.items() if bilgi["tank"] == "A"]
            b_tank_gubreler = [gubre for gubre, bilgi in gubreler.items() if bilgi["tank"] == "B"]

            st.markdown("**A Tanki Gübreleri**")
            for gubre in a_tank_gubreler:
                st.session_state.kullanilabilir_gubreler[gubre] = st.checkbox(
                    f"☐ {gubre} ({gubreler[gubre]['formul']})",
                    value=st.session_state.kullanilabilir_gubreler.get(gubre, False),
                    key=f"checkbox_{gubre}"
                )

            st.markdown("**B Tanki Gübreleri**")
            for gubre in b_tank_gubreler:
                st.session_state.kullanilabilir_gubreler[gubre] = st.checkbox(
                    f"☐ {gubre} ({gubreler[gubre]['formul']})",
                    value=st.session_state.kullanilabilir_gubreler.get(gubre, False),
                    key=f"checkbox_b_{gubre}"
                )

        with col2:
            st.subheader("Mikro Gubreler")
            mikro_element_gruplari = {}
            for gubre, bilgi in mikro_gubreler.items():
                mikro_element_gruplari.setdefault(bilgi["element"], []).append(gubre)

            for element, gubreler in mikro_element_gruplari.items():
                st.markdown(f"**{element} Kaynagi**")
                secilen_gubre = st.radio(
                    f"{element} icin gubre secimi",
                    options=["Secilmedi"] + gubreler,
                    index=0 if st.session_state.secilen_mikro_gubreler[element] not in gubreler else gubreler.index(st.session_state.secilen_mikro_gubreler[element]) + 1,
                    key=f"radio_{element}"
                )
                st.session_state.secilen_mikro_gubreler[element] = None if secilen_gubre == "Secilmedi" else secilen_gubre
                for gubre in gubreler:
                    st.session_state.kullanilabilir_mikro_gubreler[gubre] = (gubre == secilen_gubre)

        # Secilen gübreleri al
        secilen_gubreler = [gubre for gubre, secildi in st.session_state.kullanilabilir_gubreler.items() if secildi]
        secilen_mikro_gubreler = [gubre for element, gubre in st.session_state.secilen_mikro_gubreler.items() if gubre]

        st.subheader("Secilen Gubreler")
        if secilen_gubreler:
            st.write("**Makro Gubreler:**")
            for gubre in secilen_gubreler:
                if gubre in gubreler:
                    st.write(f"✓ {gubre} ({gubreler[gubre]['formul']})")
                else:
                    st.warning(f"Uyari: '{gubre}' gubresi tanimli degil!")
        else:
            st.warning("Henuz makro gubre secmediniz!")

        if secilen_mikro_gubreler:
            st.write("**Mikro Gubreler:**")
            for gubre in secilen_mikro_gubreler:
                if gubre in mikro_gubreler:
                    st.write(f"✓ {gubre} ({mikro_gubreler[gubre]['formul']})")
                else:
                    st.warning(f"Uyari: '{gubre}' mikro gubresi tanimli degil!")
        else:
            st.warning("Henuz mikro gubre secmediniz!")

        # Hata ayiklama
        with st.expander("Hata Ayiklama: Gubre Durumu"):
            st.write(f"**Secilen Makro Gubreler:** {secilen_gubreler}")
            st.write(f"**Tum Kullanilabilir Gubreler Durumu:** {st.session_state.kullanilabilir_gubreler}")

        if secilen_gubreler:
            eksik_besinler = karsilanabilirlik_kontrolu(st.session_state.recete, secilen_gubreler)
            if eksik_besinler:
                st.error(f"Secilen gubrelerle karsilanamayan besinler: {', '.join(eksik_besinler)}")
                st.markdown("**Onerilen Gubreler:**")
                for besin in eksik_besinler:
                    oneriler = [f"☐ {gubre} ({bilgi['formul']})" for gubre, bilgi in gubreler.items() if besin in bilgi["iyonlar"] and gubre not in secilen_gubreler]
                    st.markdown(f"- {besin} icin: {', '.join(oneriler) if oneriler else 'Receteyi        net_ihtiyac.items()}
    })

    # 1. Kalsiyum Nitrat
    if "Kalsiyum Nitrat" in secilen_gubreler and net_ihtiyac["Ca"] > 0:
        ca_miktar = net_ihtiyac["Ca"]
        a_tank_gubreler["Kalsiyum Nitrat"] = ca_miktar
        net_ihtiyac["Ca"] = 0
        net_ihtiyac["NO3"] -= 2 * ca_miktar
        st.session_state.hesaplama_log.append({
            "adim": f"Adim {adim}", "aciklama": f"Kalsiyum Nitrat: {ca_miktar:.2f} mmol/L",
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
            "adim": f"Adim {adim}", "aciklama": f"Magnezyum Nitrat: {mg_miktar:.2f} mmol/L",
            "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
        })
        adim += 1

    # 3. Magnezyum Sulfat
    if "Magnezyum Sulfat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        mg_miktar = net_ihtiyac["Mg"]
        b_tank_gubreler["Magnezyum Sulfat"] = mg_miktar
        net_ihtiyac["Mg"] = 0
        net_ihtiyac["SO4"] -= mg_miktar
        st.session_state.hesaplama_log.append({
            "adim": f"Adim {adim}", "aciklama": f"Magnezyum Sulfat: {mg_miktar:.2f} mmol/L",
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
            "adim": f"Adim {adim}", "aciklama": f"Monopotasyum Fosfat: {mkp_miktar:.2f} mmol/L",
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
            "adim": f"Adim {adim}", "aciklama": f"Monoamonyum Fosfat: {map_miktar:.2f} mmol/L",
            "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
        })
        adim += 1

    # 6. Amonyum Sulfat
    if "Amonyum Sulfat" in secilen_gubreler and net_ihtiyac["NH4"] > 0:
        as_miktar = net_ihtiyac["NH4"] / 2
        b_tank_gubreler["Amonyum Sulfat"] = as_miktar
        net_ihtiyac["NH4"] = 0
        net_ihtiyac["SO4"] -= as_miktar
        st.session_state.hesaplama_log.append({
            "adim": f"Adim {adim}", "aciklama": f"Amonyum Sulfat: {as_miktar:.2f} mmol/L",
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
            "adim": f"Adim {adim}", "aciklama": f"Potasyum Nitrat: {kn_miktar:.2f} mmol/L",
            "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
        })
        adim += 1

    # 8. Potasyum Sulfat
    if "Potasyum Sulfat" in secilen_gubreler and net_ihtiyac["K"] > 0:
        ks_miktar = net_ihtiyac["K"] / 2
        b_tank_gubreler["Potasyum Sulfat"] = ks_miktar
        net_ihtiyac["K"] = 0
        net_ihtiyac["SO4"] -= ks_miktar
        st.session_state.hesaplama_log.append({
            "adim": f"Adim {adim}", "aciklama": f"Potasyum Sulfat: {ks_miktar:.2f} mmol/L",
            "ihtiyac": {k: round(v, 2) for k, v in net_ihtiyac.items()}
        })
        adim += 1

    # Negatif ihtiyaclari sifirla
    negatif_ihtiyaclar = {iyon: miktar for iyon, miktar in net_ihtiyac.items() if miktar < -0.1}
    for iyon in net_ihtiyac:
        if net_ihtiyac[iyon] < 0:
            net_ihtiyac[iyon] = 0

    # Mikro besin hesaplamalari
    mikro_sonuc = []
    for element, label in [("Fe", "Demir"), ("B", "Bor"), ("Mn", "Mangan"), ("Zn", "Cinko"), ("Cu", "Bakir"), ("Mo", "Molibden")]:
        secilen_gubre = st.session_state.secilen_mikro_gubreler[element]
        if secilen_gubre and element in st.session_state.recete and float(st.session_state.recete[element]) > 0:
            try:
                mikromol = float(st.session_state.recete[element])
                gubre_bilgi = mikro_gubreler[secilen_gubre]
                mmol = mikromol / 1000
                element_mol_agirligi = element_atomik_kutle[element] * (100 / gubre_bilgi["yuzde"])
                mg_l = mmol * element_mol_agirligi
                g_tank = (mg_l * float(st.session_state.konsantrasyon) * float(st.session_state.b_tank)) / 1000
                mikro_sonuc.append([secilen_gubre, gubre_bilgi["formul"], mikromol, mg_l, g_tank])
            except (TypeError, ValueError) as e:
                st.error(f"Mikro besin '{element}' hesaplanirken hata: {str(e)}")

    # Kutle hesaplamalari
    a_tank_sonuc = []
    a_tank_toplam = 0
    for gubre, mmol in a_tank_gubreler.items():
        try:
            formul = gubreler[gubre]["formul"]
            mg_l = float(mmol) * float(gubreler[gubre]["agirlik"])
            g_tank = (mg_l * float(st.session_state.konsantrasyon) * float(st.session_state.a_tank)) / 1000
            kg_tank = g_tank / 1000
            a_tank_toplam += g_tank
            a_tank_sonuc.append([gubre, formul, mmol, mg_l, kg_tank])
        except (TypeError, ValueError, KeyError) as e:
            st.error(f"A Tanki gubresi '{gubre}' hesaplanirken hata: {str(e)}")

    b_tank_sonuc = []
    b_tank_toplam = 0
    for gubre, mmol in b_tank_gubreler.items():
        try:
            formul = gubreler[gubre]["formul"]
            mg_l = float(mmol) * float(gubreler[gubre]["agirlik"])
            g_tank = (mg_l * float(st.session_state.konsantrasyon) * float(st.session_state.b_tank)) / 1000
            kg_tank = g_tank / 1000
            b_tank_toplam += g_tank
            b_tank_sonuc.append([gubre, formul, mmol, mg_l, kg_tank])
        except (TypeError, ValueError, KeyError) as e:
            st.error(f"B Tanki gubresi '{gubre}' hesaplanirken hata: {str(e)}")

    # Sonuclari kaydet
    hesaplama_sonucu = {
        "a_tank_sonuc": a_tank_sonuc,
        "b_tank_sonuc": b_tank_sonuc,
        "mikro_sonuc": mikro_sonuc,
        "a_tank_toplam": a_tank_toplam,
        "b_tank_toplam": b_tank_toplam,
        "negatif_ihtiyaclar": negatif_ihtiyaclar,
        "net_ihtiyac": net_ihtiyac
    }

    return hesaplama_sonucu

# Hesaplama sonucunu gosterme fonksiyonu
def goster_hesaplama_sonucu(hesaplama_sonucu):
    if hesaplama_sonucu is None:
        return

    # A Tanki sonuclari
    col_sonuc1, col_sonuc2 = st.columns(2)
    with col_sonuc1:
        st.subheader("A Tanki (Kalsiyum iceren)")
        if hesaplama_sonucu["a_tank_sonuc"]:
            a_tank_df = pd.DataFrame(hesaplama_sonucu["a_tank_sonuc"], columns=["Gubre Adi", "Formul", "mmol/L", "mg/L", "kg/Tank"])
            st.dataframe(a_tank_df.style.format({"mmol/L": "{:.2f}", "mg/L": "{:.2f}", "kg/Tank": "{:.3f}"}))
            st.write(f"**Toplam A Tanki gubresi:** {hesaplama_sonucu['a_tank_toplam']/1000:.3f} kg")
        else:
            st.info("A Tanki icin gubre eklenmedi.")

    with col_sonuc2:
        st.subheader("B Tanki (Fosfat, Sulfat ve Amonyum)")
        if hesaplama_sonucu["b_tank_sonuc"]:
            b_tank_df = pd.DataFrame(hesaplama_sonucu["b_tank_sonuc"], columns=["Gubre Adi", "Formul", "mmol/L", "mg/L", "kg/Tank"])
            st.dataframe(b_tank_df.style.format({"mmol/L": "{:.2f}", "mg/L": "{:.2f}", "kg/Tank": "{:.3f}"}))
            st.write(f"**Toplam B Tanki gubresi:** {hesaplama_sonucu['b_tank_toplam']/1000:.3f} kg")
        else:
            st.info("B Tanki icin gubre eklenmedi.")

    # Mikro besinler
    st.subheader("Mikro Besin Elementleri")
    if hesaplama_sonucu["mikro_sonuc"]:
        mikro_df = pd.DataFrame(hesaplama_sonucu["mikro_sonuc"], columns=["Gubre Adi", "Formul", "mikromol/L", "mg/L", "gram/Tank"])
        st.dataframe(mikro_df.style.format({"mikromol/L": "{:.2f}", "mg/L": "{:.4f}", "gram/Tank": "{:.2f}"}))
        mikro_toplam = sum(sonuc[4] for sonuc in hesaplama_sonucu["mikro_sonuc"])
        st.write(f"**Toplam mikro besin gubresi:** {mikro_toplam:.2f} gram")
    else:
        st.info("Mikro besin elementi eklenmedi.")

    # Kuyu suyu uyarisi
    if any(st.session_state.kuyu_suyu.values()):
        st.success("Kuyu suyu analiziniz hesaplamada dikkate alindi.")

    # Negatif ihtiyac uyarisi
    if hesaplama_sonucu["negatif_ihtiyaclar"]:
        st.warning("Asagidaki besinler recete ihtiyacindan fazla eklendi:")
        for iyon, miktar in hesaplama_sonucu["negatif_ihtiyaclar"].items():
            st.markdown(f"- {iyon}: {-miktar:.2f} mmol/L fazla")
        st.markdown("Bu, bitki sagligini etkileyebilir veya EC degerini yukseltebilir.")

    # Eksik besin kontrolu
    eksik_var = False
    uyari = ""
    for iyon, miktar in hesaplama_sonucu["net_ihtiyacimport streamlit as st
import pandas as pd
import numpy as np

# Sayfa ayarlari
st.set_page_config(page_title="HydroBuddy Turkce", page_icon="🌱", layout="wide")

# Baslik ve aciklama
st.title("🌱 HydroBuddy Turkce")
st.markdown("Hidroponik besin cozeltisi hesaplama araci")

# Iyon degerlikleri
iyon_degerlikleri = {
    "NO3": -1, "H2PO4": -1, "SO4": -2,
    "NH4": 1, "K": 1, "Ca": 2, "Mg": 2
}

# Gubre bilgileri
gubreler = {
    "Kalsiyum Nitrat": {"formul": "Ca(NO3)2.4H2O", "agirlik": 236.15, "tank": "A", "iyonlar": {"Ca": 1, "NO3": 2}},
    "Potasyum Nitrat": {"formul": "KNO3", "agirlik": 101.10, "tank": "A", "iyonlar": {"K": 1, "NO3": 1}},
    "Magnezyum Nitrat": {"formul": "Mg(NO3)2.6H2O", "agirlik": 256.41, "tank": "A", "iyonlar": {"Mg": 1, "NO3": 2}},
    "Monopotasyum Fosfat": {"formul": "KH2PO4", "agirlik": 136.09, "tank": "B", "iyonlar": {"K": 1, "H2PO4": 1}},
    "Magnezyum Sulfat": {"formul": "MgSO4.7H2O", "agirlik": 246.51, "tank": "B", "iyonlar": {"Mg": 1, "SO4": 1}},
    "Potasyum Sulfat": {"formul": "K2SO4", "agirlik": 174.26, "tank": "B", "iyonlar": {"K": 2, "SO4": 1}},
    "Amonyum Sulfat": {"formul": "(NH4)2SO4", "agirlik": 132.14, "tank": "B", "iyonlar": {"NH4": 2, "SO4": 1}},
    "Monoamonyum Fosfat": {"formul": "NH4H2PO4", "agirlik": 115.03, "tank": "B", "iyonlar": {"NH4": 1, "H2PO4": 1}}
}

# Mikro elementler
mikro_gubreler = {
    "Demir EDDHA": {"formul": "Fe-EDDHA %6", "agirlik": 435.0, "element": "Fe", "yuzde": 6},
    "Demir EDTA": {"formul": "Fe-EDTA %13", "agirlik": 346.0, "element": "Fe", "yuzde": 13},
    "Demir DTPA": {"formul": "Fe-DTPA %11", "agirlik": 468.0, "element": "Fe", "yuzde": 11},
    "Borak": {"formul": "Na2B4O7.10H2O", "agirlik": 381.37, "element": "B", "yuzde": 11},
    "Borik Asit": {"formul": "H3BO3", "agirlik": 61.83, "element": "B", "yuzde": 17.5},
    "Mangan Sulfat": {"formul": "MnSO4.H2O", "agirlik": 169.02, "element": "Mn", "yuzde": 32},
    "Cinko Sulfat": {"formul": "ZnSO4.7H2O", "agirlik": 287.56, "element": "Zn", "yuzde": 23},
    "Bakir Sulfat": {"formul": "CuSO4.5H2O", "agirlik": 249.68, "element": "Cu", "yuzde": 25},
    "Sodyum Molibdat": {"formul": "Na2MoO4.2H2O", "agirlik": 241.95, "element": "Mo", "yuzde": 40}
}

# Hazir receteler
hazir_receteler = {
    "Genel Amacli": {
        "NO3": 11.75, "H2PO4": 1.25, "SO4": 1.0,
        "NH4": 1.0, "K": 5.5, "Ca": 3.25, "Mg": 1.0,
        "Fe": 40.0, "B": 30.0, "Mn": 5.0, "Zn": 4.0, "Cu": 0.75, "Mo": 0.5
    },
    "Domates": {
        "NO3": 14.0, "H2PO4": 1.5, "SO4": 1.5,
        "NH4": 1.2, "K": 7.0, "Ca": 4.0, "Mg": 1.5,
        "Fe": 50.0, "B": 40.0, "Mn": 8.0, "Zn": 4.0, "Cu": 0.8, "Mo": 0.5
    },
    "Salatalik": {
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

# Elementin atomik kutlesi (g/mol)
element_atomik_kutle = {
    "Fe": 55.845, "B": 10.81, "Mn": 54.938, "Zn": 65.38, "Cu": 63.546, "Mo": 95.95
}

# Baslangic session state ayarlari
def initialize_session_state():
    # Recete
    if 'recete' not in st.session_state:
        st.session_state.recete = {
            "NO3": 9.5, "H2PO4": 1.0, "SO4": 0.5, 
            "NH4": 0.5, "K": 5.0, "Ca": 2.25, "Mg": 0.75
        }

    # Tank ayarlari
    if 'a_tank' not in st.session_state:
        st.session_state.a_tank = 19

    if 'b_tank' not in st.session_state:
        st.session_state.b_tank = 19

    if 'konsantrasyon' not in st.session_state:
        st.session_state.konsantrasyon = 100

    # Kuyu suyu
    if 'kuyu_suyu' not in st.session_state:
        st.session_state.kuyu_suyu = {
            "NO3": 0.0, "H2PO4": 0.0, "SO4": 0.0, 
            "NH4": 0.0, "K": 0.0, "Ca": 0.0, "Mg": 0.0
        }

    # Kullanilabilir gubreler
    if 'kullanilabilir_gubreler' not in st.session_state:
        st.session_state.kullanilabilir_gubreler = {gubre: False for gubre in gubreler.keys()}

    # Kullanilabilir mikro gubreler
    if 'kullanilabilir_mikro_gubreler' not in st.session_state:
        st.session_state.kullanilabilir_mikro_gubreler = {gubre: False for gubre in mikro_gubreler.keys()}

    # Secilen mikro gubreler
    if 'secilen_mikro_gubreler' not in st.session_state:
        st.session_state.secilen_mikro_gubreler = {
            "Fe": None, "B": None, "Mn": None, "Zn": None, "Cu": None, "Mo": None
        }

    # Hesaplama logu
    if 'hesaplama_log' not in st.session_state:
        st.session_state.hesaplama_log = []

    # Hesaplama sonucu
    if 'hesaplama_sonucu' not in st.session_state:
        st.session_state.hesaplama_sonucu = None

# Iyonik denge hesaplama
def hesapla_iyonik_denge(recete):
    anyon_toplam = sum(float(recete[ion]) * abs(iyon_degerlikleri[ion]) for ion in ["NO3", "H2PO4", "SO4"])
    katyon_toplam = sum(float(recete[ion]) * abs(iyon_degerlikleri[ion]) for ion in ["NH4", "K", "Ca", "Mg"])
    return anyon_toplam, katyon_toplam

# Simulasyon ile besinlerin karsilanip karsilanamayacagini kontrol etme
def karsilanabilirlik_kontrolu(recete, secilen_gubreler):
    net_ihtiyac = {ion: max(0, float(recete[ion])) for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]}

    if "Kalsiyum Nitrat" in secilen_gubreler and net_ihtiyac["Ca"] > 0:
        net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Ca"]
        net_ihtiyac["Ca"] = 0

    if "Magnezyum Nitrat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        net_ihtiyac["NO3"] -= 2 * net_ihtiyac["Mg"]
        net_ihtiyac["Mg"] = 0
    elif "Magnezyum Sulfat" in secilen_gubreler and net_ihtiyac["Mg"] > 0:
        net_ihtiyac["SO4"] -= net_ihtiyac["Mg"]
        net_ihtiyac["Mg"] = 0

    if "Monopotasyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        net_ihtiyac["K"] -= net_ihtiyac["H2PO4"]
        net_ihtiyac["H2PO4"] = 0
    elif "Monoamonyum Fosfat" in secilen_gubreler and net_ihtiyac["H2PO4"] > 0:
        net_ihtiyac["NH4"] -= net_ihtiyac["H2PO4"]
        net_ihtiyac["H2PO4"] = 0

    if "Amonyum Sulfat" in secilen_gubreler and net_ihtiyac["NH4"] > 0:
        as_miktar = min(net_ihtiyac["NH4"] / 2, net_ihtiyac["SO4"])
        net_ihtiyac["NH4"] -= 2 * as_miktar
        net_ihtiyac["SO4"] -= as_miktar

    if "Potasyum Nitrat" in secilen_gubreler and net_ihtiyac["K"] > 0 and net_ihtiyac["NO3"] > 0:
        kn_miktar = min(net_ihtiyac["K"], net_ihtiyac["NO3"])
        net_ihtiyac["K"] -= kn_miktar
        net_ihtiyac["NO3"] -= kn_miktar

    if "Potasyum Sulfat" in secilen_gubreler and net_ihtiyac["K"] > 0:
        net_ihtiyac["SO4"] -= net_ihtiyac["K"] / 2
        net_ihtiyac["K"] = 0

    for iyon in net_ihtiyac:
        if net_ihtiyac[iyon] < 0:
            net_ihtiyac[iyon] = 0

    return [iyon for iyon, miktar in net_ihtiyac.items() if miktar > 0.1]

# Gubre hesaplama fonksiyonu
def gubre_hesapla():
    # Secilen gübreleri al
    secilen_gubreler = [gubre for gubre, secildi in st.session_state.kullanilabilir_gubreler.items() if secildi]
    secilen_mikro_gubreler = [gubre for element, gubre in st.session_state.secilen_mikro_gubreler.items() if gubre]

    # Hata ayiklama logu
    st.session_state.hesaplama_log = []
    st.session_state.hesaplama_log.append({
        "adim": "Baslangic", "aciklama": f"Secilen makro gubreler: {secilen_gubreler}", "ihtiyac": {}
    })

    if not secilen_gubreler:
        st.error("Lutfen 'Gubre Secimi' sekmesinden en az bir makro gubre secin!")
        st.warning(f"Hata Ayiklama: Secilen gubreler bos. Tum gubre durumu: {st.session_state.kullanilabilir_gubreler}")
        return None

    # Net ihtiyac hesaplama
    net_ihtiyac = {
        ion: max(0, float(st.session_state.recete[ion]) - float(st.session_state.kuyu_suyu[ion]))
        for ion in ["NO3", "H2PO4", "SO4", "NH4", "K", "Ca", "Mg"]
    }
    a_tank_gubreler = {}
    b_tank_gubreler = {}
    adim = 1

    st.session_state.hesaplama_log.append({
        "adim": "Kuyu Suyu Sonrasi", "aciklama": "Kuyu suyu sonrasi ihtiyaclar",
        "ihtiyac": {k: round(v, 2) for k, v in
