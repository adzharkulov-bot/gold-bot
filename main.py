import os, time, threading, requests
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@xauusdakyl"
app = Flask(__name__)

def send(msg):
    if not TOKEN:
        print("NO TOKEN", flush=True)
        return
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHANNEL, "text": msg, "parse_mode":"HTML"}, timeout=10)
    except Exception as e:
        print(f"TG err {e}", flush=True)

def get_price():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=5m&range=1d"
        j = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=10).json()
        closes = j['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None]
        return closes
    except Exception as e:
        print(f"price err {e}", flush=True)
        return None

def check(closes):
    price = closes[-1]
    ema20 = sum(closes[-20:])/20
    ema50 = sum(closes[-50:])/50 if len(closes)>=50 else ema20
    # RSI 14
    gains=0; losses=0
    for i in range(1,15):
        d = closes[-i]-closes[-i-1]
        if d>0: gains+=d
        else: losses-=d
    rs = (gains/14)/(losses/14) if losses!=0 else 2
    rsi = 100 - (100/(1+rs))

    buy=0; sell=0; rea=[]
    if price>ema20: buy+=1; rea.append(f"price>{ema20:.1f}")
    else: sell+=1
    if ema20>ema50: buy+=1; rea.append("EMA20>EMA50")
    else: sell+=1
    if 45<rsi<72: buy+=1; rea.append(f"RSI {rsi:.0f}")
    if 28<rsi<55: sell+=1
    if closes[-1]>closes[-2]: buy+=1
    else: sell+=1

    if buy>=3: return "BUY", price, rea, buy, rsi
    if sell>=3: return "SELL", price, rea, sell, rsi
    return None, price, rea, 0, rsi

def loop():
    print("LOOP STARTED", flush=True)
    send("✅ gold-bot кайра жанды - жаңы SMC light mode")
    while True:
        try:
            closes=get_price()
            if closes:
                side,price,rea,score,rsi = check(closes)
                print(f"Check {price:.2f} {side} score={score} RSI={rsi:.1f}", flush=True)
                if side:
                    send(f"<b>XAU {price:.2f} {side} score={score}/4</b>\n"+ "\n".join(rea))
                    time.sleep(3600) # 1 саат тыныгуу сигналдан кийин
        except Exception as e:
            print(f"loop err {e}", flush=True)
        time.sleep(300)

threading.Thread(target=loop, daemon=True).start()

@app.route("/")
def home():
    return "gold-bot live"

if __name__ == "__main__":
    port = int(os.getenv("PORT",10000))
    app.run(host="0.0.0.0", port=port)
