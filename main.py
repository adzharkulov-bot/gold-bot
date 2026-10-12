import os, time, threading, requests
import yfinance as yf
import pandas as pd
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@xauusdakyl"
app = Flask(__name__)

def send(msg):
    if not TOKEN: return
    try:
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHANNEL, "text": msg, "parse_mode":"HTML"}, timeout=10)
        print(f"TG->{r.status_code} {r.text[:100]}", flush=True)
    except Exception as e:
        print(f"TG ERR {e}", flush=True)

def get_data():
    # XAUUSD = GC=F (Gold Futures) - эң туруктуу
    df = yf.download("GC=F", period="5d", interval="15m", progress=False)
    if df.empty: return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df['EMA50'] = df['Close'].ewm(span=50).mean()
    df['EMA200'] = df['Close'].ewm(span=200).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta>0, 0).ewm(alpha=1/14).mean()
    loss = -delta.where(delta<0, 0).ewm(alpha=1/14).mean()
    df['RSI'] = 100 - (100/(1+gain/loss))
    df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
    df['MACD_sig'] = df['MACD'].ewm(span=9).mean()
    return df

def check_100_setup(df):
    c = df.iloc[-1]
    prev = df.iloc[-2]
    price = float(c['Close'])
    score_buy = 0
    score_sell = 0
    reasons = []

    # 1. Trend
    if price > c['EMA50'] > c['EMA200']:
        score_buy+=1; reasons.append("EMA50>EMA200 өйдө тренд")
    if price < c['EMA50'] < c['EMA200']:
        score_sell+=1; reasons.append("EMA50<EMA200 ылдый тренд")

    # 2. RSI
    if 48 < c['RSI'] < 68: 
        score_buy+=1; reasons.append(f"RSI {c['RSI']:.1f} күч")
    if 32 < c['RSI'] < 52:
        score_sell+=1; reasons.append(f"RSI {c['RSI']:.1f} алсыздык")

    # 3. MACD
    if c['MACD'] > c['MACD_sig'] and prev['MACD'] <= prev['MACD_sig']:
        score_buy+=1; reasons.append("MACD bullish crossover")
    if c['MACD'] < c['MACD_sig'] and prev['MACD'] >= prev['MACD_sig']:
        score_sell+=1; reasons.append("MACD bearish crossover")

    # 4. Price vs EMA50 distance (поддержка)
    if 0 < (price - c['EMA50'])/price < 0.003: # 0.3% жакын
        score_buy+=1; reasons.append("EMA50 поддержкадан секирүү")
    if 0 < (c['EMA50'] - price)/price < 0.003:
        score_sell+=1; reasons.append("EMA50 каршылыктан кайтуу")

    # 5. ATR / Volatility - соңку 3 бар өсүп жатабы
    if df['Close'].iloc[-3:].is_monotonic_increasing and c['RSI']<70:
        score_buy+=1
    if df['Close'].iloc[-3:].is_monotonic_decreasing and c['RSI']>30:
        score_sell+=1

    # 6. 100% чечим - 5+ шарт
    if score_buy >= 5:
        return "BUY", price, reasons, score_buy
    if score_sell >= 5:
        return "SELL", price, reasons, score_sell
    return None, price, [], 0

def loop():
    print("Loop started - 100% setup гана күтүү режими", flush=True)
    send("✅ gold-bot 100% сетап режимине өттү. Эми ар 30мүн эмес, болгону идеал сетапта гана сигнал @xauusdakyl")
    last_signal = 0
    while True:
        try:
            df = get_data()
            if df is not None:
                side, price, reasons, score = check_100_setup(df)
                if side and time.time() - last_signal > 3600*2: # 2 саатта 1 жолу гана
                    sl = price*0.996 if side=="BUY" else price*1.004
                    tp = price*1.008 if side=="BUY" else price*0.992
                    txt = f"<b>XAUUSD {price:.2f} - 100% {side} 🟢</b>\n\n"
                    txt += f"Score: {score}/6 ✅\n"
                    txt += "\n".join([f"• {r}" for r in reasons[:5]])
                    txt += f"\n\nSL: {sl:.2f} | TP: {tp:.2f}\n\n#XAUUSD #100setup"
                    send(txt)
                    last_signal = time.time()
                else:
                    print(f"No 100% setup. Price {df.iloc[-1]['Close']:.2f} score check", flush=True)
        except Exception as e:
            print(f"ERR {e}", flush=True)
        time.sleep(900) # 15 мүн сайын текшер

threading.Thread(target=loop, daemon=True).start()

@app.route("/")
def home(): return "gold-bot 100% setup mode live"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))
