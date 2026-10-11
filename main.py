from flask import Flask
import threading, time, requests
import telebot

TOKEN = "8639126332:AAGwJMa7InLOuMosdcS7nAZJ_boriBZK2HA"
CHANNEL = "@XAUUSDAKYL"  # мисалы @akyl_gold_signal

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "GOLD BOT ISH TEP JATAT!"

def get_price():
    try:
        r = requests.get("https://api.gold-api.com/price/XAU", timeout=10).json()
        return r['price']
    except:
        return 4193.99

def sender():
    time.sleep(5)
    try:
        bot.send_message(CHANNEL, "✅ GOLD BOT каналга кошулду! Ар 30 мүнөттө баа келет!")
    except Exception as e:
        print(f"Channel error: {e}")
    
    while True:
        try:
            p = get_price()
            msg = f"🟡 XAUUSD: ${p} | {time.strftime('%H:%M')} Bishkek"
            bot.send_message(CHANNEL, msg)
        except Exception as e:
            print(e)
        time.sleep(1800) # 30 minut

threading.Thread(target=sender, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
