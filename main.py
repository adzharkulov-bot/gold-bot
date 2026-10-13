import os, time, threading, requests
from flask import Flask
TOKEN=os.getenv("BOT_TOKEN")
CHANNEL="@xauusdakyl"
SYMBOL="PAXGUSDT"
DISPLAY="XAUUSD"
app=Flask(__name__)
@app.route('/')
def home(): return "XAU PERCENT FIXED LIVE"
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
            j=requests.get(f"{base}?symbol={SYMBOL}&interval=5m&limit={limit}",headers={"User-Agent":"Mozilla/5.0"},timeout=10).json()
            if isinstance(j,list) and len(j)>100:
                c=[float(x[4]) for x in j]
                h=[float(x[2]) for x in j]
                l=[float(x[3]) for x in j]
                v=[float(x[5]) for x in j]
                return c,h,l,v
        except: pass
    return [],[],[],[]

def rsi(c,p=14):
    g=0;l=0
    for i in range(1,p+1):
        d=c[-i]-c[-i-1]
        if d>0: g+=d
        else: l+=abs(d)
    g/=p; l/=p
    return 100-(100/(1+g/l)) if l!=0 else 50

def ema(c,p):
    k=2/(p+1)
    e=sum(c[:p])/p
    for x in c[p:]:
        e=x*k+e*(1-k)
    return e

def loop():
    global LAST
    print("XAU PERCENT FIXED STARTED",flush=True)
    while True:
        try:
            c,h,l,v=get_candles(150)
            if len(c)<120:
                time.sleep(20)
                continue
            price=c[-1]
            e20=ema(c,20); e50=ema(c,50); e200=ema(c,200)
            r=rsi(c)
            e12=ema(c,12); e26=ema(c,26); macd=e12-e26
            sma=sum(c[-20:])/20
            std=(sum((x-sma)**2 for x in c[-20:])/20)**0.5
            bb_up=sma+std*2; bb_low=sma-std*2
            vol_avg=sum(v[-20:])/20
            ah=max(h[-72:-12]); al=min(l[-72:-12])

            score_buy=0; score_sell=0
            if e20>e50>e200: score_buy+=2
            if e20<e50<e200: score_sell+=2
            if e20>e50: score_buy+=1
            if e20<e50: score_sell+=1
            if 40<r<70: score_buy+=1; score_sell+=1
            if r>50 and macd>0: score_buy+=1
            if r<50 and macd<0: score_sell+=1
            if price>bb_low and price<bb_up: score_buy+=1; score_sell+=1
            if v[-1]>vol_avg*1.2: score_buy+=1; score_sell+=1
            if price<e20*1.002 and e20>e50: score_buy+=1
            if price>e20*0.998 and e20<e50: score_sell+=1
            if c[-1]>c[-2]: score_buy+=1
            if c[-1]<c[-2]: score_sell+=1

            percent_buy=min(100,score_buy*10)
            percent_sell=min(100,score_sell*10)
            best=max(percent_buy,percent_sell)
            sig="BUY" if percent_buy>percent_sell else "SELL" if percent_sell>percent_buy else None

            print(f"CHECK GOLD {price:.1f} BUY {percent_buy}% SELL {percent_sell}% -> {sig}",flush=True)

            if best>=60 and sig and time.time()-LAST>1800:
                risk=3.5
                if sig=="BUY":
                    entry=price; sl=entry-risk
                    tp1=entry+risk; tp2=entry+risk*2; tp3=entry+risk*3
                    msg = (f"<b>{DISPLAY} {sig} {best}%</b>\n\n"
                           f"Buy at: {entry:.2f}\n"
                           f"Stop loss: {sl:.2f}\n\n"
                           f"TP1: {tp1:.2f}\n"
                           f"TP2: {tp2:.2f}\n"
                           f"TP3: {tp3:.2f}\n\n"
                           f"RSI:{r:.0f} EMA:{e20:.1f}/{e50:.1f}\n"
                           f"#XAUUSD #{sig}")
                else:
                    entry=price; sl=entry+risk
                    tp1=entry-risk; tp2=entry-risk*2; tp3=entry-risk*3
                    msg = (f"<b>{DISPLAY} {sig} {best}%</b>\n\n"
                           f"Sell at: {entry:.2f}\n"
                           f"Stop loss: {sl:.2f}\n\n"
                           f"TP1: {tp1:.2f}\n"
                           f"TP2: {tp2:.2f}\n"
                           f"TP3: {tp3:.2f}\n\n"
                           f"RSI:{r:.0f} EMA:{e20:.1f}/{e50:.1f}\n"
                           f"#XAUUSD #{sig}")
                if send(msg):
                    LAST=time.time()
            time.sleep(60)
        except Exception as e:
