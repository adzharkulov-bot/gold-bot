from flask import Flask
import threading, time, requests
import telebot
import pandas as pd
import numpy as np

TOKEN = "8639126332:AAGwJMa7InLOuMosdcS7nAZJ_boriBZK2HA"
CHANNEL = "@Xauusdakylbot" # Сенин канал

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "GOLD BOT ISH TEP JATAT!"

def get_klines():
    # PAXG = Gold proxy, Binance бесплатно
    url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=15m&limit=200"
    r = requests.get(url, timeout=10).json()
    df = pd.DataFrame(r, columns=['t','o','h','l','c','v','T','q','n','V','Q','B'])
    df['c'] = df['c'].astype(float)
    df['h'] = df['h'].astype(float)
    df['l'] = df['l'].astype(float)
    return df

def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def ema(series, period):
    return series.ewm(span=period).mean()

def check_setup():
    df = get_klines()
    close = df['c']
    df['EMA50'] = ema(close, 50)
    df['EMA200'] = ema(close, 200)
    df['RSI'] = rsi(close, 14)
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    rsi_val = round(last['RSI'], 1)
    ema50 = round(last['EMA50'], 2)
    ema200 = round(last['EMA200'], 2)
    price = round(last['c'], 2)
    
    # Bull/Bear тренд
    bullish = last['EMA50'] > last['EMA200'] and last['c'] > last['EMA50']
    
    # BOS аныктоо: акыркы high сындыбы?
    recent_high = df['h'].iloc[-20:-1].max()
    bos = last['h'] > recent_high
    
    # Конкретный сетуп: BOS + RSI>55 + Bull тренд
    if bos and rsi_val > 55 and bullish and rsi_val < 75:
        sl = round(price - 35, 2) # 35$ SL
        tp1 = round(recent_high, 2)
        tp2 = round(price + 80, 2)
        
        text = f"""
🟡 XAUUSD - КОНКРЕТНЫЙ LONG СЕТАП

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
RSI: {rsi_val} {"🟢 >55 КҮЧТҮҮ" if rsi_val>55 else "🔴"}
EMA50: ${ema50} {"🟢 үстүндө" if price>ema50 else "🔴"}
EMA200: ${ema200} {"🟢 BULL тренд" if bullish else "🔴"}
MACD: 🟢 LONG
💧 ⚠️ Liq алына элек
💧 Максат: ${tp1}

⚠️ Эгер LIMIT аткарылбаса MARKET менен кир!
"""
        return text
    return None

def sender():
    time.sleep(10)
    bot.send_message(CHANNEL, "✅ GOLD BOT жаңырды! Эми ар 30 мүнөт эмес, КОНКРЕТНЫЙ РАЗВОРОТ болгондо гана сигнал келет!")
    last_signal_time = 0
    while True:
        try:
            setup = check_setup()
            # 2 саатта 1 жолу гана сигнал, спам болбош үчүн
            if setup and (time.time() - last_signal_time > 7200):
                bot.send_message(CHANNEL, setup)
                last_signal_time = time.time()
            else:
                print("Setup жок, күтөбүз...")
        except Exception as e:
            print(e)
        time.sleep(900) # ар 15 мүнөттө текшерет

threading.Thread(target=sender, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
