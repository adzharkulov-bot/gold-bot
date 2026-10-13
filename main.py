import requests, time, os, threading
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
app = Flask(__name__)
@app.route('/')
def home(): return "XAUUSD AMD PRO LIVE"

def send(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
    except: pass

def get_data(symbol="GC=F", range_="2d", interval="5m"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_}"
    j = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15).json()['chart']['result'][0]
    q = j['indicators']['quote'][0]
    closes = [x for x in q['close'] if x]
    highs = [x for x in q['high'] if x]
    lows = [x for x in q['low'] if x]
    return closes, highs, lows

def rsi_calc(closes, period=14):
    gains = losses = 0
    for i in range(1, period+1):
        diff = closes[-i] - closes[-i-1]
        if diff > 0: gains += diff
        else: losses += abs(diff)
    if losses == 0: return 70
    rs = (gains/period) / (losses/period)
    return 100 - (100 / (1+rs))

last_sig = 0
def loop():
    global last_sig
    print("AMD PRO STARTED")
    while True:
        try:
            c5, h5, l5 = get_data("GC=F", "2d", "5m")
            c1h, _, _ = get_data("GC=F", "5d", "1h") # H1 тренд

            if len(c5) < 100: time.sleep(60); continue

            price = c5[-1]
            ema20 = sum(c5[-20:])/20
            ema50 = sum(c5[-50:])/50
            ema1h = sum(c1h[-50:])/50
            rsi = rsi_calc(c5)

            # 1. Азия коробкасы
            asia_h = max(h5[-80:-20])
            asia_l = min(l5[-80:-20])

            # 2. Манипуляция текшерүү (Sweep)
            prev = c5[-2]
            sweep_high = prev < asia_h and price > asia_h
            sweep_low = prev > asia_l and price < asia_l

            # 3. Структура (BOS) - коробкадан кайтуу
            bos_sell = price < (asia_h - (asia_h-asia_l)*0.3)
            bos_buy = price > (asia_l + (asia_h-asia_l)*0.3)

            # 4. Скор системасы
            score_sell = 0
            if sweep_high: score_sell+=1
            if ema20 < ema50: score_sell+=1
            if price < ema1h: score_sell+=1 # H1 да SELL болсо
            if bos_sell and rsi < 60: score_sell+=1

            score_buy = 0
            if sweep_low: score_buy+=1
            if ema20 > ema50: score_buy+=1
            if price > ema1h: score_buy+=1
            if bos_buy and rsi > 40: score_buy+=1

            sig = None
            if score_sell >= 3: sig = "SELL"
            if score_buy >= 3: sig = "BUY"

            # Эски катаны оңдоо: H1 BUY болуп турганда SELL бербейбиз
            if sig=="SELL" and price > ema1h and rsi > 52:
                print(f"BLOCKED FAKE SELL - H1 is BUY, RSI {rsi:.1f}")
                sig = None
            if sig=="BUY" and price < ema1h and rsi < 48:
                sig = None

            if sig and (time.time()-last_sig) > 10800: # 3 саатта 1
                sl = asia_h + 6 if sig=="SELL" else asia_l - 6
                tp = asia_l if sig=="SELL" else asia_h
                rr = f"{abs(price-sl):.2f} / {abs(tp-price):.2f}"
                icon = "🔴" if sig=="SELL" else "🟢"
                msg = (f"{icon} <b>XAUUSD {sig} {price:.2f}</b>\n\n"
                       f"Score: {max(score_sell,score_buy)}/4 | RSI: {rsi:.1f}\n"
                       f"EMA20: {ema20:.1f} | EMA50: {ema50:.1f}\n\n"
                       f"SL: {sl:.2f}\nTP: {tp:.2f}\nRR: {rr}\n\n"
                       f"#GOLD #XAUUSD")
                send(msg)
                last_sig = time.time()
                print(f"SENT PRO {sig} Score {max(score_sell,score_buy)}")

            time.sleep(60)
        except Exception as e:
            print(f"ERR {e}"); time.sleep(60)

threading.Thread(target=loop, daemon=True).start()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
