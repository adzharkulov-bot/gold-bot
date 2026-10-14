import os, time, threading, requests
from flask import Flask
from datetime import datetime
import math
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
app = Flask(__name__)

def send(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
        r = requests.post(url, json=data, timeout=10)
        print(f"Telegram response: {r.text}") # ушул маанилүү!
        return r.ok
    except Exception as e:
        print(f"Send error {e}")
        return False

def get_gold():
    """Алтын баасы - эң туруктуу булак"""
    try:
        # GC=F = Gold Futures
        url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=15m&range=5d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        data = r.json()['chart']['result'][0]
        closes = data['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None]
        highs = data['indicators']['quote'][0]['high']
        lows = data['indicators']['quote'][0]['low']
        highs = [h for h in highs if h is not None]
        lows = [l for l in lows if l is not None]
        return closes, highs, lows
    except Exception as e:
        print(f"Gold err {e}")
        return None, None, None

def ema(data, p):
    if len(data) < p: return None
    k = 2/(p+1)
    e = sum(data[:p])/p
    for x in data[p:]:
        e = x*k + e*(1-k)
    return e

def rsi(data, p=14):
    if len(data) < p+1: return 50
    g=l=0
    for i in range(1, p+1):
        d = data[-i] - data[-i-1]
        if d>0: g+=d
        else: l-=d
    if l==0: return 100
    return 100 - (100/(1+g/l))

def analyze_gold():
    closes, highs, lows = get_gold()
    if not closes or len(closes) < 200:
        return None

    price = closes[-1]
    ema20 = ema(closes, 20)
    ema50 = ema(closes, 50)
    ema200 = ema(closes, 200)
    r = rsi(closes, 14)

    # Bollinger
    sma20 = sum(closes[-20:])/20
    std = math.sqrt(sum((x-sma20)**2 for x in closes[-20:])/20)
    upper = sma20 + std*2
    lower = sma20 - std*2

    # ATR
    atr = sum(abs(highs[-i] - lows[-i]) for i in range(1,15)) / 14

    score = 0
    reasons = []
    direction = ""

    # 1. ТРЕНД (30%)
    if price > ema20 > ema50 > ema200:
        score+=30
        direction="BUY"
        reasons.append(f"✅ Күчтүү UPTREND: Баа > EMA20 > EMA50 > EMA200")
    elif price < ema20 < ema50 < ema200:
        score+=30
        direction="SELL"
        reasons.append(f"✅ Күчтүү DOWNTREND: Баа < EMA20 < EMA50 < EMA200")
    elif price > ema50 and ema50 > ema200:
        score+=20
        direction="BUY"
        reasons.append(f"✅ Uptrend: EMA50 > EMA200")
    elif price < ema50 and ema50 < ema200:
        score+=20
        direction="SELL"
        reasons.append(f"✅ Downtrend: EMA50 < EMA200")

    # 2. RSI (20%)
    if direction=="BUY" and 40 < r < 60:
        score+=20
        reasons.append(f"✅ RSI {r:.1f} - Пулбек, кирүүгө идеалдуу")
    elif direction=="SELL" and 40 < r < 60:
        score+=20
        reasons.append(f"✅ RSI {r:.1f} - Пулбек, кирүүгө идеалдуу")
    elif r < 30:
        score+=15
        reasons.append(f"⚠️ RSI {r:.1f} - Oversold, BUY мүмкүн")
        direction="BUY"
    elif r > 70:
        score+=15
        reasons.append(f"⚠️ RSI {r:.1f} - Overbought, SELL мүмкүн")
        direction="SELL"

    # 3. Bollinger (20%)
    if price <= lower*1.002 and direction=="BUY":
        score+=20
        reasons.append(f"✅ Bollinger Lower тийди - Отскок")
    if price >= upper*0.998 and direction=="SELL":
        score+=20
        reasons.append(f"✅ Bollinger Upper тийди - Отскок")

    # 4. Поддержка/Сопротивление
    recent_high = max(highs[-30:-1])
    recent_low = min(lows[-30:-1])
    if price > recent_high and direction=="BUY":
        score+=15
        reasons.append(f"✅ Сопротивление {recent_high:.1f} бузулду - Breakout")
    if price < recent_low and direction=="SELL":
        score+=15
        reasons.append(f"✅ Поддержка {recent_low:.1f} бузулду - Breakdown")

    if score >= 60:
        if direction=="BUY":
            sl = price - atr*1.5
            tp1 = price + atr*1.5
            tp2 = price + atr*3
        else:
            sl = price + atr*1.5
            tp1 = price - atr*1.5
            tp2 = price - atr*3

        emoji = "🟢" if direction=="BUY" else "🔴"

        msg = f"""🏆 *GOLD (XAUUSD) {score}% SETUP {emoji} {direction}*

💰 Баа: `{price:.2f}`
📊 RSI: `{r:.1f}` | EMA20: `{ema20:.1f}` | EMA50: `{ema50:.1f}`

📈 *ТЕХ АНАЛИЗ:*
{chr(10).join(reasons)}

🎯 *СОДА ПЛАНЫ:*
Вход: `{price:.2f}`
SL: `{sl:.2f}` ({abs(price-sl):.1f}$)
TP1: `{tp1:.2f}` (+{abs(tp1-price):.1f}$)
TP2: `{tp2:.2f}` (+{abs(tp2-price):.1f}$)

📏 ATR: `{atr:.2f}` | BB: `{lower:.1f} - {upper:.1f}`

⚠️ 1-2% риск!
🕐 {datetime.now().strftime('%H:%M Bishkek')}

@xauusdakyl"""

        return msg, score
    return None

def loop():
    print("GOLD Bot started")
    send("✅ *GOLD Bot* тех анализ менен иштеп баштады!\n60-100% сетап күтүүдө... @xauusdakyl")
    last=0
    while True:
        try:
            res = analyze_gold()
            if res and time.time()-last>1800: # 30 мүнөттө 1
                send(res[0])
                last=time.time()
            else:
                print(f"No setup {datetime.now()}")
        except Exception as e:
            print(e)
        time.sleep(300)

threading.Thread(target=loop, daemon=True).start()

@app.route('/')
def home():
    c,h,l = get_gold()
    p = c[-1] if c else 0
    return f"GOLD Live {p} - {datetime.now()}"

@app.route('/test')
def test():
    res = analyze_gold()
    if res:
        send(res[0])
        return f"GOLD Signal {res[1]}% sent"
    else:
        c,h,l = get_gold()
        p = c[-1] if c else 0
        r = rsi(c) if c else 0
        send(f"🔍 *GOLD TEST*\n\nБаа: {p:.2f}\nRSI: {r:.1f}\n\n60%+ сетап азыр жок, бирок бот иштеп жатат ✅ Тех анализ иштеп жатат! @xauusdakyl")
        return f"Test sent price {p}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
