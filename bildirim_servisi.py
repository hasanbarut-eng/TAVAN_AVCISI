import requests

class BildirimServisi:
    def __init__(self, token, chat_id):
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    def rapor_gonder(self, adaylar, riskli_olanlar):
        # 1. Pozitif Sinyaller
        if adaylar:
            adaylar.sort(key=lambda x: x['ai_skor'], reverse=True)
            for a in adaylar[:6]:
                mesaj = (
                    f"🚀 <b>{a['durum']} | #{a['sembol']}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚠️ <i>Yatırım tavsiyesi değildir.</i>\n\n"
                    f"| 🛡️ SEMBOL | 💰 FİYAT | 📈 DEĞİŞİM | 📊 SKOR |\n"
                    f"| :--- | :--- | :--- | :--- |\n"
                    f"| <b>#{a['sembol']}</b> | {a['fiyat']} TL | %{a['degisim']} | <b>%{a['ai_skor']}</b> |\n\n"
                    f"| 🔥 HACİM | 📉 PD/DD | 🛡️ DESTEK | 🎯 DİRENÇ |\n"
                    f"| :--- | :--- | :--- | :--- |\n"
                    f"| <b>{a['hacim_kat']}x</b> | {a['pddd']} | {a['destek']} | {a['direnc']} |\n\n"
                    f"💡 <b>DERİN ANALİZ:</b>\n<i>{a['analiz']}</i>\n"
                    f"━━━━━━━━━━━━━━━━━━━━"
                )
                self._gonder(mesaj)

        # 2. Riskli Sinyaller (Haber Kalkanı)
        if riskli_olanlar:
            for r in riskli_olanlar:
                r_mesaj = f"🚨 <b>KRİTİK RİSK UYARISI | #{r['sembol']}</b>\n━━━━━━━━━━━━━━━━━━━━\n{r['mesaj']}"
                self._gonder(r_mesaj)

    def _gonder(self, metin):
        try:
            requests.post(self.url, json={"chat_id": self.chat_id, "text": metin, "parse_mode": "HTML"})
        except: pass