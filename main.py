import os
import yfinance as yf
import pandas as pd

# Токендер Render Environment'ден келет
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# --- SMC ФУНКЦИЯЛАРЫ ---

def get_gold_data():
    # Gold 15m data
    data = yf.download("GC=F", period="5d", interval="15m")
    return data

def find_order_block(df):
    # Акыркы 50 свечадан Order Block издейбиз
    # Order Block = Чоң импульстан мурунку акыркы карама-каршы свеча
    df = df.tail(50)
    for i in range(len(df)-5, 2, -1):
        # Күчтүү бычий импульс
        if df['Close'].iloc[i+1] > df['Open'].iloc[i+1] and (df['Close'].iloc[i+1] - df['Open'].iloc[i+1]) > (df['High'].iloc[i] - df['Low'].iloc[i]):
            # Анын алдындагы медвежий свеча - бычий Order Block
            if df['Close'].iloc[i] < df['Open'].iloc[i]:
                return {
                    "type": "BULLISH_OB",
                    "high": float(df['High'].iloc[i]),
                    "low": float(df['Low'].iloc[i]),
                    "price": float(df['Low'].iloc[i])
                }
        # Күчтүү медвежий импульс
        if df['Close'].iloc[i+1] < df['Open'].iloc[i+1] and (df['Open'].iloc[i+1] - df['Close'].iloc[i+1]) > (df['High'].iloc[i] - df['Low'].iloc[i]):
            if df['Close'].iloc[i] > df['Open'].iloc[i]:
                return {
                    "type": "BEARISH_OB",
                    "high": float(df['High'].iloc[i]),
                    "low": float(df['Low'].iloc[i]),
                    "price": float(df['High'].iloc[i])
                }
    return None

def check_strategy():
    df = get_gold_data()
    if df.empty:
        return None

    current_price = float(df['Close'].iloc[-1])
    ob = find_order_block(df)
    if not ob:
        return None

    # Баа Order Block'ка кайтып келдиби?
    # 0.5% жакындык
    distance = abs(current_price - ob['price']) / current_price * 100

    if distance < 0.2: # 0.2% ичине кирсе сигнал
        if ob['type'] == "BULLISH_OB":
            return f"🟢 GOLD BUY SIGNAL (SMC Lite)\n\nБаа бычий Order Block'ка келди\nOB: {ob['low']:.1f} - {ob['high']:.1f}\nУчурдагы баа: {current_price:.1f}\n\nSL: {ob['low']-5:.1f}\nTP: {current_price+15:.1f}\n\nСтратегия: Ликвид + BOS + OB retest"
        else:
            return f"🔴 GOLD SELL SIGNAL (SMC Lite)\n\nБаа медвежий Order Block'ка келди\nOB: {ob['low']:.1f} - {ob['high']:.1f}\nУчурдагы баа: {current_price:.1f}\n\nSL: {ob['high']+5:.1f}\nTP: {current_price-15:.1f}\n\nСтратегия: Ликвид + BOS + OB retest"

    return None

# --- SENIN TEST FUNKSIYANA USHUNU KOSHSUN ---
# def test_signal():
# msg = check_strategy()
# if msg: send_telegram(msg)
# else: send_telegram("Күтүү... баа OB'да эмес")
