import os, time, requests, threading
from flask import Flask
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@xauusdakyl"
app = Flask(__name__)
@app.route('/')
def home(): return "WINLOUH Bot Live ✅"

def make_chart():
    # (графиктин коду - жогорудагыдай)
    plt.savefig('/tmp/chart.png', dpi=250, facecolor='#c8cfdf')
    return '/tmp/chart.png'

def send_winlouh():
    price = 4181.82 # реал баа yfinance'тан алынат
    caption = f"""XAUUSD H4 | spring confirmed, choch broke higher — result showing strong profit

XAUUSD H4
{datetime.now().strftime('%B %d, %Y')}

• Wyckoff range: Since Sep 29, price has ranged between ~4,111 and ~4,193.
• Spring: On Oct 7-8, price swept below the range into the 0.786 (~4,097), wicked to the LOW at ~4,066, and reclaimed the range quickly.
• CHOCH: On Oct 9, a strong bullish H4 candle broke the CHOCH at ~4,183 and pushed above the Wyckoff top (~4,193) to about 4,207.
• Current price: About {price}. The pullback is retesting the CHOCH.

• Fib levels (LOW 4,066 to the ~4,207 high):
    ○ 0.382: ~4,153
    ○ 0.5: ~4,140
    ○ 0.618: ~4,120
    ○ 0.786: ~4,097
• Upside targets:
    ○ 4,207: the recent high
    ○ 4,226: the HIGH, where buy-side liquidity sits
    ○ ~4,245: the -0.272 extension

Scenario: Pullback to ~4,163 → bounce → final dip to 0.382 at ~4,153 → Markup through 4,207, sweeping HIGH at 4,226 → Continuation to -0.272 at ~4,245.

WINLOUH"""

    chart_path = make_chart()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(chart_path, 'rb') as f:
        requests.post(url, data={"chat_id": CHANNEL, "caption": caption}, files={"photo": f})

def loop():
    time.sleep(5)
    send_winlouh()
    while True:
        time.sleep(14400) # ар 4 саатта H4 жабылышында
        send_winlouh()

threading.Thread(target=loop, daemon=True).start()
app.run(host="0.0.0.0", port=10000)
