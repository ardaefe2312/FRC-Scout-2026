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
st.set_page_config(page_title="FRC AI Scout Pro", layout="wide")
tab1, tab2, tab3 = st.tabs(["📥 Match Scout", "🛠️ Pit Scout", "🤖 Stratejik AI Analiz"])

# --- TAB 1: MATCH SCOUT (MAÇ VERİSİ) ---
with tab1:
    st.title("🕹️ Maç Veri Girişi")
    c1, c2 = st.columns(2)
    with c1:
        t_no = st.number_input("Takım No", min_value=1, step=1, key="m_tno")
        auto_p = st.number_input("Otonom Puanı", min_value=0, step=1)
    with c2:
        m_no = st.number_input("Maç No", min_value=1, step=1, key="m_no")
        tele_p = st.number_input("Teleop Puanı", min_value=0, step=1)
    
    st.divider()
    c3, c4 = st.columns(2)
    with c3:
        climb_status = st.selectbox("Tırmanma", ["Yok", "Basamak 1", "Basamak 2", "Basamak 3", "Park Edildi"])
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
        
        # --- YENİ REVİZE: İTTİFAK ROLÜ SEÇİMİ ---
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
            # Kayıt sütununda rol bilgisini saklıyoruz
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

#  TAB 3: AKILLI AI ANALİZ (İTTİFAK ODAKLI) 
with tab3:
    st.title("🤖 İttifak Odaklı Stratejik Analiz")
    if st.button("📊 İttifak Verilerini Analiz Et", use_container_width=True):
        match_data = sheet1.get_all_records()
        pit_data = sheet2.get_all_records()
        
        if match_data and pit_data:
            df = pd.DataFrame(match_data)
            pdf = pd.DataFrame(pit_data)
            
            c_map = {"Yok":0, "Park Edildi":2, "Basamak 1":5, "Basamak 2":10, "Basamak 3":15}
            df['Climb_Score'] = df['Tırmanma'].map(c_map).fillna(0)
            df['Is_Broken'] = df.iloc[:, 5].apply(lambda x: 1 if str(x).lower() == 'true' else 0)

            analiz_df = df.groupby('Takım No').agg({
                'Otonom Puanı': 'mean', 'Teleop Puanı': 'mean', 'Climb_Score': 'mean', 'Is_Broken': 'sum'
            })
            analiz_df['Güç_Skoru'] = (analiz_df['Otonom Puanı'] * 0.4) + (analiz_df['Teleop Puanı'] * 0.3) + (analiz_df['Climb_Score'] * 0.3) - (analiz_df['Is_Broken'] * 5)
            analiz_df = analiz_df.sort_values('Güç_Skoru', ascending=False)

            # --- YENİ REVİZE: İTTİFAK ROBOTLARINI FİLTRELEME ---
            ittifak_robotları = pdf[pdf.iloc[:, 1].str.contains("Robot", na=False)]
            
            if not ittifak_robotları.empty:
                st.subheader("🛡️ İttifak Grubu Analizi")
                c_itt1, c_itt2, c_itt3 = st.columns(3)
                
                # Her bir partner için analiz
                cols = [c_itt1, c_itt2, c_itt3]
                for i, row in enumerate(ittifak_robotları.itertuples()):
                    if i < 3:
                        t_no_itt = row[1]
                        t_rol = row[2]
                        if t_no_itt in analiz_df.index:
                            puan = analiz_df.loc[t_no_itt, 'Güç_Skoru']
                            cols[i].metric(label=f"{t_rol} (T-{t_no_itt})", value=f"{puan:.1f} Puan")
                        else:
                            cols[i].warning(f"{t_rol} (T-{t_no_itt}) henüz maça çıkmadı.")

                # İttifakın en zayıf noktasını bulma (Toplam ortalama üzerinden)
                itt_nolar = ittifak_robotları.iloc[:, 0].values
                itt_verileri = analiz_df[analiz_df.index.isin(itt_nolar)]
                
                if not itt_verileri.empty:
                    st.divider()
                    zayif_alan = itt_verileri[['Otonom Puanı', 'Teleop Puanı', 'Climb_Score']].mean().idxmin()
                    alan_tr = {"Otonom Puanı": "Otonom", "Teleop Puanı": "Teleop", "Climb_Score": "Tırmanma"}
                    
                    st.warning(f"💡 İttifakınızın genel olarak **{alan_tr[zayif_alan]}** desteğine ihtiyacı var.")
                    
                    # Bu zayıf alanı kapatacak en iyi 3 dış rakip (partner adayı)
                    adaylar = analiz_df[~analiz_df.index.isin(itt_nolar)]
                    en_iyi_destek = adaylar.sort_values(zayif_alan, ascending=False).head(3)
                    
                    st.success(f"🔍 İttifakınıza 4. partner olarak en uygun takımlar: {', '.join(map(str, en_iyi_destek.index.tolist()))}")
            else:
                st.info("İttifak partnerlerinizi belirlemek için Pit Scout sekmesinden rol seçimi yapın.")

            st.divider()
            st.subheader("📊 Genel Güç Sıralaması (Tüm Takımlar)")
            fig = px.bar(analiz_df.reset_index(), x='Takım No', y='Güç_Skoru', color='Güç_Skoru', color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(analiz_df.style.background_gradient(subset=['Güç_Skoru'], cmap='RdYlGn'), use_container_width=True)
        else:
            st.warning("Analiz için veri yetersiz.")
