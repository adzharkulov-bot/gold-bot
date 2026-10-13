import yfinance as yf
import pandas as pd
import time, requests, os, threading
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SYMBOL = "GC=F"

app = Flask(__name__)
@app.route('/')
def home(): return "AMD BOT LIVE - XAUUSD"

COOLDOWN = 2*3600
last_time = 0
last_type = None

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except: pass

def bot_loop():
    global last_time, last_type
    print("BOT STARTED AMD DISTRIBUTION")
    while True:
        try:
            df = yf.download(SYMBOL, period="2d", interval="5m", auto_adjust=True, progress=False)
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            if len(df) < 100: 
                time.sleep(60); continue

            df['EMA20'] = df['Close'].ewm(span=20).mean()
            df['EMA50'] = df['Close'].ewm(span=50).mean()

            price = float(df['Close'].iloc[-1])
            ema20 = float(df['EMA20'].iloc[-1])
            ema50 = float(df['EMA50'].iloc[-1])

            asia = df.iloc[-80:-20]
            ah = float(asia['High'].max())
            al = float(asia['Low'].min())
            rng = ah - al
            fib_short = ah - rng*0.38
            fib_long = al + rng*0.38

            prev = float(df['Close'].iloc[-2])
            manip_high = prev < ah and price > ah
            manip_low = prev > al and price < al

            sig = None
            sl = tp = 0
            if manip_high and price < fib_short and ema20 < ema50:
                sig = "SELL"; sl = ah+5; tp = al
            if manip_low and price > fib_long and ema20 > ema50:
                sig = "BUY"; sl = al-5; tp = ah

            can_send = (time.time() - last_time) > COOLDOWN
            no_flip = True
            if last_type and last_type != sig:
                if (time.time() - last_time) < 4*3600: no_flip = False

            if sig and can_send and no_flip:
                icon = "BUY" if sig=="BUY" else "SELL"
                msg = f"<b>XAUUSD {icon} {price:.2f}</b>\n\n"
                msg += f"AMD Distribution\nAsia {al:.1f}-{ah:.1f}\n38% Fib {fib_short:.1f}\nEMA {ema20:.1f}/{ema50:.1f}\n\nSL {sl:.2f} TP {tp:.2f}\n#GOLD"
                send(msg)
                last_time = time.time(); last_type = sig
                print(f"SENT {sig}")

            time.sleep(60)
        except Exception as e:
            print(f"Error {e}"); time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
