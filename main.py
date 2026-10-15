import os
import requests
from flask import Flask
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print(f"Token/ChatID жок! BOT_TOKEN={bool(BOT_TOKEN)} CHAT_ID={CHAT_ID}")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
        print(f"Telegram response: {r.text}")
    except Exception as e:
        print(f"Telegram error: {e}")

@app.route("/")
def home():
    return "GOLD Bot is Live - Lite Mode"

@app.route("/test")
def test():
    # yfinance жок, жөн гана тест
    msg = f"✅ БОТ ИШТЕП ЖАТАТ!\n\nGOLD SMC Lite Bot\nУбакыт: {datetime.now().strftime('%H:%M:%S')}\nСтатус: Live\n\nRender катасы оңдолду!"
    send_telegram(msg)
    return f"Sent: {msg}"

@app.route("/check")
def check():
    # Бул жерден бааны текшеребиз кийин Order Block кошобуз
    send_telegram("🔍 Gold текшерилүүдө... OB изделүүдө")
    return "Checking"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
