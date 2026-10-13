import yfinance as yf
import pandas as pd
import time
import requests
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SYMBOL = "GC=F"

COOLDOWN = 2 * 3600
last_signal_time = 0
last_type = None

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"Send error {e}")

def get_data():
    df = yf.download(SYMBOL, period="2d", interval="5m", auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

print("BOT STARTED AMD DISTRIBUTION")

while True:
    try:
        df = get_data()
        if len(df) < 100:
            time.sleep(60)
            continue

        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        
        curr = df.iloc[-1]
        price = float(curr['Close'])
        ema20 = float(curr['EMA20'])
        ema50 = float(curr['EMA50'])

        asia = df.iloc[-80:-20]
        asia_high = float(asia['High'].max())
        asia_low = float(asia['Low'].min())
        
        range_hl = asia_high - asia_low
        fib_short = asia_high - range_hl * 0.38
        fib_long = asia_low + range_hl * 0.38

        prev_close = float(df.iloc[-2]['Close'])
        manipulated_high = prev_close < asia_high and price > asia_high
        manipulated_low = prev_close > asia_low and price < asia_low

        signal = None
        sl = 0
        tp = 0

        if manipulated_high and price < fib_short and ema20 < ema50:
            signal = "SELL"
            sl = asia_high + 5
            tp = asia_low

        if manipulated_low and price > fib_long and ema20 > ema50:
            signal = "BUY"
            sl = asia_low - 5
            tp = asia_high

        can_send = (time.time() - last_signal_time) > COOLDOWN
        no_flip = True
        if last_type and last_type != signal:
            if (time.time() - last_signal_time) < 4*3600:
                no_flip = False

        if signal and can_send and no_flip:
            if signal == "BUY":
                icon = "BUY"
            else:
                icon = "SELL"
            
            msg = "<b>XAUUSD " + icon + " " + f"{price:.2f}" + "</b>\n\n"
            msg += "AMD Distribution confirmed\n"
            msg += f"Asia: {asia_low:.1f} - {asia_high:.1f}\n"
            msg += f"38% Fib: {fib_short:.1f}\n"
            msg += f"EMA20: {ema20:.1f} | EMA50: {ema50:.1f}\n\n"
            msg += f"SL: {sl:.2f}\n"
            msg += f"TP: {tp:.2f}\n\n"
            msg += "#GOLD #XAUUSD"
            
            send(msg)
            last_signal_time = time.time()
            last_type = signal
            print(f"SENT {signal}")

        print(f"PRICE {price:.2f} ASIA {asia_low:.1f}-{asia_high:.1f}")
        time.sleep(60)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
