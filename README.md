# FRC-Scout-2026

#  FRC AI Scout  2026

👌😉 Uygulamaya Gitmek İçin Tıkla https://frc-scout-2026arda.streamlit.app/

Bu proje, FRC (First Robotics Competition) takımları için geliştirilmiş, **Google Sheets** tabanlı, gerçek zamanlı veri girişi ve **AI destekli stratejik analiz** sunan bir Scouting uygulamasıdır.

##  Özellikler
* ** Match Scout:** Maç verilerini (otonom, teleop, tırmanma, arıza durumu vb.) anlık olarak kaydeder.
* ** Pit Scout:** Robotların teknik özelliklerini ve fotoğraflarını dijital ortama aktarır.
* ** Stratejik AI Analiz:** Toplanan verileri işleyerek takımların "Güç Skorlarını" hesaplar ve ittifak seçimi için en uygun partnerleri önerir.
* ** Veri Görselleştirme:** Takım performanslarını grafikler ve ısı haritaları ile sunar.

##  Teknoloji Yığını
* **Dil:** Python
* **Arayüz:** Streamlit
* **Veritabanı:** Google Sheets API
* **Kütüphaneler:** Pandas, Plotly, Gspread, Matplotlib

##  Kurulum ve Dağıtım
Bu uygulama **Streamlit Cloud** üzerinde yayına alınmak üzere optimize edilmiştir.

1.  Gereksinimleri yükleyin: `pip install -r requirements.txt`
2.  Google Cloud Console üzerinden bir Service Account oluşturun.
3.  Streamlit "Secrets" panelinde API anahtarlarınızı yapılandırın.
4.  Uygulamayı başlatın: `streamlit run frcscout.py`

##  Güvenlik
Bu proje **.gitignore** dosyası ile korunmaktadır. Hassas API anahtarları asla GitHub üzerinden paylaşılmaz; yalnızca Streamlit Cloud'un güvenli **Secrets** kasasında saklanır.

---
**Geliştiren:** Arda Efe Elgay - FRC 2026 Sezonu için sevgiyle yapıldı. 🦾
