import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq

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
        st.error("Hata: Google Sheets'te 'Sheet2' sayfası bulunamadı!")

# --- 2. SAYFA AYARLARI ---
st.set_page_config(page_title="FRC AI Scout Pro 2026", layout="wide")
tab1, tab2, tab3 = st.tabs(["📥 Match Scout", "🛠️ Pit Scout", "🤖 Stratejik AI Analiz"])

# --- TAB 1: MATCH SCOUT (Değişmedi) ---
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
        climb_status = st.selectbox("Tırmanma (Endgame)", 
                                    ["Yok", "Park Edildi (2 Puan)", "Basamak 1 (6 Puan)", "Basamak 2 (12 Puan)", "Basamak 3 (20 Puan)"])
    with c4:
        broken = st.checkbox("🛑 Robot Arıza Yaptı")
        defense = st.checkbox("🛡️ Çok İyi Savunma Yaptı")

    if st.button("MAÇ VERİSİNİ KAYDET", type="primary", use_container_width=True):
        sheet1.append_row([t_no, m_no, auto_p, tele_p, climb_status, str(broken), str(defense)])
        st.success(f"✅ Takım {t_no} kaydedildi!")

# --- TAB 2: PIT SCOUT (Değişmedi) ---
with tab2:
    st.title("🛠️ Pit Scouting & İttifak Yönetimi")
    col_f1, col_f2 = st.columns([1, 1.5])
    with col_f1:
        st.subheader("📝 Teknik Özellikler")
        pit_tno = st.number_input("Takım No", min_value=1, step=1, key="pit_tno")
        alliance_role = st.radio("🤝 Robotun İttifak Rolü", ["Rakip / Diğer", "1. Ana Robot (Biz)", "2. Partner Robot", "3. Partner Robot"])
        capability = st.multiselect("Neler Yapabilir?", ["Aktif Hub Fuel", "Pasif Hub Fuel", "Tower Tırmanma L1", "Tower Tırmanma L2", "Tower Tırmanma L3"])
        auto_focus = st.selectbox("Otonom Odak", ["Sadece Start Line", "Start Line + Hub Fuel", "Sadece Hub Fuel"])
        defense_pot = st.slider("Savunma Potansiyeli (1-5)", 1, 5, 3)
        robot_type = st.radio("Robot Tipi", ["Özel Tasarım (Custom)", "Kitbot"], horizontal=True)
        drive_train = st.selectbox("Şasi Tipi", ["Swerve", "Tank", "Mecanum", "Diğer"])
        motor_choice = st.multiselect("Kullanılan Motorlar", ["Kraken", "NEO", "Falcon 500", "CIM", "Vortex"])
        
        if st.button("PİT VERİLERİNİ KAYDET", use_container_width=True, type="primary"):
            motor_str = ", ".join(motor_choice)
            cap_str = ", ".join(capability)
            sheet2.append_row([pit_tno, alliance_role, cap_str, auto_focus, defense_pot, robot_type, drive_train, motor_str])
            st.success(f"✅ Takım {pit_tno} kaydedildi!")

    with col_f2:
        st.subheader("📋 Kayıtlı Pit Verileri")
        if st.button("Verileri Yenile"):
            data_pit = sheet2.get_all_records()
            if data_pit: st.dataframe(pd.DataFrame(data_pit), use_container_width=True)

# --- TAB 3: AKILLI ANALİZ & AI ---
with tab3:
    st.title("🤖 2026 REBUILT Strateji Motoru")
    if st.button("📊 Tüm Robotları ve İttifakı Analiz Et", use_container_width=True):
        match_data = sheet1.get_all_records()
        pit_data = sheet2.get_all_records()
        
        if match_data and pit_data:
            df = pd.DataFrame(match_data)
            pdf = pd.DataFrame(pit_data)
            
            # Sayısal Analizler (Senin Orijinal Mantığın)
            c_map = {"Yok": 0, "Park Edildi (2 Puan)": 2, "Basamak 1 (6 Puan)": 6, "Basamak 2 (12 Puan)": 12, "Basamak 3 (20 Puan)": 20}
            df['Climb_Score'] = df['Tırmanma'].map(c_map).fillna(0)
            df['Is_Broken'] = df.iloc[:, 5].apply(lambda x: 1 if str(x).lower() == 'true' else 0)

            analiz_df = df.groupby('Takım No').agg({'Otonom Puanı': 'mean', 'Teleop Puanı': 'mean', 'Climb_Score': 'mean', 'Is_Broken': 'sum'})
            analiz_df['Güç_Skoru'] = (analiz_df['Otonom Puanı'] * 2.5) + (analiz_df['Teleop Puanı'] * 1.2) + (analiz_df['Climb_Score'] * 1.5) - (analiz_df['Is_Broken'] * 10)
            analiz_df = analiz_df.sort_values('Güç_Skoru', ascending=False)

            # --- AI ANALİZ (EN STABİL HALİ) ---
            st.divider()
            st.subheader("🤖 Gemini AI Stratejik Raporu")
            if "groq_api_key" in st.secrets:
    try:
        client = Groq(api_key=st.secrets["groq_api_key"])
        prompt = f"FRC Strateji Uzmanı olarak bu verileri yorumla ve ittifak öner: {analiz_df.head(5).to_string()}"
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
        )
        st.success("🤖 AI Stratejik Rapor:")
        st.info(chat.choices[0].message.content)
    except Exception as e:
        st.error(f"Hata: {e}")
```


            st.divider()
            st.subheader("📊 Turnuva Performans Grafiği")
            fig = px.bar(analiz_df.reset_index(), x='Takım No', y='Güç_Skoru', color='Güç_Skoru', color_continuous_scale='Plasma')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(analiz_df.style.background_gradient(subset=['Güç_Skoru'], cmap='RdYlGn'), use_container_width=True)
        else:
            st.warning("Veri bekleniyor...")
          
