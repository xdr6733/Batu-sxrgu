from flask import Flask, jsonify, request
import threading
import telebot
import requests
import json
from telebot import types
from datetime import datetime, date
from bs4 import BeautifulSoup
import os
import time
import io

app = Flask(__name__)

# Global dictionary to track running bot instances {token: { "bot": instance, "thread": thread }}
bot_instances = {}

# File to store tokens
TOKENS_FILE = "tokens.json"

# Renk tanımlamaları
çıkarşuşarkıyıbatuflex = "\033[35m"
yatak = "\033[36m"
hackerhıhı = "\033[100m"
dev = "\033[101m"
batu = "\033[94m"
hehe = "\033[0m"

# ASCII art
hackerbatu = """⠀⠀⠀⠀⠀⣠⣴⣶⣿⣿⠿⣷⣶⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣶⣷⠿⣿⣿⣶⣦⣀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣶⣦⣬⡉⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠚⢉⣥⣴⣾⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀
⠀⠀⠀⡾⠿⠛⠛⠛⠛⠿⢿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣾⣿⣿⣿⣿⣿⠿⠿⠛⠛⠛⠛⠿⢧⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⣿⣿⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀⣠⣿⣿⣿⣿⡿⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣠⣤⠶⠶⠶⠰⠦⣤⣀⠀⠙⣷⠀⠀⠀⠀⠀⠀⠀⢠⡿⠋⢀⣀⣤⢴⠆⠲⠶⠶⣤⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠘⣆⠀⠀⢠⣾⣫⣶⣾⣿⣿⣿⣿⣷⣯⣿⣦⠈⠃⡇⠀⠀⠀⠀⢸⠘⢁⣶⣿⣵⣾⣿⣿⣿⣿⣷⣦⣝⣷⡄⠀⠀⡰⠂⠀
⠀⠀⣨⣷⣶⣿⣧⣛⣛⠿⠿⣿⢿⣿⣿⣛⣿⡿⠀⠀⡇⠀⠀⠀⠀⢸⠀⠈⢿⣟⣛⠿⢿⡿⢿⢿⢿⣛⣫⣼⡿⣶⣾⣅⡀⠀
⢀⡼⠋⠁⠀⠀⠈⠉⠛⠛⠻⠟⠸⠛⠋⠉⠁⠀⠀⢸⡇⠀⠀⠄⠀⢸⡄⠀⠀⠈⠉⠙⠛⠃⠻⠛⠛⠛⠉⠁⠀⠀⠈⠙⢧⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⡇⢠⠀⠀⠀⢸⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⡇⠀⠀⠀⠀⢸⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠟⠁⣿⠇⠀⠀⠀⠀⢸⡇⠙⢿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠰⣄⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣾⠖⡾⠁⠀⠀⣿⠀⠀⠀⠀⠀⠘⣿⠀⠀⠙⡇⢸⣷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠄⠀
⠀⠀⢻⣷⡦⣤⣤⣤⡴⠶⠿⠛⠉⠁⠀⢳⠀⢠⡀⢿⣀⠀⠀⠀⠀⣠⡟⢀⣀⢠⠇⠀⠈⠙⠛⠷⠶⢦⣤⣤⣤⢴⣾⡏⠀⠀
⠀⠀⠈⣿⣧⠙⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠘⠛⢊⣙⠛⠒⠒⢛⣋⡚⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⡿⠁⣾⡿⠀⠀⠀
⠀⠀⠀⠘⣿⣇⠈⢿⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⡿⢿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⡟⠁⣼⡿⠁⠀⠀⠀
⠀⠀⠀⠀⠘⣿⣦⠀⠻⣿⣷⣦⣤⣤⣶⣶⣶⣿⣿⣿⣿⠏⠀⠀⠻⣿⣿⣿⣿⣶⣶⣶⣦⣤⣴⣿⣿⠏⢀⣼⡿⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠘⢿⣷⣄⠙⠻⠿⠿⠿⠿⠿⢿⣿⣿⣿⣁⣀⣀⣀⣀⣙⣿⣿⣿⠿⠿⠿⠿⠿⠿⠟⠁⣠⣿⡿⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠻⣯⠙⢦⣀⠀⠀⠀⠀⠀⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠀⠀⠀⠀⠀⣠⠴⢋⣾⠟⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠙⢧⡀⠈⠉⠒⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠐⠒⠉⠁⢀⡾⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⣠⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢦⡀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⢀⡴⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀"""

