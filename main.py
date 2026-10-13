import os, time, threading, requests
from flask import Flask
TOKEN=os.getenv("BOT_TOKEN")
CHANNEL="@xauusdakyl"
SYMBOL="PAXGUSDT"
DISPLAY="XAUUSD"
app=Flask(__name__)
@app.route('/')
def home(): return "XAU PERCENT LIVE"
LAST=0
def send(m):
    try:
        r=requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHANNEL,"text":m,"parse_mode":"HTML"},timeout=15)
        print(f"SEND {r.status_code}",flush=True)
        return r.ok
    except Exception as e:
        print(f"ERR {e}",flush=True)
        return False
def get_candles(limit=150):
    for base in ["https://data-api.binance.vision/api/v3/klines","https://fapi.binance.com/fapi/v1/klines"]:
        try:
            url=f"{base}?symbol={SYMBOL}&interval=5m&limit={limit}"
            j=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=10).json()
            if isinstance(j,list) and len(j)>100:
                c=[float(x[4]) for x in j];h=[float(x[2]) for x in j];l=[float(x[3]) for x in j];v=[float(x[5]) for x in j]
                return c,h,l,v
        except: pass
    return [],[],[],[]
def rsi(c,p=14):
    g=l_=0.0
    for i in range(1,p+1):
        d=c[-i]-c[-i-1]
        if d>0: g+=d
        else: l_+=abs(d)
    g/=p;l_/=p
    return 100-(100/(1+g/l_)) if l_!=0 else 50
def ema(c,p):
    k=2/(p+1);e=sum(c[:p])/p
    for x in c[p:]: e=x*k+e*(1-k)
    return e
def loop():
    global LAST
    print("XAU PERCENT FIXED STARTED",flush=True)
    while True:
        try:
            c,h,l,v=get_candles(150)
            if len(c)<120: time.sleep(20);continue
            price=c[-1];e20=ema(c,20);e50=ema(c,50);e200=ema(c,200);r=rsi(c);e12=ema(c,12);e26=ema(c,26);macd=e12-e26
            vol_avg=sum(v[-20:])/20
            buy=sell=0
            if e20>e50: buy+=30
            if e20<e50: sell+=30
            if r>50 and macd>0: buy+=20
            if r<50 and macd<0: sell+=20
            if v[-1]>vol_avg: buy+=10;sell+=10
            if e20>e50>e200: buy+=20
            if e20<e50<e200: sell+=20
            if c[-1]>c[-2]: buy+=20
            if c[-1]<c[-2]: sell+=20
            best=max(buy,sell);sig="BUY" if buy>sell else "SELL"
            print(f"CHECK GOLD {price:.1f} BUY {buy}% SELL {sell}% -> {sig}",flush=True)
            if best>=60 and time.time()-LAST>1800:
                risk=3.5
                if sig=="BUY":
                    sl=price-risk;tp1=price+risk;tp2=price+risk*2;tp3=price+risk*3
                    msg="<b>"+DISPLAY+" "+sig+" "+str(best)+"%</b>\n\nBuy at: "+f"{price:.2f}"+"\nSL: "+f"{sl:.2f}"+"\nTP1: "+f"{tp1:.2f}"+"\nTP2: "+f"{tp2:.2f}"+"\nTP3: "+f"{tp3:.2f}"+"\n\nRSI:"+f"{r:.0f}"+" #XAUUSD"
                else:
                    sl=price+risk;tp1=price-risk;tp2=price-risk*2;tp3=price-risk*3
                    msg="<b>"+DISPLAY+" "+sig+" "+str(best)+"%</b>\n\nSell at: "+f"{price:.2f}"+"\nSL: "+f"{sl:.2f}"+"\nTP1: "+f"{tp1:.2f}"+"\nTP2: "+f"{tp2:.2f}"+"\nTP3: "+f"{tp3:.2f}"+"\n\nRSI:"+f"{r:.0f}"+" #XAUUSD"
                if send(msg): LAST=time.time()
            time.sleep(60)
        except Exception as e:
            print(f"LOOP ERR {e}",flush=True);time.sleep(30)
threading.Thread(target=loop,daemon=True).start()
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
