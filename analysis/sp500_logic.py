def get_sp500_recommendations():
    from analysis.data_fetch import fetch_stock_history, add_indicators, check_technical_signals
    from analysis.fundamentals import get_fundamentals
    from analysis.scoring import intelligent_score, score_to_action, trend
    import pandas as pd

    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM", "V", "UNH"]
    rows = []

    for tk in tickers:
        hist = fetch_stock_history(tk, alpaca=None, lookback_days=100)  # use cached or dummy Alpaca obj
        if hist.empty:
            continue
        hist = add_indicators(hist)
        latest = hist.iloc[-1]
        fundamentals = get_fundamentals(tk)
        technicals = check_technical_signals(latest)

        # Assume dummy target for scoring
        score, reason = intelligent_score(technicals, fundamentals, 0, 10, 10)
        action = score_to_action(score)

        rows.append({
            "Ticker": tk,
            "RSI": round(latest['RSI'], 2),
            "MACD": round(latest['MACD'], 2),
            "Trend": trend(latest["MA20"], latest["MA50"]),
            "Score": score,
            "Reason": reason,
            "Action": action
        })

    return pd.DataFrame(rows)
