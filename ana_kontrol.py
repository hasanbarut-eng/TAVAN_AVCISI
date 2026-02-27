import yfinance as yf
import logging
import sys
import traceback
from ayarlar import TELEGRAM, HISSE_LISTESI
from finans_motoru import FinansMotoru
from bildirim_servisi import BildirimServisi

# Loglama Ayarları - Üretim seviyesi formatlama
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

def baslat():
    logging.info("🏭 TAVAN AVCISI ÜRETİM BANDI DEVREDE...")
    
    try:
        motor = FinansMotoru()
        servis = BildirimServisi(TELEGRAM["TOKEN"], TELEGRAM["CHAT_ID"])
    except Exception as e:
        logging.error(f"❌ Servisler başlatılamadı: {e}")
        return

    adaylar = []
    
    # Hızlı analiz için sembol listesini dönüyoruz
    for sembol in HISSE_LISTESI:
        sembol_full = f"{sembol}.IS"
        try:
            ticker = yf.Ticker(sembol_full)
            
            # yfinance'ın en stabil çalıştığı period/interval kombinasyonu
            # 30 günlük veriyi tek seferde çekiyoruz
            df = ticker.history(period="1mo", interval="1d")
            
            if df is None or df.empty or len(df) < 20:
                logging.warning(f"📉 {sembol_full} için yetersiz veri.")
                continue

            # .info kısmı takılmalara neden olabilir, opsiyonel ve timeout kontrollü
            info = {}
            try:
                # Bazı kritik veriler için info gerekebilir ama timeout riski taşır
                info = ticker.info 
            except Exception:
                logging.debug(f"ℹ️ {sembol} için info verisi alınamadı, teknik analizle devam ediliyor.")

            # Analiz Motorunu Çalıştır
            sonuc = motor.analiz_et(sembol, df, info)
            if sonuc:
                adaylar.append(sonuc)
                logging.info(f"🎯 Sinyal Yakalandı: #{sembol}")
            
        except Exception as e:
            logging.error(f"⚠️ {sembol} işlenirken hata oluştu: {str(e)}")
            continue

    # Raporlama Mantığı
    if adaylar:
        try:
            # Skorlama varsa sırala
            adaylar.sort(key=lambda x: x.get('ai_skor', 0), reverse=True)
            servis.rapor_gonder(adaylar)
            logging.info(f"✅ {len(adaylar)} aday Telegram'a iletildi.")
        except Exception as e:
            logging.error(f"❌ Rapor gönderimi sırasında hata: {e}")
    else:
        logging.info("😴 Uygun aday bulunamadı.")

if __name__ == "__main__":
    # DİKKAT: GitHub Actions cron kullandığı için 'while True' kaldırıldı.
    # Bu script bir kez çalışır, işini yapar ve kapanır. 
    # Bir sonraki tetiklemeyi GitHub yapacak.
    try:
        start_time = time.time()
        baslat()
        end_time = time.time()
        logging.info(f"⏱️ İşlem {round(end_time - start_time, 2)} saniyede tamamlandı.")
    except Exception as e:
        logging.critical(f"💥 KRİTİK SİSTEM HATASI: {traceback.format_exc()}")
        sys.exit(1)
