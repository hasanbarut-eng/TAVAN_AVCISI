import requests
import logging

class BildirimServisi:
    def __init__(self, token, chat_id):
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    def rapor_gonder(self, adaylar):
        """
        Sinyalleri eğitici bir dille ve stratejik seviyelerle Telegram'a mühürler.
        """
        for a in adaylar[:5]: # En kaliteli 5 sinyali gönder
            mesaj = (
                f"🚀 <b>TAVAN POTANSİYELİ | #{a['sembol']}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 <b>Fiyat:</b> {a['fiyat']} TL | %{a['degisim']}\n"
                f"🌟 <b>SERİ POTANSİYELİ:</b> {a['seri']}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📥 <b>STRATEJİK İŞLEM PLANI</b>\n"
                f"• <b>Alım Aralığı:</b> {round(a['fiyat']*0.995, 2)} - {round(a['fiyat']*1.005, 2)} TL\n"
                f"• <b>Kâr Al (Hedef):</b> {a['direnc']} TL\n"
                f"• <b>Zarar Kes (Stop):</b> {a['destek']} TL\n\n"
                f"🔍 <b>NEDEN BU HİSSEYİ SEÇTİM? (EĞİTİM)</b>\n"
                f"<i>{a['analiz']}</i>\n\n"
                f"📘 <b>KÜÇÜK BİR SÖZLÜK:</b>\n"
                f"• <i>Tavan Adayı: Bugün %10 yükselme potansiyeli olan.</i>\n"
                f"• <i>Tavan Serisi: Yükselişin birkaç gün sürme ihtimali.</i>\n"
                f"• <i>Tavan-Taban Riski: Hacimsiz (sahte) yükselişlerdeki düşüş tehlikesi.</i>\n\n"
                f"⚠️ <b>Yatırım Tavsiyesi Değildir.</b> Matematiksel analizdir.\n"
                f"━━━━━━━━━━━━━━━━━━━━"
            )
            try:
                requests.post(self.url, json={"chat_id": self.chat_id, "text": mesaj, "parse_mode": "HTML"}, timeout=10)
            except Exception as e:
                logging.error(f"❌ Telegram gönderim hatası: {e}")

    def hata_bildir(self, mesaj):
        """Sistem hatalarını yöneticiye bildirir."""
        try:
            requests.post(self.url, json={"chat_id": self.chat_id, "text": f"🚨 SİSTEM HATASI: {mesaj}"})
        except: pass
