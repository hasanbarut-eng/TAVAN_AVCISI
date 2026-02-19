import pandas as pd
import numpy as np
import pandas_ta as ta

class FinansMotoru:
    def __init__(self):
        self.pddd_limit = 2.5
        self.ani_dusus_esigi = -3.5 # Negatif haber koruması

    def analiz_et(self, sembol, df, info):
        try:
            # --- VERİ HAZIRLIĞI ---
            kapanis = float(df['Close'].iloc[-1])
            acilis = float(df['Open'].iloc[-1])
            dun_kapanis = float(df['Close'].iloc[-2])
            gunluk_degisim = ((kapanis / dun_kapanis) - 1) * 100
            
            pddd = info.get('priceToBook', 0)
            pddd = float(pddd) if (pddd and not isinstance(pddd, str)) else 0.0

            # 🛑 RİSK KORUMASI: Ani çöküş varsa risk bildirimi yap
            if gunluk_degisim < self.ani_dusus_esigi:
                return {"sembol": sembol, "durum": "TEHLIKE", "mesaj": f"#{sembol} hissesinde %{round(gunluk_degisim,2)} ani değer kaybı! Teknik yapı haber etkisiyle bozulmuştur."}

            # --- TEKNİK SÜZGEÇLER ---
            rsi = ta.rsi(df['Close'], length=14).iloc[-1]
            avg_vol = df['Volume'].tail(20).mean()
            current_vol = df['Volume'].iloc[-1]
            vol_kat = round(current_vol / avg_vol, 1)

            # Emniyet Kilidi: Fiyat dünün ve açılışın üzerinde olmalı
            fiyat_onay = kapanis > dun_kapanis and kapanis > acilis
            vol_shock = vol_kat >= 1.7

            if not fiyat_onay or pddd > self.pddd_limit or pddd <= 0: return None

            # Pivot Hesaplama
            L_H, L_L, L_C = float(df['High'].iloc[-2]), float(df['Low'].iloc[-2]), float(df['Close'].iloc[-2])
            pivot = (L_H + L_L + L_C) / 3
            res1 = (2 * pivot) - L_L
            sup1 = (2 * pivot) - L_H

            puan = 0
            if 50 <= rsi <= 78: puan += 30
            if vol_shock: puan += 40
            if kapanis > res1: puan += 30

            if puan < 65: return None

            # 💡 ÖZEL ANALİZ YORUMU (3-5 Cümle)
            analiz_metni = (
                f"#{sembol} hissesinde hacim katsayısı {vol_kat}x seviyesine ulaşarak ortalamanın çok üzerinde bir para girişini doğrulamıştır. "
                f"PD/DD oranı {round(pddd,2)} ile temel iskontosunu korurken, fiyatın dünkü kapanış üzerinde kalması yükseliş isteğini teyit etmektedir. "
                f"RSI değeri {round(rsi,1)} ile momentumun taze olduğunu göstermektedir. "
                f"Anlık {round(res1,2)} direnci hedeflenirken, {round(sup1,2)} desteği emniyet sınırı olarak takip edilmelidir."
            )

            return {
                "sembol": sembol, "fiyat": round(kapanis, 2), "degisim": round(gunluk_degisim, 2),
                "ai_skor": puan, "hacim_kat": vol_kat, "pddd": round(pddd, 2),
                "destek": round(sup1, 2), "direnc": round(res1, 2), "rsi": round(rsi, 1),
                "analiz": analiz_metni,
                "durum": "🔥 TAVAN ADAYI" if vol_shock and gunluk_degisim > 3.5 else "🚀 MOMENTUM"
            }
        except: return None