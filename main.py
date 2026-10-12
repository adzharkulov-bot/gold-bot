import os, time, threading, requests
from flask import Flask
app = Flask(__name__)
BOT_TOKEN = os.getenv("8639126332:AAGwJMa7InLOuMosdcS7nAZJ_boriBZK2HA")
CHANNEL = "@xauusdakyl"

def send(text):
    if not BOT_TOKEN:
        print("❌ NO TOKEN"); return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHANNEL, "text": text}, timeout=10)
        print(f"TG -> {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"TG ERR {e}")

def loop():
    time.sleep(5)
    print("Loop started")
    send("✅ TEST: Gold-bot подключился! Если видишь это в @xauusdakyl - бот работает.")
    while True:
        time.sleep(14400)
        send("XAUUSD Update - Bot Live")

threading.Thread(target=loop, daemon=True).start()

@app.route('/')
def home():
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
