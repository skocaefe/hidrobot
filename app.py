import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

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

    # Yardım butonu
    if st.button("Drenaj EC’si Nedir?"):
        st.write("""
        **Drenaj EC’si nedir?**  
        Drenaj EC’si, hidroponik sisteminizden çıkan suyun elektriksel iletkenliğini (tuz miktarını) ölçer.  
        - **Normal değer**: Bitkinizin hedef EC’sine yakın olmalı (örneğin, çilek için 1.6-2.1 mS/cm).  
        - **Yüksekse**: Besin dozu azaltılır (örneğin, Azot ve Potasyum %10 düşer).  
        - **Nasıl ölçülür?**: EC ölçer cihazıyla.  
        Daha fazla bilgi için ziraat uzmanına danışabilirsiniz.
        """)

    # Kullanıcıdan seçim al
    bitki = st.selectbox("Bitkiyi seçin:", list(besin_veritabani.keys()))
    asama = st.selectbox("Büyüme aşamasını seçin:", list(besin_veritabani[bitki].keys()))
    drain_ec = st.number_input("Drenaj EC’si (mS/cm, isteğe bağlı)", min_value=0.0, step=0.1, value=0.0)

    # Reçeteyi hesapla
    if st.button("Reçeteyi Göster"):
        # Hata kontrolü
        if drain_ec < 0 or drain_ec > 10:
            st.error("Hatalı drenaj EC’si! Lütfen 0 ile 10 mS/cm arasında bir değer girin.")
        else:
            recete = besin_veritabani[bitki][asama].copy()
            birim = "mmol/L" if bitki == "çilek" else "ppm"
            if drain_ec > recete["EC"] + 0.5:
                recete["Azot"] *= 0.9
                recete["Potasyum"] *= 0.9
                st.write("**Uyarı**: Drenaj EC’si yüksek, Azot ve Potasyum %10 azaltıldı.")
            
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
            st.write(f"**{bitki.capitalize()} ({asama}) reçetesi:**")
            st.table(df)

            # PDF oluştur
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.drawString(100, 750, f"{bitki.capitalize()} ({asama}) Reçetesi")
            y = 700
            for besin, deger in zip(tablo_veri["Besin"], tablo_veri["Değer"]):
                c.drawString(100, y, f"{besin}: {deger}")
                y -= 20
            c.showPage()
            c.save()
            buffer.seek(0)
            st.download_button(
                label="Reçeteyi PDF Olarak İndir",
                data=buffer,
                file_name=f"{bitki}_{asama}_recete.pdf",
                mime="application/pdf"
            )
