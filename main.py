import os, requests
from flask import Flask

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

@app.route("/")
def home():
    return f"Bot Live! Token барбы: {bool(BOT_TOKEN)}, ChatID: {CHAT_ID}"

@app.route("/test")
def test():
    if not BOT_TOKEN:
        return "КАТА: BOT_TOKEN Environment'де жок!"
    if not CHAT_ID:
        return "КАТА: CHAT_ID Environment'де жок!"
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "✅ БОТ ИШТЕП ЖАТАТ! Render оңдолду."}
    r = requests.post(url, json=payload)
    return f"Telegram жообу: {r.text}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
