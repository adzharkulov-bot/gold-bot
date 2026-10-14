@app.route("/test")
def test():
    try:
        df = yf.download("GC=F", period="1d", interval="5m")
        price = float(df['Close'].iloc[-1])
        msg = f"✅ БОТ ИШТЕП ЖАТАТ!\nGOLD баасы: {price:.2f}\nУбакыт: 15-окт\nСтатус: OB күтүлүүдө"
        send_telegram(msg)
        return f"Sent: {msg}"
    except Exception as e:
        return f"Error: {e}"
