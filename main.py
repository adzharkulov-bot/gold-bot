import requests, time, threading
from flask import Flask
from datetime import datetime, timezone, timedelta

BOT_TOKEN = "8639126332:AAGwJMa7InLOuMosdcS7nAZJ_boriBZK2HA"
CHAT_ID = "8639126332"

app = Flask(__name__)
@app.route('/')
def home():
    return "GOLD BOT ISH TEP JATAT!"

def send(t):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": t}, timeout=10)
    except: pass

def get_gold():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
        return float(r['price'])
    except:
        return None

def bot_loop():
    send("✅ GOLD BOT Render да куйду!")
    last = 0
    while True:
        try:
            price = get_gold()
            if price:
                bish = (datetime.now(timezone.utc)+timedelta(hours=6)).strftime("%H:%M")
                print(f"${price} {bish}")
                if last != 0 and abs(price-last) > 1:
                    send(f"🔥 GOLD {price:.2f} ⏰{bish}\nОзгоруу {price-last:+.2f}")
                if last == 0:
                    send(f"💰 GOLD ${price:.2f} козомол башталды {bish}")
                last = price
        except: pass
        time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
