import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from oauth2client.service_account import ServiceAccountCredentials
import os

# --- 1. BAĞLANTI AYARLARI ---
@st.cache_resource
def get_connections():
    if "gcp_service_account" in st.secrets:
        creds_info = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, [
            "https://spreadsheets.google.com/feeds", 
            'https://www.googleapis.com/auth/drive'
        ])
    else:
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('anahtar.json', scope)
    
    client = gspread.authorize(creds)
    spreadsheet = client.open("FRC scout")
    return spreadsheet

doc = get_connections()

if doc:
    sheet1 = doc.sheet1 # Maç Verileri
    try:
        sheet2 = doc.worksheet("Sheet2") # Pit Verileri
    except:
        st.error("Hata: Google Sheets'te 'Sheet2' sayfası bulunamadı! Lütfen oluşturun.")

# --- 2. SAYFA AYARLARI ---
st.set_page_config(page_title="FRC AI Scout Pro 2026", layout="wide")
tab1, tab2, tab3 = st.tabs(["📥 Match Scout", "🛠️ Pit Scout", "🤖 Stratejik AI Analiz"])

# --- TAB 1: MATCH SCOUT (MAÇ VERİSİ) ---
with tab1:
    st.title("🕹️ Maç Veri Girişi")
    c1, c2 = st.columns(2)
    with c1:
        t_no = st.number_input("Takım No", min_value=1, step=1, key="m_tno")
        auto_p = st.number_input("Otonom Puanı (FUEL + Hareket)", min_value=0, step=1)
    with c2:
        m_no = st.number_input("Maç No", min_value=1, step=1, key="m_no")
        tele_p = st.number_input("Teleop Puanı (FUEL)", min_value=0, step=1)
    
    st.divider()
    c3, c4 = st.columns(2)
    with c3:
        # 2026 REBUILT Tırmanma Seviyeleri ve Puan Karşılıkları
        climb_status = st.selectbox("Tırmanma (Endgame)", 
                                    ["Yok", "Park Edildi (2 Puan)", "Basamak 1 (6 Puan)", "Basamak 2 (12 Puan)", "Basamak 3 (20 Puan)"])
    with c4:
        broken = st.checkbox("🛑 Robot Arıza Yaptı")
        defense = st.checkbox("🛡️ Çok İyi Savunma Yaptı")

    if st.button("MAÇ VERİSİNİ KAYDET", type="primary", use_container_width=True):
        sheet1.append_row([t_no, m_no, auto_p, tele_p, climb_status, str(broken), str(defense)])
        st.success(f"✅ Takım {t_no} - Maç {m_no} kaydedildi!")

