import yfinance as yf
import pandas as pd
import time, requests, os
from datetime import datetime

# === НАСТРОЙКА ===
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SYMBOL = "GC=F"  # XAUUSD үчүн GC=F, USOIL үчүн CL=F
COOLDOWN = 2 * 3600 # 2 саатта 1 сигнал

last_signal_time = 0
last_type = None

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})

def get_data():
    df = yf.download(SYMBOL, period="2d", interval="5m")
    df.columns = df.columns.get_level_values(0) if hasattr(df.columns, 'get_level_values') else df.columns
    return df

while True:
    try:
        df = get_data()
        # EMA жана RSI
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['RSI'] = 100 - (100 / (1 + df['Close'].pct_change().rolling(14).mean()))

        curr = df.iloc[-1]
        price = float(curr['Close'])
        ema20 = float(curr['EMA20'])
        ema50 = float(curr['EMA50'])
        rsi = float(curr['RSI'])

        # === 1. АККУМУЛЯЦИЯ (Азия) ===
        # Акыркы 12 шам (1 саат = 12*5м) Азия коробкасы
        asia = df.iloc[-80:-20] # кечээки А
