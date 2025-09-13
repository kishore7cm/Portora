import pandas as pd

def check_technical_signals(latest):
    rsi = latest["RSI"]
    macd = latest["MACD"]
    macd_sig = latest["MACD_Signal"]
    price = latest["close"]
    bb_upper = latest["BB_Upper"]
    bb_lower = latest["BB_Lower"]
    return {
        "overbought": (rsi > 70) or (price > bb_upper),
        "oversold": (rsi < 30) or (price < bb_lower),
        "macd_bear": macd < macd_sig,
        "macd_bull": macd > macd_sig
    }

def trend(ma20, ma50):
    return "↗️ Up" if ma20 > ma50 else "↘️ Down" if not pd.isna(ma20) and not pd.isna(ma50) else "N/A"

def score_to_action(score):
    if score >= 70:
        return "✅ Strong Buy"
    elif 40 <= score < 70:
        return "🔄 Optional Buy"
    elif -39 <= score <= 39:
        return "❌ Hold"
    elif -69 <= score < -40:
        return "🔄 Optional Sell"
    else:
        return "✅ Strong Sell"