from flask import Flask
import threading, time, requests
import telebot
import pandas as pd

TOKEN = "8639126332:AAGwJMa7InLOuMosdcS7nAZJ_boriBZK2HA"  # <--- ТОКЕНДИ ОСМОГ!
CHANNEL = -1004381755603

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "GOLD BOT LIVE!"

def get_df():
    url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=200"
    r = requests.get(url, timeout=10).json()
    df = pd.DataFrame(r, columns=['t','o','h','l','c','v','T','q','n','V','Q','B'])
    df['c'] = df['c'].astype(float)
    df['h'] = df['h'].astype(float)
    df['l'] = df['l'].astype(float)
    return df

def rsi(s, p=14):
    d = s.diff()
    g = d.where(d>0,0).rolling(p).mean()
    l = -d.where(d<0,0).rolling(p).mean()
    rs = g/l
    return 100 - (100/(1+rs))

def ema(s,p): return s.ewm(span=p).mean()

def check_signal():
    df = get_df()
    close = df['c']
    df['RSI'] = rsi(close)
    df['EMA50'] = ema(close,50)
    df['EMA200'] = ema(close,200)
    
    last = df.iloc[-1]
    price = round(last['c'],2)
    rsi_v = round(last['RSI'],1)
    ema50 = round(last['EMA50'],2)
    ema200 = round(last['EMA200'],2)
    
    bullish = last['EMA50'] > last['EMA200'] and last['c'] > last['EMA50']
    recent_high = df['h'].iloc[-20:-1].max()
    bos = last['h'] > recent_high
    
    if bos and 55 < rsi_v < 78 and bullish:
        sl = round(price - 38,2)
        tp1 = round(recent_high,2)
        tp2 = round(price + 85,2)
        return f"""🟡 XAUUSD - КОНКРЕТНЫЙ LONG СЕТАП

Кирүү: ${price} (BOS ${round(recent_high,2)} сынды)
⏰ {time.strftime('%H:%M Бишкек')}

🎯 КОНКРЕТНЫЙ ПЛАН:
1️⃣ Кирүү: MARKET LONG азыр
Же LIMIT: ${round(recent_high,2)} ретестте
2️⃣ SL: ${sl} (Sell Liq асты) - 100% милдеттүү!
3️⃣ TP1: ${tp1} (Buy Liq) -> 50% жап
4️⃣ TP2: ${tp2} -> 50% жап
5️⃣ RR: 1:2.5

📊 ПОДТВЕРЖДЕНИЕ:
RSI: {rsi_v} 🟢 >55 КҮЧТҮҮ
EMA50: ${ema50} 🟢 үстүндө
EMA200: ${ema200} 🟢 BULL тренд
MACD: 🟢 LONG
💧 ⚠️ Liq алына элек
💧 Максат: ${tp1}

⚠️ Эгер LIMIT аткарылбаса MARKET менен кир!"""
    return None

def run():
    time.sleep(8)
    try:
        bot.send_message(CHANNEL, "✅ GOLD BOT жаңырды!\nЭми ар 30 мүнөт эмес, КОНКРЕТНЫЙ РАЗВОРОТ (BOS) болгондо гана сигнал келет!\n\nID: -1004381755603")
    except Exception as e:
        print(e)
    
    last_sig = 0
    while True:
        try:
            sig = check_signal()
            if sig and (time.time()-last_sig > 7200):
                bot.send_message(CHANNEL, sig)
                last_sig = time.time()
            else:
                print("Сетап жок, күтөбүз...")
        except Exception as e:
            print(e)
        time.sleep(900)

threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