class Batuflex:
    def __init__(self, token):
        try:
            # Attempt to create a TeleBot instance and verify the token by getting bot details.
            self.batuHeker = telebot.TeleBot(token)
            bot_info = self.batuHeker.get_me()
        except Exception as e:
            raise ValueError("Token geçersiz veya bot başlatılamadı: " + str(e))
        print(f"{dev}Dev: @batukurucu{hehe}")
        time.sleep(2)
        os.system('clear')
        print(f"{batu}{hackerbatu}{hehe}")
        print(f"{hackerhıhı}                  BOT BAŞLADI                             {hehe}")
        self.hekirBatuHekir = {}
        self.cistakHacker = {
            "Ad Soyad": {"url": "http://api.prymx.fun/apiler/adsoyad.php", "params": ["ad", "soyad", "il"], "method": "GET"},
            "TC Bilgi": {"url": "http://api.prymx.fun/apiler/tc.php", "params": ["tc"], "method": "GET"},
            "Aile": {"url": "http://api.prymx.fun/apiler/aile.php", "params": ["tc"], "method": "GET"},
            "Sulale": {"url": "http://api.prymx.fun/apiler/sulale.php", "params": ["tc"], "method": "GET"},
            "GSM TC": {"url": "http://api.prymx.fun/apiler/gsmtc.php", "params": ["gsm"], "method": "GET"},
            "TC GSM": {"url": "http://api.prymx.fun/apiler/tcgsm.php", "params": ["tc"], "method": "GET"},
            "SGK": {"url": "http://api.prymx.fun/apiler/sgk.php", "params": ["tc"], "method": "GET"},
            "Tapu": {"url": "http://api.prymx.fun/apiler/tapu.php", "params": ["tc"], "method": "GET"},
            "IP": {"url": "https://ipinfo.io", "params": ["ip"], "method": "GET"},
            "IBAN": {"url": "https://hesapno.com/mod_coz_iban.php", "params": ["iban"], "method": "POST"},
            "Burç Sorgu": {"url": "http://api.prymx.fun/apiler/tc.php", "params": ["tc"], "method": "GET"},
            "Hayat Bilgisi": {"url": "http://api.prymx.fun/apiler/tc.php", "params": ["tc"], "method": "GET"},
            "Site Ekran Görüntüsü": {"url": "https://api.pikwy.com/", "params": ["url"], "method": "GET", "screenshot": True},
            "sms bomber": {"url": "https://prymx.store/apiler/sms.php", "params": ["gsm"], "method": "GET", "ignore_response": True}
        }
        self.RESPONSE_LENGTH_THRESHOLD = 1000
        self.kardeşimAşkımYatSoySok()

    def kardeşimAşkımYatSoySok(self):
        @self.batuHeker.message_handler(commands=['start'])
        def basla(m):
            self.hekirHıhıSok(m)

        @self.batuHeker.callback_query_handler(func=lambda c: True)
        def callback(c):
            cid = c.message.chat.id
            secim = c.data
            self.hekirBatuHekir[cid] = {"selected_api": secim, "step": 0, "params": {}}
            if secim == "sms bomber":
                self.batuHeker.send_message(cid, "🧾 Lütfen 5 ile başlayan numarayı giriniz:")
            elif secim in ["IBAN", "IP", "Burç Sorgu", "Hayat Bilgisi", "Site Ekran Görüntüsü"]:
                pr = ("💳 Lütfen IBAN bilgisini giriniz:" if secim == "IBAN" else
                      ("🌐 Lütfen IP adresini giriniz:" if secim == "IP" else
                       ("🧾 Lütfen TC numaranızı giriniz:" if secim in ["Burç Sorgu", "Hayat Bilgisi"] else
                        "🔗 Lütfen site URL'sini giriniz:")))
                self.batuHeker.send_message(cid, pr)
            else:
                ilk = self.cistakHacker[secim]["params"][0]
                self.soySok(cid, ilk)

        @self.batuHeker.message_handler(func=lambda m: True)
        def mesaj_isle(m):
            cid = m.chat.id
            txt = m.text.strip()
            if cid not in self.hekirBatuHekir or "selected_api" not in self.hekirBatuHekir[cid]:
                self.batuHeker.send_message(cid, "ℹ️ Lütfen /start yaz.")
                return
            secim = self.hekirBatuHekir[cid]["selected_api"]
            if secim == "sms bomber":
                if not txt.startswith("5"):
                    self.batuHeker.send_message(cid, "⚠️ Numara geçersiz, lütfen 5 ile başlayan numara giriniz.")
                    return
                self.hekirBatuHekir[cid]["params"]["gsm"] = txt
                self.sisSok(cid)
            elif secim in ["IBAN", "IP", "Burç Sorgu", "Hayat Bilgisi", "Site Ekran Görüntüsü"]:
                key = "iban" if secim == "IBAN" else ("ip" if secim == "IP" else ("tc" if secim in ["Burç Sorgu", "Hayat Bilgisi"] else "url"))
                self.hekirBatuHekir[cid]["params"][key] = txt
                self.sisSok(cid)
            else:
                state = self.hekirBatuHekir[cid]
                adım = state.get("step", 0)
                reqs = self.cistakHacker[secim]["params"]
                cur = reqs[adım]
                if cur == "il" and txt == "İl Bilmiyorum":
                    state["params"][cur] = ""
                else:
                    state["params"][cur] = txt
                state["step"] += 1
                if state["step"] >= len(reqs):
                    self.sisSok(cid)
                else:
                    nextp = reqs[state["step"]]
                    self.soySok(cid, nextp)

    def soylikSelamSok(self):
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = [types.InlineKeyboardButton(text=anahtar, callback_data=anahtar) for anahtar in self.cistakHacker.keys()]
        markup.add(*buttons)
        return markup

    def hekirHıhıSok(self, mesaj):
        cid = mesaj.chat.id
        self.hekirBatuHekir[cid] = {}
        gselam = self.kardeşimAşkımYatSoy()
        self.batuHeker.send_message(cid, f"👋 {gselam}! Sorgu Bot'una hoş geldin! Lütfen aşağıdaki seçeneklerden istediğini seç:", reply_markup=self.soylikSelamSok())

    def kardeşimAşkımYatSoy(self):
        saat = datetime.now().hour
        if saat < 12:
            return "Günaydın"
        elif saat < 18:
            return "Tünaydın"
        else:
            return "İyi akşamlar"

    def soySok(self, cid, param):
        if param == "il":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            markup.add("İl Bilmiyorum")
            self.batuHeker.send_message(cid, f"🏙️ Lütfen 'il' bilgisini gir veya 'İl Bilmiyorum' deyin:", reply_markup=markup)
        else:
            self.batuHeker.send_message(cid, f"📝 Lütfen '{param}' bilgisini gir:")

    def sisSok(self, cid):
        secim = self.hekirBatuHekir[cid]["selected_api"]
        parms = self.hekirBatuHekir[cid]["params"]
        info = self.cistakHacker.get(secim)
        method = info.get("method", "GET")
        url = info["url"]
        try:
            if secim == "IP":
                full_url = f"https://ipinfo.io/{parms.get('ip','')}/json"
                resp = requests.get(full_url)
            elif secim == "IBAN":
                iban_val = parms.get("iban", "")
                cookies = {'PHPSESSID': 'jthkuejr3j9f6jetegjnfp1ou2'}
                headers = {'User-Agent': 'Mozilla/5.0'}
                resp = requests.post(url, cookies=cookies, headers=headers, data={'iban': iban_val, 'x': '84', 'y': '29'})
                soup = BeautifulSoup(resp.text, 'html.parser')
                def gn(tag, d=""):
                    return tag.next_sibling.strip() if tag and tag.next_sibling else d
                res = {
                    'Banka Adı': gn(soup.find('b', string='Ad:')),
                    'Banka Kodu': gn(soup.find('b', string='Kod:'))
                }
                mesaj = "\n".join([f"{k}: {v}" for k, v in res.items()])
                self.batuHeker.send_message(cid, mesaj)
                self.hekirBatuHekir.pop(cid, None)
                return
            elif secim == "Site Ekran Görüntüsü":
                url_input = parms.get("url", "")
                sp = {'tkn': '125', 'd': '3000', 'u': url_input, 'fs': '0', 'w': '1280', 'h': '1200', 's': '100', 'z': '100', 'f': 'jpg', 'rt': 'jweb'}
                hdr = {'User-Agent': 'Mozilla/5.0'}
                r = requests.get("https://api.pikwy.com/", params=sp, headers=hdr)
                ds = r.json()
                iurl = ds.get("iurl")
                if iurl:
                    ir = requests.get(iurl)
                    photo = io.BytesIO(ir.content)
                    photo.name = "ekran_goruntusu.jpg"
                    self.batuHeker.send_photo(cid, photo, caption="📸 Site ekran görüntüsü hazır!")
                else:
                    self.batuHeker.send_message(cid, "Görüntü URL'si alınamadı!")
                self.hekirBatuHekir.pop(cid, None)
                return
            elif secim == "sms bomber":
                gsm_num = parms.get("gsm", "")
                full_url = f"{url}?gsm={gsm_num}"
                requests.get(full_url)
                self.batuHeker.send_message(cid, "SMS bomber işlemi başlatıldı!")
                self.hekirBatuHekir.pop(cid, None)
                return
            else:
                if method == "GET":
                    resp = requests.get(url, params=parms)
                else:
                    resp = requests.request(method, url, params=parms)
            resp.raise_for_status()
            if secim in ["Burç Sorgu", "Hayat Bilgisi"]:
                ddata = resp.json()
                if "data" in ddata and ddata["data"]:
                    rec = ddata["data"][0]
                    dob_str = rec.get("DOGUMTARIHI", "")
                    zodiac = "Bilinmiyor"
                    age = "Bilinmiyor"
                    if dob_str:
                        try:
                            parts = dob_str.split('.')
                            if len(parts) >= 3:
                                day = int(parts[0])
                                month = int(parts[1])
                                year = int(parts[2])
                                zodiac = self.compute_zodiac(day, month)
                                bdate = date(year, month, day)
                                today = date.today()
                                age = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
                        except Exception:
                            zodiac = "Bilinmiyor"
                    if secim == "Burç Sorgu":
                        mesaj = f"💫 Doğum Tarihiniz: {dob_str}\n👉 Burcunuz: {zodiac}"
                    else:
                        mn = {1:"Ocak",2:"Şubat",3:"Mart",4:"Nisan",5:"Mayıs",6:"Haziran",7:"Temmuz",8:"Ağustos",9:"Eylül",10:"Ekim",11:"Kasım",12:"Aralık"}
                        try:
                            if dob_str and len(parts) >= 3:
                                fdob = f"{day} {mn.get(month,month)} {year}"
                            else:
                                fdob = dob_str
                        except Exception:
                            fdob = dob_str
                        mesaj = (f"{rec.get('ADI','Bilinmiyor')} {rec.get('SOYADI','Bilinmiyor')}, {rec.get('TC','')} TC kimlik numaralıdır. "
                                 f"Doğum tarihi {fdob} olarak kaydedilmiştir ve yaklaşık {age} yaşındadır. "
                                 f"Burcu {zodiac} olup, babası {rec.get('BABAADI','Bilinmiyor')} (TC: {rec.get('BABATC','')}) ve annesi "
                                 f"{rec.get('ANNEADI','Bilinmiyor')} (TC: {rec.get('ANNETC','')}) kayıtlıdır. "
                                 f"İkamet {rec.get('NUFUSIL','Bilinmiyor')}/{rec.get('NUFUSILCE','Bilinmiyor')} ve uyruk {rec.get('UYRUK','Bilinmiyor')}.")
                    self.batuHeker.send_message(cid, mesaj)
                else:
                    self.batuHeker.send_message(cid, "Veri alınamadı. Lütfen geçerli bir TC girin.")
            else:
                ddata = resp.json()
                pretty = json.dumps(ddata, indent=4, ensure_ascii=False)
                if len(pretty) > self.RESPONSE_LENGTH_THRESHOLD:
                    fname = f"{secim.replace(' ', '_')}_.txt"
                    with open(fname, "w", encoding="utf-8") as f:
                        f.write(pretty)
                    with open(fname, "rb") as f:
                        self.batuHeker.send_document(cid, f, caption="📄 Yanıt dosyası:")
                else:
                    self.batuHeker.send_message(cid, f"📋 Sorgu Sonucu:\n\n<pre>{pretty}</pre>", parse_mode="HTML")
        except Exception as ex:
            self.batuHeker.send_message(cid, f"❌ API isteğinde hata")
        self.hekirBatuHekir.pop(cid, None)
        self.batuHeker.send_message(cid, "✅ İşlem tamamlandı. Yeni sorgu için /start yazın.")

    def compute_zodiac(self, day, month):
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "Koç"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "Boğa"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return "İkizler"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return "Yengeç"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "Aslan"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "Başak"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return "Terazi"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return "Akrep"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return "Yay"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "Oğlak"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "Kova"
        elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
            return "Balık"
        else:
            return "Bilinmiyor"

    def waitForSok(self):
        while True:
            try:
                requests.get("https://www.google.com", timeout=5)
                break
            except requests.RequestException:
                time.sleep(5)

    def run(self):
        # Bot polling işlemi bloklamaması için pollingle başlatılır.
        self.batuHeker.polling(none_stop=True)

