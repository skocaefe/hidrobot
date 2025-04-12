import streamlit as st

# Reçeteler
cilek_vejetatif = {
    "Azot": 9,
    "Fosfor": 1,
    "Potasyum": 5.5,
    "Kalsiyum": 2.5,
    "Magnezyum": 1,
    "EC": 1.6,
    "pH": 5.8
}
cilek_meyve = {
    "Azot": 9,
    "Fosfor": 1.5,
    "Potasyum": 7.5,
    "Kalsiyum": 3.5,
    "Magnezyum": 2,
    "EC": 2.1,
    "pH": 5.8
}
marul_uretim = {
    "Azot": 150,
    "Fosfor": 40,
    "Potasyum": 200,
    "Kalsiyum": 120,
    "Magnezyum": 40,
    "EC": 1.8,
    "pH": 5.8
}
domates_ciceklenme = {
    "Azot": 170,
    "Fosfor": 50,
    "Potasyum": 250,
    "Kalsiyum": 140,
    "Magnezyum": 40,
    "EC": 2.3,
    "pH": 6.0
}
domates_meyve = {
    "Azot": 190,
    "Fosfor": 50,
    "Potasyum": 300,
    "Kalsiyum": 150,
    "Magnezyum": 50,
    "EC": 2.5,
    "pH": 6.0
}
besin_veritabani = {
    "çilek": {"vejetatif": cilek_vejetatif, "meyve": cilek_meyve},
    "marul": {"üretim": marul_uretim},
    "domates": {"çiçeklenme": domates_ciceklenme, "meyve": domates_meyve}
}

# Erişim kontrolü
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Giriş Yap")
    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        if username == "hidrobot" and password == "sifre123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Hatalı kullanıcı adı veya şifre!")
else:
    st.title("Hidroponik Besin Çözeltisi Chatbot")
    st.write("Aşağıdan bitki, aşama ve drenaj EC’si girin:")

    # Kullanıcıdan seçim al
    bitki = st.selectbox("Bitkiyi seçin:", list(besin_veritabani.keys()))
    asama = st.selectbox("Büyüme aşamasını seçin:", list(besin_veritabani[bitki].keys()))
    drain_ec = st.number_input("Drenaj EC’si (mS/cm, isteğe bağlı)", min_value=0.0, step=0.1, value=0.0)

    # Reçeteyi hesapla
    if st.button("Reçeteyi Göster"):
        recete = besin_veritabani[bitki][asama].copy()
        birim = "mmol/L" if bitki == "çilek" else "ppm"
        if drain_ec > recete["EC"] + 0.5:
            recete["Azot"] *= 0.9
            recete["Potasyum"] *= 0.9
            st.write("**Uyarı**: Drenaj EC’si yüksek, Azot ve Potasyum %10 azaltıldı.")
        
        st.write(f"**{bitki.capitalize()} ({asama}) reçetesi:**")
        st.write(f"Azot: {recete['Azot']} {birim}")
        st.write(f"Fosfor: {recete['Fosfor']} {birim}")
        st.write(f"Potasyum: {recete['Potasyum']} {birim}")
        st.write(f"Kalsiyum: {recete['Kalsiyum']} {birim}")
        st.write(f"Magnezyum: {recete['Magnezyum']} {birim}")
        st.write(f"EC: {recete['EC']} mS/cm")
        st.write(f"pH: {recete['pH']}")
