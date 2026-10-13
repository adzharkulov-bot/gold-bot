import requests, time, os, threading
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)
@app.route('/')
def home():
    return "GOLD BOT LIVE - AMD"

def send(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
    except: pass

def get_price_data():
    # Yahoo API түз, pandas'sыз
    url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=5m&range=2d"
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15).json()
    result = r['chart']['result'][0]
    closes = result['indicators']['quote'][0]['close']
    highs = result['indicators']['quote'][0]['high']
    lows = result['indicators']['quote'][0]['low']
    # None'лерди тазалоо
    closes = [c for c in closes if c is not None]
    highs = [h for h in highs if h is not None]
    lows = [l for l in lows if l is not None]
    return closes, highs, lows

last_time = 0
def bot_loop():
    global last_time
    print("BOT LOOP STARTED NO PANDAS")
    while True:
        try:
            closes, highs, lows = get_price_data()
            if len(closes) < 80:
                time.sleep(60)
                continue

            price = closes[-1]
            # EMA20 vs EMA50 ордуна жөнөкөй орточо
            ema20 = sum(closes[-20:]) / 20
            ema50 = sum(closes[-50:]) / 50

            # Азия коробкасы (кечээки 60 шам)
            asia_high = max(highs[-80:-20])
            asia_low = min(lows[-80:-20])
            rng = asia_high - asia_low
            fib_short = asia_high - rng * 0.38
            fib_long = asia_low + rng * 0.38

            prev = closes[-2]
            sig = None
            # ДИСТРИБУЦИЯ
            if prev < asia_high and price > asia_high and price < fib_short and ema20 < ema50:
                sig = "SELL"
            if prev > asia_low and price < asia_low and price > fib_long and ema20 > ema50:
                sig = "BUY"

            if sig and (time.time() - last_time) > 7200: # 2 саатта 1
                msg = f"<b>XAUUSD {sig} {price:.2f}</b>\n\nAMD Distribution\nAsia {asia_low:.1f}-{asia_high:.1f}\nFib 38% {fib_short:.1f}\nEMA {ema20:.1f}/{ema50:.1f}\n\n#GOLD"
                send(msg)
                last_time = time.time()
                print(f"SENT {sig}")

            print(f"Price {price:.2f} Asia {asia_low:.1f}-{asia_high:.1f}")
            time.sleep(60)
        except Exception as e:
            print(f"Error {e}")
            time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
