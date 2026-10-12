def check_100(closes):
    if len(closes)<50: return None, closes[-1], [], 0
    price = closes[-1]
    ema20 = sum(closes[-20:])/20
    ema50 = sum(closes[-50:])/50
    r = rsi(closes)
    
    score_buy=0; score_sell=0; reasons=[]

    # 1. Тренд
    if price > ema50: 
        score_buy+=1; reasons.append(f"Баа EMA50 {ema50:.1f} үстүндө")
    if price < ema50: 
        score_sell+=1; reasons.append(f"Баа EMA50 {ema50:.1f} астында")

    # 2. RSI
    if 45 < r < 70: score_buy+=1; reasons.append(f"RSI {r:.1f} күч")
    if 30 < r < 55: score_sell+=1; reasons.append(f"RSI {r:.1f} алсыз")

    # 3. Импульс - акыркы 3 шам
    if closes[-1] > closes[-2] > closes[-3]: score_buy+=1
    if closes[-1] < closes[-2] < closes[-3]: score_sell+=1

    # 4. EMA20>EMA50 тренд
    if ema20 > ema50: score_buy+=1; reasons.append("EMA20>EMA50 өйдө")
    if ema20 < ema50: score_sell+=1; reasons.append("EMA20<EMA50 ылдый")

    if score_buy>=3: return "BUY", price, reasons, score_buy
    if score_sell>=3: return "SELL", price, reasons, score_sell
    return None, price, reasons, 0
