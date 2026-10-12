import os, time, threading, requests
from flask import Flask

app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
CHAT = "@xauusdakyl"

def send(text):
    if not TOKEN:
        print("❌ BOT_TOKEN жок! Render Environment текшер")
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT, "text": text}, timeout=15)
        print(f"TG->{r.status_code} {r.text[:150]}")
    except Exception as e:
        print(f"TG ERR {e}")

def loop():
    time.sleep(3)
    print("Loop started")
    send("✅ TEST: gold-bot жанданды @xauusdakyl")
    while True:
        time.sleep(3600*4)
        send("XAUUSD Live Update - bot иштеп жатат")

threading.Thread(target=loop, daemon=True).start()

@app.route("/")
def home():
    return "OK - bot running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
