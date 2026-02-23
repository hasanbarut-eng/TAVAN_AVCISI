import pandas as pd
import numpy as np
import pandas_ta as ta
import logging

class FinansMotoru:
    def __init__(self):
        # Stratejik Sınırlar
        self.pddd_limit = 8.0          # Defter değeri üst sınırı
        self.hacim_z_skor_esigi = 2.5  # Olağan dışı para girişi onayı

    def analiz_et(self, sembol, df, info):
        """
        Ücretsiz verileri türev ve istatistikle işleyerek tavan potansiyelini ölçer.
        """
        try:
            if df is None or len(df) < 50:
                return None
            
            # --- VERİ HAZIRLIĞI ---
            kapanis = float(df['Close'].iloc[-1])
            dun_kapanis = float(df['Close'].iloc[-2])
            acilis = float(df['Open'].iloc[-1])
            gunluk_degisim = ((kapanis / dun_kapanis) - 1) * 100
            
            pddd = float(info.get('priceToBook', 0)) if info.get('priceToBook') else 0.0

            # 🛡️ GİRİŞ DİSİPLİNİ: Tavan olmuş kağıdı alma, iştahı yeni başlayanı yakala
            if gunluk_degisim > 7.5 or gunluk_degisim < 1.5:
                return None

            # --- KATMAN 1: HACİM Z-SKOR ANALİZİ (Para Girişi) ---
            h_seri = df['Volume'].tail(20)
            h_std = h_seri.std()
            z_score = (df['Volume'].iloc[-1] - h_seri.mean()) / h_std if h_std > 0 else 0
            
            # --- KATMAN 2: ORTALAMALAR VE GOLDEN CROSS ---
            ema50 = ta.ema(df['Close'], length=50).iloc[-1]
            ema200 = ta.ema(df['Close'], length=200).iloc[-1]
            golden_cross = ema50 > ema200
            rsi = ta.rsi(df['Close'], length=14).iloc[-1]

            # --- KATMAN 3: STRATEJİK SEVİYELER (Pivot) ---
            l_h, l_l, l_c = float(df['High'].iloc[-2]), float(df['Low'].iloc[-2]), float(df['Close'].iloc[-2])
            pivot = (l_h + l_l + l_c) / 3
            res1 = (2 * pivot) - l_l  # İlk Hedef
            sup1 = (2 * pivot) - l_h  # Zarar Kes (Stop)

            # --- PUANLAMA MANTIĞI ---
            puan = 0
            if z_score > self.hacim_z_skor_esigi: puan += 50 # Hacim patlaması en önemli kriter
            if golden_cross: puan += 20                      # Uzun vadeli trend desteği
            if kapanis > pivot: puan += 20                   # Fiyatın direnci aşma isteği
            if 50 <= rsi <= 78: puan += 10                   # Momentumun sağlıklı olması

            if puan >= 70 and pddd <= self.pddd_limit:
                # Seri potansiyeli; hem hacim hem de büyük trend desteği varsa yüksektir.
                seri_notu = "YÜKSEK 🌟" if golden_cross and z_score > 3 else "Normal"
                
                # EĞİTİCİ ANALİZ NOTU (Sıradan insan dili)
                analiz_metni = (
                    f"#{sembol} hissesinde normalin {round(z_score,1)} katı bir para girişi (iştah) var. "
                    f"Fiyat {round(pivot,2)} seviyesindeki barajın üzerinde kalarak gücünü kanıtladı. "
                    f"Ortalamaların dizilimi (50/200 EMA) bu hareketin kalıcı bir seriye dönüşebileceğini gösteriyor."
                )

                return {
                    "sembol": sembol, "fiyat": round(kapanis, 2), "degisim": round(gunluk_degisim, 2),
                    "ai_skor": puan, "pddd": round(pddd, 2), "destek": round(sup1, 2), 
                    "direnc": round(res1, 2), "analiz": analiz_metni, "seri": seri_notu
                }
            
            return None
        except Exception as e:
            logging.error(f"⚠️ {sembol} analizi sırasında hata: {e}")
            return None
