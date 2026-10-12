from flask import Flask
import threading, time, requests, os
app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@xauusdakyl"
@app.route('/')
def home(): return "WINLOUH Bot Live ✅"

def send():
    text = """XAUUSD H4
October 12, 2026

- Wyckoff range: 4,111 - 4,193
- Spring: 4,066 LOW swept
- CHOCH: 4,183 broke
- Current: 4,182

Targets: 4,207 / 4,226 HIGH / 4,245
Invalidation: H4 close below 4,111

WINLOUH"""
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={"chat_id":CHANNEL,"text":text})

threading.Thread(target=lambda: (time.sleep(5), send()), daemon=True).start()
app.run(host="0.0.0.0", port=10000)
