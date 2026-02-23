import yfinance as yf
import logging
import time
from ayarlar import TELEGRAM, HISSE_LISTESI
from finans_motoru import FinansMotoru
from bildirim_servisi import BildirimServisi

# Loglama Ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def baslat():
    logging.info("🏭 TAVAN AVCISI ÜRETİM BANDI DEVREDE...")
    motor = FinansMotoru()
    servis = BildirimServisi(TELEGRAM["TOKEN"], TELEGRAM["CHAT_ID"])
    
    adaylar = []
    for sembol in HISSE_LISTESI:
        try:
            ticker = yf.Ticker(f"{sembol}.IS")
            # 15 dakikalık iştahı yakalamak için son 30 günlük günlük veriyi alıyoruz
            df = ticker.history(period="30d", interval="1d")
            
            if df is None or df.empty or len(df) < 25:
                continue

            try:
                info = ticker.info
            except:
                info = {}

            # Analiz Motorunu Çalıştır
            sonuc = motor.analiz_et(sembol, df, info)
            if sonuc:
                adaylar.append(sonuc)
                logging.info(f"🎯 Sinyal Yakalandı: #{sembol}")
            
            time.sleep(0.1) # API limit koruması
        except Exception as e:
            logging.warning(f"⚠️ {sembol} atlandı: {e}")
            continue

    if adaylar:
        # Puanı en yüksek olanları öne çıkar
        adaylar.sort(key=lambda x: x['ai_skor'], reverse=True)
        servis.rapor_gonder(adaylar)
        logging.info(f"✅ {len(adaylar)} aday Telegram'a mühürlendi.")
    else:
        logging.info("😴 Uygun aday bulunamadı.")

if __name__ == "__main__":
    while True:
        baslat()
        # Bir sonraki tarama için 15 dakika (900 saniye) bekle
        logging.info("⏳ 15 dakika sonraki tarama bekleniyor...")
        time.sleep(900)
