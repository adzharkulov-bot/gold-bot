import os, time, threading, requests
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@xauusdakyl"  # @ белгиси менен!

@app.route('/')
def home():
    return f"BOT LIVE! Token exists: {bool(BOT_TOKEN)} | Channel: {CHANNEL}"

def send_to_telegram(text):
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN жок! Render > Environment текшер")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL, "text": text}
    try:
        r = requests.post(url, json=payload, timeout=20)
        print(f"Telegram response: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Telegram error: {e}")

def pro_signal_loop():
    print("Loop started, waiting 5 sec...")
    time.sleep(5)
    
    # Сразу 1 жолу жөнөт
    price = 4185.50
    msg = f"""XAUUSD | BUY SETUP H4 PRO 🚀

Current: {price}
Wyckoff Range: 4111 - 4193
Spring: 4066 LOW ✅
CHOCH: 4183 broke ✅

INDICATORS 90/100:
✅ EMA 50>200 Bullish
✅ RSI 56 Healthy
✅ MACD Bullish Cross
✅ Fib 0.382 retest

Entry: 4156
SL: 4103
TP1: 4193 | TP2: 4226 | TP3: 4251
RR: 1:3.2

@xauusdakyl | TEST SIGNAL - Bot ishlep jatady!
"""
    send_to_telegram(msg)
    
    # Андан кийин ар 4 саатта
    while True:
        time.sleep(14400)
        send_to_telegram(msg)

threading.Thread(target=pro_signal_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
