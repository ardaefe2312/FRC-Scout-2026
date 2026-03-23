# FRC-Scout-2026

#  FRC AI Scout  2026

UYGULAMAYA GİTMEK İÇİN🏹🏹
https://frc-scout-2026arda.streamlit.app/

📌 Proje Hakkında
FRC AI Scout Pro, FIRST Robotics Competition (FRC) 2026 Decode sezonuna özel geliştirilmiş bir scouting ve stratejik analiz platformudur. Turnuva sırasında sahada toplanan maç ve pit verilerini anlık olarak kaydeder; özel bir Güç Skoru algoritması ve yapay zeka ile ittifak seçimi için en uygun takımları önerir.

Bu proje Future Talent Program 201 — Yapay Zeka Bitirme Projesi kapsamında geliştirilmiştir.


✨ Özellikler
📥 Match Scout

Takım no, maç no, otonom puanı, teleop puanı girişi
Tırmanma durumu seçimi (Park / Basamak 1-2-3)
Arıza ve savunma durumu takibi
Veriler Google Sheets'e anlık kaydedilir

🛠️ Pit Scout

Robotun ittifak rolü, şasi tipi, motor seçimi
Otonom odak ve savunma potansiyeli değerlendirmesi
Kayıtlı pit verilerini tablo olarak görüntüleme

🤖 Stratejik AI Analiz

Özel Güç Skoru algoritması:

  Güç Skoru = (Otonom × 2.5) + (Teleop × 1.2) + (Tırmanma × 1.5) − (Arıza × 10)

Groq / LLaMA 3.1 destekli doğal dil stratejik raporu
En iyi 3 takım otomatik önerilir
AI çalışmasa bile sayısal analiz aktif kalır (graceful degradation)

📊 Veri Görselleştirme

Plotly ile interaktif bar grafikleri
Güç Skoruna göre renk gradyanlı sıralama tablosu


🛠️ Teknoloji Yığını
KatmanTeknolojiDilPython 3.10+ArayüzStreamlitVeritabanıGoogle Sheets API (gspread)Yapay ZekaGroq API — LLaMA 3.1 8B InstantGörselleştirmePlotly ExpressVeri İşlemePandasKimlik DoğrulamaGoogle Service Account (oauth2client)DeployStreamlit Cloud

🚀 Kurulum
1. Repoyu klonla
bashgit clone https://github.com/ardaefe2312/FRC-Scout-2026.git
cd FRC-Scout-2026
2. Bağımlılıkları yükle
bashpip install -r requirements.txt
3. Google Cloud ayarları

Google Cloud Console'dan bir Service Account oluştur
Google Sheets API ve Google Drive API'yi etkinleştir
JSON anahtar dosyasını anahtar.json olarak kaydet
Sheets dosyasını Service Account e-postasıyla paylaş

4. Groq API Key

console.groq.com üzerinden ücretsiz API anahtarı al

5. Uygulamayı başlat
bashstreamlit run frcscout.py

☁️ Streamlit Cloud Deploy
Secrets paneline şu değerleri ekle:
tomlgroq_api_key = "gsk_..."

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."

🔒 Güvenlik

.gitignore ile tüm hassas dosyalar Git'ten hariç tutulmuştur
API anahtarları yalnızca Streamlit Cloud'un şifreli Secrets kasasında saklanır
Servis hesabı yetkileri yalnızca ilgili Sheets dosyasıyla sınırlıdır


📁 Dosya Yapısı
FRC-Scout-2026/
├── frcscout.py          # Ana uygulama
├── requirements.txt     # Bağımlılıklar
├── .gitignore           # Hassas dosya koruması
└── README.md            # Bu dosya

👤 Geliştiren
Arda Efe Elgay
FRC 2026 Decode Sezonu için sevgiyle yapıldı. 💜👽
