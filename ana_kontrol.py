import time
import sys
import logging
import traceback
import signal
from datetime import datetime

# --- SENIOR LOGGING CONFIGURATION ---
# Loglar hem dosyaya hem de GitHub Actions konsoluna (stdout) yazılır.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("robot_execution.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class RobotAtesleyici:
    """
    Tavan Avcısı Robotu'nun ana yönetim sınıfı.
    Sinyal yönetimi ve hata yakalama blokları ile donatılmıştır.
    """
    def __init__(self):
        self.execution_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = 0
        self.is_active = True
        
        # Graceful Shutdown (Sistemi kibarca kapatma) için sinyal yakalayıcılar
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)

    def _handle_exit(self, signum, frame):
        logger.warning(f"Sistemden çıkış sinyali alındı (Signal: {signum}). Temizlik yapılıyor...")
        self.is_active = False

    def baglantilari_dogrula(self) -> bool:
        """
        Robot ateşlenmeden önce tüm dış bağlantıları (API, DB, Internet) kontrol eder.
        """
        try:
            logger.info(f"[{self.execution_id}] Sistem kontrolleri yapılıyor...")
            # Buraya API anahtarı kontrolü veya veri kaynağı testi gelecek.
            # Örnek: if not check_internet(): raise ConnectionError("İnternet yok!")
            return True
        except Exception as e:
            logger.error(f"Kritik Bağlantı Hatası: {str(e)}")
            return False

    def robotu_baslat(self):
        """
        Görseldeki 77. satır ve devamındaki mantığı yöneten ana metod.
        """
        if not self.baglantilari_dogrula():
            logger.critical("Sistem doğrulaması başarısız. Ateşleme iptal edildi.")
            sys.exit(1)

        try:
            # --- HATANIN OLDUĞU KRİTİK BÖLGE ---
            self.start_time = time.time()  # Artık 'time' tanımlı
            logger.info("🚀 Robot Ateşlendi! Analiz süreci başlıyor...")

            while self.is_active:
                # Ana iş mantığınızı burada bir try-except içine alın
                try:
                    self._analiz_dongusu()
                    
                    # Robotun sürekli çalışması yerine GitHub Actions'ta bir tur atıp 
                    # çıkmasını istiyorsan döngüyü burada kırabilirsin.
                    break 

                except Exception as loop_error:
                    logger.error(f"Döngü içerisinde hata oluştu: {loop_error}")
                    time.sleep(5)  # Hata durumunda sistemi yormamak için bekle ve tekrar dene
                    continue

            total_duration = time.time() - self.start_time
            logger.info(f"✅ Analiz başarıyla tamamlandı. Toplam çalışma süresi: {total_duration:.4f} saniye.")

        except Exception as e:
            logger.critical("!!! KRİTİK SİSTEM HATASI: Robot durduruldu !!!")
            logger.error(f"Hata Detayı: {str(e)}")
            logger.error(f"Traceback: \n{traceback.format_exc()}")
            sys.exit(1)

    def _analiz_dongusu(self):
        """
        Asıl veri çekme ve işlem yapma mantığının bulunduğu alt metod.
        """
        logger.info("Piyasa verileri taranıyor...")
        # Örnek İşlem:
        # data = fetch_market_data()
        # if data['tavan_olasiligi'] > 0.8: execute_trade()
        time.sleep(2) # İşlem simülasyonu
        logger.info("Tarama sonuçları işlendi.")

    def kapat(self):
        """Kaynakları temizler ve güvenli kapanış sağlar."""
        logger.info("Robot güvenli modda kapatıldı.")

# --- ANA ÇALIŞTIRMA ---
if __name__ == "__main__":
    robot = RobotAtesleyici()
    try:
        robot.robotu_baslat()
    finally:
        robot.kapat()