def load_tokens():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r") as f:
            return json.load(f)
    return []

def save_token(token):
    tokens = load_tokens()
    if token not in tokens:
        tokens.append(token)
        with open(TOKENS_FILE, "w") as f:
            json.dump(tokens, f)

def start_bot(token):
    try:
        bot_instance = Batuflex(token)
    except ValueError as e:
        # Oluşan hata token geçersiz olduğunda yakalanır.
        return None, str(e)
    t = threading.Thread(target=bot_instance.run)
    t.daemon = True
    t.start()
    return {"instance": bot_instance, "thread": t}, None

@app.route('/')
def index():
    return jsonify({
        "message": "Lütfen URL'yi şu formatta kullanın: /botbaşlat<token> veya /botdurdur<token>. Örneğin: http://127.0.0.1:5000/botbaşlat123456:ABCDEF"
    })

@app.route('/botbaşlat<token>', methods=['GET'])
def bot_baslat(token):
    if token in bot_instances:
        return jsonify({
            "status": "error",
            "message": "Bu token ile bir bot zaten çalışıyor. Bot bilgisi:",
            "bot_info": {
                "username": bot_instances[token]["instance"].batuHeker.get_me().username,
                "id": bot_instances[token]["instance"].batuHeker.get_me().id,
                "developer": "@batukurucu"
            }
        })
    bot_data, err = start_bot(token)
    if err:
        return jsonify({
            "status": "error",
            "message": "Bot başlatılamadı: " + err
        })
    # Token dosyaya kaydedilir.
    save_token(token)
    bot_instances[token] = bot_data
    bot_info = bot_data["instance"].batuHeker.get_me()
    return jsonify({
        "status": "success",
        "message": "Bot aktif oldu!",
        "bot_info": {
            "username": bot_info.username,
            "id": bot_info.id,
            "developer": "@batukurucu"
        }
    })

@app.route('/botdurdur<token>', methods=['GET'])
def bot_durdur(token):
    if token not in bot_instances:
        return jsonify({
            "status": "error",
            "message": "Bu token için çalışan bir bot bulunamadı. Lütfen doğru token ile giriş yapın. Örneğin: /botdurdur123456:ABCDEF"
        })
    try:
        instance = bot_instances[token]["instance"]
        instance.batuHeker.stop_polling()
        # Bot durduktan sonra global kayıttan siliniyor.
        del bot_instances[token]
        return jsonify({
            "status": "success",
            "message": "Bot inaktif hale getirildi.",
            "bot_info": {
                "developer": "@batukurucu"
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Bot durdurulurken hata oluştu: " + str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
