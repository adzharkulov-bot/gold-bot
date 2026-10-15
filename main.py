import os
import requests
from flask import Flask
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

# Токендерди Render Environment'ден алат
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Send error: BOT_TOKEN or CHAT_ID not defined")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

@app.route("/")
def home():
    return "GOLD Bot is Live"

@app.route("/test")
def test():
    try:
        df = yf.download("GC=F", period="1d", interval="5m")
        price = float(df['Close'].iloc[-1])
        msg = f"✅ БОТ ИШТЕП ЖАТАТ!\nGOLD: {price:.2f}\nУбакыт: {datetime.now().strftime('%H:%M')}\nСтатус: Live"
        send_telegram(msg)
        return f"Sent: {msg}"
    except Exception as e:
        return f"Error: {e}"

def check_setup():
    # Бул жер сенин SMC стратегияң болот
    # Азыр жөн гана лог чыгарат
    print(f"No setup {datetime.now()}")

if __name__ == "__main__":
    check_setup()
    app.run(host="0.0.0.0", port=10000)
