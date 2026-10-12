import os, time, threading, requests
from flask import Flask
import json

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@xauusdakyl"
app = Flask(__name__)

def send(msg):
    if not TOKEN: return
    try:
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHANNEL, "text": msg, "parse_mode":"HTML"}, timeout=15)
        print(f"TG->{r.status_code}", flush=True)
    except Exception as e:
        print(f"TG ERR {e}", flush=True)

def get_gold():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=15m&range=5d"
        j = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15).json()
        closes = j['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None][-200:]
        return closes
    except Exception as e:
        print(f"DATA ERR {e}", flush=True)
        return None

def ema(data, span):
    k = 2/(span+1)
    e = data[0]
    for p in data[1:]: e = p*k + e*(1-k)
    return e

def rsi(data, period=14):
    gains=losses=0
    for i in range(1, period+1):
        d = data[-i] - data[-i-1]
        if d>0: gains+=d
        else: losses+=-d
    if losses==0: return 70
    rs = (gains/period)/(losses/period)
    return 100 - (100/(1+rs))

def check_100(closes):
    if len(closes)<200: return None, closes[-1], [], 0
    price = closes[-1]
    ema50 = ema(closes[-50:], 50)
    ema200 = ema(closes[-200:], 200)
    r = rsi(closes)
    # MACD simple
    ema12 = ema(closes[-12:], 12)
    ema26 = ema(closes[-26:], 26)
    macd = ema12-ema26

    score_buy=0; score_sell=0; reasons=[]

    if price > ema50 > ema200:
        score_buy+=1; reasons.append(f"Тренд өйдө: {price:.1f} > EMA50 {ema50:.1f}")
    if price < ema50 < ema200:
        score_sell+=1; reasons.append(f"Тренд ылдый: {price:.1f} < EMA50")

    if 48 < r < 68:
        score_buy+=1; reasons.append(f"RSI {r:.1f} күч бар")
    if 32 < r < 52:
        score_sell+=1; reasons.append(f"RSI {r:.1f} алсыздык")

    if macd > 0 and closes[-1] > closes[-2]:
        score_buy+=1; reasons.append("MACD оң + өсүш")
    if macd < 0 and closes[-1] < closes[-2]:
        score_sell+=1; reasons.append("MACD терс + түшүш")

    if 0 < (price-ema50)/price < 0.004:
        score_buy+=1; reasons.append("EMA50 колдоодон секирүү")
    if 0 < (ema50-price)/price < 0.004:
        score_sell+=1; reasons.append("EMA50 каршылыктан кайтуу")

    # 3 бар өсүш/түшүш
    if closes[-3] < closes[-2] < closes[-1] and r<70:
        score_buy+=1
    if closes[-3] > closes[-2] > closes[-1] and r>30:
        score_sell+=1

    if score_buy>=5: return "BUY", price, reasons, score_buy
    if score_sell>=5: return "SELL", price, reasons, score_sell
    return None, price, [], 0

def loop():
    print("Loop 100% ONLY mode", flush=True)
    send("✅ gold-bot эми 100% сетап гана күтөт. Ар 30мүн эмес — болгону идеал сигналда @xauusdakyl")
    last=0
    while True:
        try:
            closes = get_gold()
            if closes:
                side, price, reasons, score = check_100(closes)
                print(f"Check price {price:.2f} side={side} score={score}", flush=True)
                if side and time.time()-last > 7200: # 2 саатта 1 жолу
                    sl = price*0.996 if side=="BUY" else price*1.004
                    tp = price*1.008 if side=="BUY" else price*0.992
                    txt = f"<b>XAUUSD {price:.2f} — 100% {side} 🔥</b>\n\nScore {score}/5 ✅\n"
                    txt += "\n".join([f"• {r}" for r in reasons])
                    txt += f"\n\nSL {sl:.2f} | TP {tp:.2f}\n\n#XAUUSD"
                    send(txt)
                    last=time.time()
        except Exception as e:
            print(f"LOOP ERR {e}", flush=True)
        time.sleep(900)

threading.Thread(target=loop, daemon=True).start()
@app.route("/")
def home(): return "gold-bot 100% live"
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))