#  TAB 2: PIT SCOUT (TEKNİK DETAYLAR & İTTİFAK SEÇİMİ)
with tab2:
    st.title("🛠️ Pit Scouting & İttifak Yönetimi")
    col_f1, col_f2 = st.columns([1, 1.5])
    
    with col_f1:
        st.subheader("📝 Teknik Özellikler")
        pit_tno = st.number_input("Takım No", min_value=1, step=1, key="pit_tno")
        
        alliance_role = st.radio(
            "🤝 Robotun İttifak Rolü",
            ["Rakip / Diğer", "1. Ana Robot (Biz)", "2. Partner Robot", "3. Partner Robot"],
            help="İşbirliği yaptığınız takımları buradan işaretleyebilirsiniz."
        )
        
        robot_type = st.radio("Robot Tipi", ["Özel Tasarım (Custom)", "Kitbot"], horizontal=True)
        weight = st.number_input("Robot Ağırlığı (kg)", min_value=0.0, step=0.1)
        dimensions = st.text_input("Robot Boyutları (Örn: 75x75x60 cm)")
        drive_train = st.selectbox("Şasi Tipi", ["Swerve", "Tank", "Mecanum", "Diğer"])
        motor_choice = st.multiselect("Kullanılan Motorlar", ["Kraken", "NEO", "Falcon 500", "CIM", "Vortex"])
        uploaded_file = st.file_uploader("Robot Fotoğrafı", type=["jpg", "png", "jpeg"])
        
        if st.button("PİT VERİLERİNİ KAYDET", use_container_width=True, type="primary"):
            motor_str = ", ".join(motor_choice)
            sheet2.append_row([pit_tno, alliance_role, robot_type, weight, dimensions, drive_train, motor_str])
            
            if uploaded_file:
                if not os.path.exists("robot_fotolari"): os.makedirs("robot_fotolari")
                with open(f"robot_fotolari/Takim_{pit_tno}.jpg", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.info("📸 Fotoğraf kaydedildi.")
            
            st.success(f"✅ Takım {pit_tno} ({alliance_role}) kaydedildi!")

    with col_f2:
        st.subheader("📋 Kayıtlı Pit Verileri")
        if st.button("Verileri Yenile"):
            data_pit = sheet2.get_all_records()
            if data_pit:
                st.dataframe(pd.DataFrame(data_pit), use_container_width=True)
            else:
                st.info("Henüz teknik veri girilmemiş.")

# --- TAB 3: AKILLI BİREYSEL & İTTİFAK ANALİZİ ---
with tab3:
    st.title("🤖 2026 REBUILT Strateji Motoru")
    if st.button("📊 Tüm Robotları ve İttifakı Analiz Et", use_container_width=True):
        match_data = sheet1.get_all_records()
        pit_data = sheet2.get_all_records()
        
        if match_data and pit_data:
            df = pd.DataFrame(match_data)
            pdf = pd.DataFrame(pit_data)
            
            # 2026 Manuel Puanlama Eşleşmesi
            c_map = {
                "Yok": 0, 
                "Park Edildi (2 Puan)": 2, 
                "Basamak 1 (6 Puan)": 6, 
                "Basamak 2 (12 Puan)": 12, 
                "Basamak 3 (20 Puan)": 20
            }
            df['Climb_Score'] = df['Tırmanma'].map(c_map).fillna(0)
            df['Is_Broken'] = df.iloc[:, 5].apply(lambda x: 1 if str(x).lower() == 'true' else 0)

            # Genel Analiz Tablosu
            analiz_df = df.groupby('Takım No').agg({
                'Otonom Puanı': 'mean', 'Teleop Puanı': 'mean', 'Climb_Score': 'mean', 'Is_Broken': 'sum'
            })
            
            # 2026 REBUILT KATSAYI GÜNCELLEMESİ:
            # Otonom (x2.5), Teleop (x1.2), Climb (x1.5) - Arıza Cezası (-10)
            analiz_df['Güç_Skoru'] = (analiz_df['Otonom Puanı'] * 2.5) + \
                                     (analiz_df['Teleop Puanı'] * 1.2) + \
                                     (analiz_df['Climb_Score'] * 1.5) - \
                                     (analiz_df['Is_Broken'] * 10)
            
            analiz_df = analiz_df.sort_values('Güç_Skoru', ascending=False)

            ittifak_robotları = pdf[pdf.iloc[:, 1].str.contains("Robot", na=False)]
            itt_nolar = ittifak_robotları.iloc[:, 0].values.tolist()

            if not ittifak_robotları.empty:
                st.subheader("🛡️ Partner Bazlı Özel Analizler")
                
                for index, row in ittifak_robotları.iterrows():
                    t_no_itt = row.iloc[0]
                    t_rol = row.iloc[1]
                    
                    with st.expander(f"📊 {t_rol} (Takım {t_no_itt}) Analizi", expanded=True):
                        if t_no_itt in analiz_df.index:
                            rb_puan = analiz_df.loc[t_no_itt]
                            
                            m1, m2, m3, m4 = st.columns(4)
                            m1.metric("Güç Skoru", f"{rb_puan['Güç_Skoru']:.1f}")
                            m2.write(f"**Oto. Ort:** {rb_puan['Otonom Puanı']:.1f}")
                            m3.write(f"**Tele. Ort:** {rb_puan['Teleop Puanı']:.1f}")
                            m4.write(f"**Climb Ort:** {rb_puan['Climb_Score']:.1f}")

                            # En zayıf alan tespiti
                            alanlar = {'Otonom Puanı': rb_puan['Otonom Puanı'], 
                                      'Teleop Puanı': rb_puan['Teleop Puanı'], 
                                      'Climb_Score': rb_puan['Climb_Score']}
                            en_zayif_alan = min(alanlar, key=alanlar.get)
                            alan_isim = {"Otonom Puanı": "Otonom", "Teleop Puanı": "Teleop", "Climb_Score": "Tırmanma"}

                            adaylar = analiz_df[~analiz_df.index.isin(itt_nolar)]
                            en_iyi_partnerler = adaylar.sort_values(en_zayif_alan, ascending=False).head(2)

                            st.divider()
                            st.write(f"🎯 **Stratejik İhtiyaç:** Bu robot için en iyi partner **{alan_isim[en_zayif_alan]}** uzmanı olmalı.")
                            
                            c_p1, c_p2 = st.columns(2)
                            c_p1.success(f"🥇 Önerilen: Takım {en_iyi_partnerler.index[0]}")
                            c_p2.success(f"🥈 Yedek: Takım {en_iyi_partnerler.index[1]}")
                        else:
                            st.warning(f"Takım {t_no_itt} verisi henüz girilmedi.")
            else:
                st.info("Pit Scout sekmesinden partnerlerinizi işaretleyin.")

            st.divider()
            st.subheader("📊 2026 Turnuva Performans Grafiği")
            fig = px.bar(analiz_df.reset_index(), x='Takım No', y='Güç_Skoru', 
                         color='Güç_Skoru', color_continuous_scale='Plasma')
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(analiz_df.style.background_gradient(subset=['Güç_Skoru'], cmap='RdYlGn'), use_container_width=True)
        else:
            st.warning("Veri bekleniyor...")
