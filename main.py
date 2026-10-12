import os, time, threading, requests
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@xauusdakyl"
app = Flask(__name__)
LAST_SIGNAL_TIME = 0

def send(msg):
    if not TOKEN: return
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHANNEL, "text": msg, "parse_mode":"HTML", "disable_web_page_preview": True}, timeout=10)
    except: pass

def get_price():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=5m&range=1d"
        j = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=10).json()
        closes = j['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None]
        return closes
    except: return None

def check(closes):
    price = closes[-1]
    ema20 = sum(closes[-20:])/20
    ema50 = sum(closes[-50:])/50 if len(closes)>=50 else ema20
    gains=losses=0
    for i in range(1,15):
        d=closes[-i]-closes[-i-1]
        if d>0: gains+=d
        else: losses-=d
    rs = (gains/14)/(losses/14) if losses!=0 else 2
    rsi = 100 - (100/(1+rs))
    buy=0; sell=0
    if price>ema20: buy+=1
    else: sell+=1
    if ema20>ema50: buy+=1
    else: sell+=1
    if 45<rsi<72: buy+=1
    if 28<rsi<55: sell+=1
    if closes[-1]>closes[-2]: buy+=1
    else: sell+=1
    if buy>=3: return "BUY", price, rsi, ema20, ema50, buy
    if sell>=3: return "SELL", price, rsi, ema20, ema50, sell
    return None, price, rsi, ema20, ema50, 0

def loop():
    global LAST_SIGNAL_TIME
    print("LOOP SINGLE MODE", flush=True)
    # Startup бир гана жолу 5 мүнөттөн кийин кетет, дубль болбойт
    time.sleep(10)
    while True:
        try:
            closes=get_price()
            if closes:
                side,price,rsi,ema20,ema50,score = check(closes)
                print(f"Check {price:.2f} {side} {score}", flush=True)
                now=time.time()
                if side and (now-LAST_SIGNAL_TIME)>3600: # 1 саатта 1 сигнал гана
                    sl = price*0.997 if side=="BUY" else price*1.003
                    tp = price*1.006 if side=="BUY" else price*0.994
                    emoji = "🟢" if side=="BUY" else "🔴"
                    txt = f"<b>{emoji} XAUUSD {side} {price:.2f}</b>\n\n"
                    txt+=f"Score: {score}/4 | RSI: {rsi:.1f}\n"
                    txt+=f"EMA20: {ema20:.1f} | EMA50: {ema50:.1f}\n\n"
                    txt+=f"SL: {sl:.2f}\nTP: {tp:.2f}\n\n#GOLD #XAUUSD"
                    send(txt)
                    LAST_SIGNAL_TIME=now
        except Exception as e:
            print(f"err {e}", flush=True)
        time.sleep(300)

threading.Thread(target=loop, daemon=True).start()

@app.route("/")
def home(): return "gold-bot single live"

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))
