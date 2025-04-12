import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Dil seçenekleri
dil_secenekleri = {
    "Türkçe": {
        "title": "Hidroponik Besin Çözeltisi Chatbot",
        "welcome": "Aşağıdan bitki, aşama ve drenaj EC’si girin:",
        "help_button": "Drenaj EC’si Nedir?",
        "help_text": """
        **Drenaj EC’si nedir?**  
        Drenaj EC’si, hidroponik sisteminizden çıkan suyun elektriksel iletkenliğini (tuz miktarını) ölçer.  
        - **Normal değer**: Bitkinizin hedef EC’sine yakın olmalı (örneğin, çilek için 1.6-2.1 mS/cm).  
        - **Yüksekse**: Besin dozu azaltılır (örneğin, Azot ve Potasyum %10 düşer).  
        - **Nasıl ölçülür?**: EC ölçer cihazıyla.  
        Daha fazla bilgi için ziraat uzmanına danışabilirsiniz.
        """,
        "select_plant": "Bitkiyi seçin:",
        "select_stage": "Büyüme aşamasını seçin:",
        "drain_ec": "Drenaj EC’si (mS/cm, isteğe bağlı)",
        "show_recipe": "Reçeteyi Göster",
        "error_ec": "Hatalı drenaj EC’si! Lütfen 0 ile 10 mS/cm arasında bir değer girin.",
        "warning_ec": "Uyarı: Drenaj EC’si yüksek, Azot ve Potasyum %10 azaltıldı.",
        "recipe_title": "{} ({}) reçetesi:",
        "download": "Reçeteyi PDF Olarak İndir",
        "login_title": "Giriş Yap",
        "username": "Kullanıcı Adı",
        "password": "Şifre",
        "login_button": "Giriş",
        "login_error": "Hatalı kullanıcı adı veya şifre!"
    },
    "English": {
        "title": "Hydroponic Nutrient Solution Chatbot",
        "welcome": "Select plant, stage, and drainage EC below:",
        "help_button": "What is Drainage EC?",
        "help_text": """
        **What is Drainage EC?**  
        Drainage EC measures the electrical conductivity (salt content) of water exiting your hydroponic system.  
        - **Normal value**: Should be close to your plant’s target EC (e.g., 1.6-2.1 mS/cm for strawberries).  
        - **If high**: Nutrient dose is reduced (e.g., Nitrogen and Potassium decreased by 10%).  
        - **How to measure?**: Use an EC meter.  
        Consult an agricultural expert for more information.
        """,
        "select_plant": "Select plant:",
        "select_stage": "Select growth stage:",
        "drain_ec": "Drainage EC (mS/cm, optional)",
        "show_recipe": "Show Recipe",
        "error_ec": "Invalid drainage EC! Please enter a value between 0 and 10 mS/cm.",
        "warning_ec": "Warning: Drainage EC is high, Nitrogen and Potassium reduced by 10%.",
        "recipe_title": "{} ({}) recipe:",
        "download": "Download Recipe as PDF",
        "login_title": "Log In",
        "username": "Username",
        "password": "Password",
        "login_button": "Log In",
        "login_error": "Invalid username or password!"
    }
}

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
biber_meyve = {
    "Azot": 150,
    "Fosfor": 50,
    "Potasyum": 200,
    "Kalsiyum": 120,
    "Magnezyum": 40,
    "EC": 2.0,
    "pH": 6.0
}
besin_veritabani = {
    "çilek": {"vejetatif": cilek_vejetatif, "meyve": cilek_meyve},
    "marul": {"üretim": marul_uretim},
    "domates": {"çiçeklenme": domates_ciceklenme, "meyve": domates_meyve},
    "biber": {"meyve": biber_meyve}
}

# Stil ekleme
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    h1 {
        color: #2e7d32;
        text-align: center;
    }
    .stButton>button {
        background-color: #4caf50;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Dil seçimi
dil = st.sidebar.selectbox("Dil / Language:", ["Türkçe", "English"])
metin = dil_secenekleri[dil]

# Erişim kontrolü
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title(metin["login_title"])
    username = st.text_input(metin["username"])
    password = st.text_input(metin["password"], type="password")
    if st.button(metin["login_button"]):
        if username == "tarimci" and password == "bitki2025":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error(metin["login_error"])
else:
    st.title(metin["title"])
    st.write(metin["welcome"])

    # Yardım butonu
    if st.button(metin["help_button"]):
        st.write(metin["help_text"])

    # Kullanıcıdan seçim al
    bitki = st.selectbox(metin["select_plant"], list(besin_veritabani.keys()))
    asama = st.selectbox(metin["select_stage"], list(besin_veritabani[bitki].keys()))
    drain_ec = st.number_input(metin["drain_ec"], min_value=0.0, step=0.1, value=0.0)

    # Reçeteyi hesapla
    if st.button(metin["show_recipe"]):
        # Hata kontrolü
        if drain_ec < 0 or drain_ec > 10:
            st.error(metin["error_ec"])
        else:
            recete = besin_veritabani[bitki][asama].copy()
            birim = "mmol/L" if bitki == "çilek" else "ppm"
            uyar = ""
            if drain_ec > recete["EC"] + 0.5:
                recete["Azot"] *= 0.9
                recete["Potasyum"] *= 0.9
                uyar = metin["warning_ec"]
            
            # Tablo oluştur
            tablo_veri = {
                "Besin": ["Azot", "Fosfor", "Potasyum", "Kalsiyum", "Magnezyum", "EC", "pH"],
                "Değer": [
                    f"{recete['Azot']} {birim}",
                    f"{recete['Fosfor']} {birim}",
                    f"{recete['Potasyum']} {birim}",
                    f"{recete['Kalsiyum']} {birim}",
                    f"{recete['Magnezyum']} {birim}",
                    f"{recete['EC']} mS/cm",
                    f"{recete['pH']}"
                ]
            }
            df = pd.DataFrame(tablo_veri)
            st.write(f"**{metin['recipe_title'].format(bitki.capitalize(), asama)}**")
            if uyar:
                st.write(f"**{uyar}**")
            st.table(df)

            # PDF oluşturma
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.drawString(100, 750, f"{bitki.capitalize()} ({asama})")
            y = 700
            for besin, deger in zip(tablo_veri["Besin"], tablo_veri["Değer"]):
                c.drawString(100, y, f"{besin}: {deger}")
                y -= 20
            c.showPage()
            c.save()
            buffer.seek(0)
            st.download_button(
                label=metin["download"],
                data=buffer,
                file_name=f"{bitki}_{asama}_recipe.pdf",
                mime="application/pdf",
                key="download_button"
            )
