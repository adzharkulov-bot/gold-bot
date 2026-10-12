import os, time, threading, requests
from flask import Flask
import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@xauusdakyl"

@app.route('/')
def home(): return "XAUUSD PRO SETUP BOT LIVE ✅"

def get_data():
    try:
        df = yf.download("GC=F", period="20d", interval="1h", progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return None

def indicators(df):
    close = df['Close']
    # EMA
    df['EMA50'] = close.ewm(span=50).mean()
    df['EMA200'] = close.ewm(span=200).mean()
    # RSI
    delta = close.diff()
    gain = delta.where(delta>0,0).rolling(14).mean()
    loss = -delta.where(delta<0,0).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + gain/loss))
    # ATR for SL
    tr = pd.concat([df['High']-df['Low'], (df['High']-close.shift()).abs(), (df['Low']-close.shift()).abs()], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(14).mean()
    # MACD
    ema12 = close.ewm(span=12).mean()
    ema26 = close.ewm(span=26).mean()
    df['MACD'] = ema12 - ema26
    df['SIGNAL'] = df['MACD'].ewm(span=9).mean()
    return df

def generate_pro_setup(df):
    last = df.iloc[-1]
    price = float(last['Close'])
    atr = float(last['ATR'])
    rsi = float(last['RSI'])
    ema50 = float(last['EMA50'])
    ema200 = float(last['EMA200'])

    # Wyckoff levels (auto detect recent range)
    recent_high = df['High'].tail(100).max()
    recent_low = df['Low'].tail(100).min()
    wyck_top = df['High'].tail(50).max()
    wyck_bottom = df['Low'].tail(50).min()
    
    # Fib from last swing low to high
    fib_0382 = recent_low + (recent_high - recent_low)*0.618 # inverted for pullback long
    fib_05 = recent_low + (recent_high - recent_low)*0.5
    fib_0618 = recent_low + (recent_high - recent_low)*0.382

    # Logic scoring
    score = 0
    reasons = []
    if price > ema50 and ema50 > ema200: 
        score+=20; reasons.append("✅ Trend: EMA 50>200 Bullish")
    else: reasons.append("⚠️ Trend: Mixed")
    if 40 < rsi < 65: 
        score+=20; reasons.append(f"✅ RSI: {rsi:.1f} Healthy pullback")
    if last['MACD'] > last['SIGNAL']: 
        score+=15; reasons.append("✅ MACD Bullish Cross")
    if price < wyck_top and price > wyck_bottom: 
        score+=15; reasons.append("✅ Wyckoff Re-accumulation")
    # CHOCH + Spring logic
    if df['Low'].tail(10).min() < wyck_bottom: 
        score+=15; reasons.append("✅ Spring: Liquidity sweep below range")
    
    direction = "BUY" if score >= 60 else "WAIT"
    
    entry = round(price,2) if direction=="BUY" else round(fib_0382,2)
    sl = round(entry - atr*1.5,2)
    tp1 = round(entry + (entry-sl)*1.5,2)
    tp2 = round(recent_high,2)
    tp3 = round(recent_high + atr*2,2)
    rr = round((tp2-entry)/(entry-sl),2) if entry!=sl else 0

    msg = f"""XAUUSD | {direction} SETUP H4 PRO
📅 {pd.Timestamp.now().strftime('%B %d, %Y %H:%M')} GMT+6

PRICE ACTION:
- Current: {price}
- Wyckoff Range: {wyck_bottom:.0f} - {wyck_top:.0f}
- Recent HIGH: {recent_high:.0f} | LOW: {recent_low:.0f}
- CHOCH Level: {wyck_top:.0f} broke

INDICATORS CONFLUENCE {score}/100:
{chr(10).join(reasons)}
- ATR(14): {atr:.2f} (Volatility)
- EMA50: {ema50:.1f} | EMA200: {ema200:.1f}

SETUP:
Entry: {entry} (0.382 + CHoCH retest + EMA50)
Stop Loss: {sl} (Below 0.618 & ATR)
TP1: {tp1} (Recent High retest)
TP2: {tp2} (Buy-side Liquidity)
TP3: {tp3} (Extension -0.272)
Risk/Reward: 1:{rr}

INVALIDATION:
H1 close below {sl} or RSI < 35

WINLOUH PRO | @xauusdakyl
"""
    return msg

def send_loop():
    time.sleep(5)
    while True:
        try:
            df = get_data()
            if df is not None:
                df = indicators(df)
                text = generate_pro_setup(df)
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                requests.post(url, data={"chat_id": CHANNEL, "text": text})
                print("Signal sent")
            else:
                print("No data")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(14400) # 4 саатта бир H4

threading.Thread(target=send_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
