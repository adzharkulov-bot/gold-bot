from flask import Flask
import threading, time, requests
import telebot
import pandas as pd

TOKEN = "8639126332:AAGwJMa7InLOuMosdcS7nAZJ_boriBZK2HA"  # <--- ТОКЕН
CHANNEL = "@xauusdakyl"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "WYCKOFF BOT LIVE!"

def get_h4():
    url = "https://api.binance.com/api/v3/klines?symbol=PAXGUSDT&interval=4h&limit=200"
    r = requests.get(url, timeout=15).json()
    df = pd.DataFrame(r, columns=['t','o','h','l','c','v','T','q','n','V','Q','B'])
    df['c'] = df['c'].astype(float)
    df['h'] = df['h'].astype(float)
    df['l'] = df['l'].astype(float)
    df['o'] = df['o'].astype(float)
    return df

def check_wyckoff():
    df = get_h4()
    
    # Негизги деңгээлдер (сүрөттөн)
    WYCKOFF_LOW = 4111
    WYCKOFF_HIGH = 4193
    SPRING_LOW = 4066
    CHOCH_LEVEL = 4183
    RECENT_HIGH = 4207
    HIGH_LIQ = 4226
    EXT_0272 = 4245
    
    last = df.iloc[-1]
    price = round(last['c'],2)
    
    # Акыркы 10 H4 свечаны текшер
    lows = df['l'].iloc[-10:]
    highs = df['h'].iloc[-10:]
    
    # 1. SPRING болдубу? 4066 чейин сайып кайра 4111 үстүнө чыктыбы?
    spring_detected = (lows.min() <= 4080) and (price > WYCKOFF_LOW)
    
    # 2. CHOCH болдубу? 4183 сындыбы?
    choch_broke = df['c'].iloc[-3:].max() > CHOCH_LEVEL and price > WYCKOFF_HIGH
    
    # 3. FIBO (4066 LOW -> 4207 HIGH)
    low_fib = SPRING_LOW
    high_fib = RECENT_HIGH
    diff = high_fib - low_fib
    fib_0382 = round(high_fib - diff*0.382, 0) # 4153
    fib_05 = round(high_fib - diff*0.5, 0)     # 4140
    fib_0618 = round(high_fib - diff*0.618, 0) # 4120
    fib_0786 = round(high_fib - diff*0.786, 0) # 4097

    # INVALIDATION
    if price < WYCKOFF_LOW:
        return f"""❌ XAUUSD H4 INVALIDATION

Баа {WYCKOFF_LOW} астына жабылды!
Spring жокко чыкты. Кайра LOW {SPRING_LOW} ачылат.

Азыр: ${price}
Күтөбүз."""

    # НЕГИЗГИ СИГНАЛ - Wyckoff + Spring + CHOCH
    if spring_detected and choch_broke and price >= 4145 and price <= 4195:
        return f"""🟡 XAUUSD H4 - WYCKOFF SPRING + CHOCH

📊 Wyckoff range: {WYCKOFF_LOW} - {WYCKOFF_HIGH} (Sep 29 бери)
🌸 Spring: {SPRING_LOW} чейин сайып, {fib_0786} ретест - стоптор жуулду!
💥 CHOCH: {CHOCH_LEVEL} сынды, {WYCKOFF_HIGH} үстү {RECENT_HIGH} - КҮЧ!

Азыркы баа: ${price} - CHOCH ретест!

🎯 КОНКРЕТНЫЙ ПЛАН:
1️⃣ Кирүү: ${fib_0382} (0.382) LIMIT LONG - идеалдуу!
   Альтернатива: ${round(price-15,0)} MARKET кирсе болот
2️⃣ SL: ${WYCKOFF_LOW-10} ({WYCKOFF_LOW} асты) - Invalidation!
3️⃣ TP1: ${RECENT_HIGH} (жакынкы High)
4️⃣ TP2: ${HIGH_LIQ} (HIGH Liq - эң көп Liq!)
5️⃣ TP3: ${EXT_0272} (-0.272 extension)

📈 Сценарий (сүрөттөгүдөй):
• ${round(price-10,0)} → ~4170 bounce
• Акыркы дип {fib_0382} 0.382 - Higher Low
• {RECENT_HIGH} сындырып {HIGH_LIQ} Liq алат
• {EXT_0272} чейин markup!

📐 Fib:
0.382: {fib_0382} ← КИРҮҮ
0.5: {fib_05}
0.618: {fib_0618} - сынса структура бузулат
0.786: {fib_0786}

⚠️ Deeper: {fib_0382} кармабаса {fib_05} колдоо.
Bull {fib_0618} үстүндө сакталат.

⏰ {time.strftime('%H:%M Бишкек')} | WINLOUH стиль"""

    # Күтүү режими
    if price > WYCKOFF_HIGH:
        return None # Жогору кетти, ретест күтөбүз
    
    return None

def run():
    time.sleep(5)
    try:
        bot.send_message(CHANNEL, "✅ WYCKOFF BOT жаңырды!\nЭми Spring + CHOCH + Fib 0.382 логикасы менен иштейт!\n\nxauusd.lou стилинде анализ жөнөтөт!")
    except Exception as e:
        print(e)
    
    last_sig = 0
    while True:
        try:
            msg = check_wyckoff()
            if msg and (time.time() - last_sig > 3600*4): # 4 саатта 1 жолу
                bot.send_message(CHANNEL, msg)
                last_sig = time.time()
                print("Сигнал жөнөтүлдү!")
            else:
                print(f"Күтүү... Баа: Wyckoff текшерилди")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1800) # ар 30 мүнөт текшер

threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
