import yfinance as yf
import pandas as pd
import time, requests, os, threading
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SYMBOL = "GC=F" # GOLD

app = Flask(__name__)
@app.route('/')
def home():
    return "AMD BOT LIVE"

COOLDOWN = 2*3600
last_time = 0
last_type = None

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except:
        pass

def bot_loop():
    global last_time, last_type
    print("BOT LOOP STARTED")
    while True:
        try:
            df = yf.download(SYMBOL, period="2d", interval="5m", auto_adjust=True, progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if len(df) < 100:
                time.sleep(60)
                continue

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
            if manip_high and price < fib_short and ema20 < ema50:
                sig = "SELL"
            if manip_low and price > fib_long and ema20 > ema50:
                sig = "BUY"

            can_send = (time.time() - last_time) > COOLDOWN
            if sig and can_send:
                if last_type != sig or (time.time()-last_time)>144
