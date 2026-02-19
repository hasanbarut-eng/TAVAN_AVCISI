import yfinance as yf
import logging
from ayarlar import TELEGRAM, HISSE_LISTESI
from finans_motoru import FinansMotoru
from bildirim_servisi import BildirimServisi

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def baslat():
    logging.info("⚡ Tavan Avcısı Robotu İşleme Başladı...")
    motor = FinansMotoru()
    servis = BildirimServisi(TELEGRAM["TOKEN"], TELEGRAM["CHAT_ID"])
    adaylar, riskler = [], []
    
    for s in HISSE_LISTESI:
        try:
            ticker = yf.Ticker(f"{s}.IS")
            df = ticker.history(period="5d", interval="1d")
            if df.empty or len(df) < 2: continue
            
            res = motor.analiz_et(s, df, ticker.info)
            if res:
                if res.get("durum") == "TEHLIKE": riskler.append(res)
                else: adaylar.append(res)
        except Exception: continue

    servis.rapor_gonder(adaylar, riskler)
    logging.info(f"✅ İşlem tamamlandı. {len(adaylar)} aday raporlandı.")

if __name__ == "__main__":
    baslat()