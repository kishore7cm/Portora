def intelligent_score(technicals, fundamentals, category_drift, alloc_pct, target_pct):
    score = 0
    reasons = []

    # --- Technicals (Weight: 30) ---
    if technicals.get("macd_bull"):
        score += 15
        reasons.append("MACD Bullish")
    elif technicals.get("macd_bear"):
        score -= 15
        reasons.append("MACD Bearish")

    if technicals.get("oversold"):
        score += 10
        reasons.append("RSI Oversold")
    elif technicals.get("overbought"):
        score -= 10
        reasons.append("RSI Overbought")

    # --- Allocation Drift (Weight: 10) ---
    drift = alloc_pct - target_pct
    if drift < -3:
        score += 5
        reasons.append("Underweight")
    elif drift > 3:
        score -= 5
        reasons.append("Overweight")

    try:
        recom = float(fundamentals.get("Recom", 0))
        target_price = float(fundamentals.get("Target Price", 0))
        current_price = float(fundamentals.get("Price", 0))
        peg = float(fundamentals.get("PEG", 0))
        pe = float(fundamentals.get("P/E", 0))
        beta = float(fundamentals.get("Beta", 1))
        short_float = float(fundamentals.get("Short Float", "0%").replace("%", ""))
        eps_growth = float(fundamentals.get("EPS next Y Percentage", "0%").replace("%", ""))
        sales_growth = float(fundamentals.get("Sales Q/Q", "0%").replace("%", ""))
        roe = float(fundamentals.get("ROE", "0%").replace("%", ""))
        debt_eq = float(fundamentals.get("Debt/Eq", 0))
        high_52w = float(fundamentals.get("52W High", 0))
    except:
        return 0, "⚠️ Incomplete data"

    # --- Analyst Recommendation (Weight: 10) ---
    if 0 < recom < 2:
        score += 10
        reasons.append("Strong Analyst Rating")
    elif recom > 3:
        score -= 5
        reasons.append("Weak Analyst Rating")

    # --- Valuation (Weight: 10) ---
    if target_price and current_price < target_price * 0.85:
        score += 5
        reasons.append("Undervalued (vs Target Price)")
    if peg < 1.5 or pe < 15:
        score += 5
        reasons.append("Good Valuation")
    if peg > 3:
        score -= 5
        reasons.append("Overvalued (PEG)")

    # --- Growth (Weight: 10) ---
    if eps_growth > 10 or sales_growth > 10:
        score += 5
        reasons.append("High Growth Potential")

    # --- Profitability & Stability (Weight: 10) ---
    if roe > 15:
        score += 5
        reasons.append("High ROE")
    if debt_eq > 2:
        score -= 5
        reasons.append("High Debt/Equity")

    # --- Risk (Weight: 10) ---
    if beta > 1.5:
        score -= 3
        reasons.append("High Volatility")
    if short_float > 5:
        score -= 3
        reasons.append("High Short Interest")

    # --- Price Location (Weight: 5) ---
    if high_52w and current_price < 0.7 * high_52w:
        score += 3
        reasons.append("Well Below 52W High")
    elif high_52w and current_price > 0.95 * high_52w:
        score -= 3
        reasons.append("Near 52W Peak")
    
    # Add sentiment if passed
    if "sentiment" in fundamentals:
        sentiment = fundamentals["sentiment"]
        if sentiment == "Positive":
            score += 10
            reasons.append("Positive News Sentiment")
        elif sentiment == "Negative":
            score -= 10
            reasons.append("Negative News Sentiment")


    # Final safety check
    return max(min(score, 100), -100), ", ".join(reasons)

def intelligent_score_sp500(technicals, fundamentals):
    reasons = []
    score = 0

    # Technical analysis (weight: 60%)
    if technicals.get("macd_bull"):
        score += 15
        reasons.append("MACD Bullish")
    elif technicals.get("macd_bear"):
        score -= 15
        reasons.append("MACD Bearish")
    
    if technicals.get("overbought"):
        score -= 10
        reasons.append("RSI Overbought")
    elif technicals.get("oversold"):
        score += 10
        reasons.append("RSI Oversold")

    # Fundamentals analysis (weight: 40%)
    try:
        pe = float(fundamentals.get("P/E", 0))
        peg = float(fundamentals.get("PEG", 0))
        roe = float(fundamentals.get("ROE", "0%").replace("%", ""))
        eps_growth = float(fundamentals.get("EPS next Y Percentage", "0%").replace("%", ""))
        
        # Valuation
        if pe > 0 and pe < 20:
            score += 5
            reasons.append("Good P/E")
        if peg > 0 and peg < 1.5:
            score += 5
            reasons.append("Good PEG")
        
        # Growth
        if eps_growth > 10:
            score += 5
            reasons.append("High EPS Growth")
        
        # Profitability
        if roe > 15:
            score += 5
            reasons.append("High ROE")
            
    except (ValueError, TypeError):
        pass  # Skip if fundamentals data is incomplete

    if not reasons:
        return 0, "⚠️ Incomplete data"
    return score, ", ".join(reasons)