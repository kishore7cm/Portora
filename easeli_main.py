# main.py
import pandas as pd
import time
import os
import json
from config.api_keys import load_keys
from data.load_portfolio import load_portfolio
from data.target_allocation import build_portfolio, target_allocation
from analysis.fundamentals import get_fundamentals
from analysis.data_fetch import fetch_stock_history, fetch_crypto_history
from analysis.indicators import add_indicators
from analysis.signals import check_technical_signals, trend, score_to_action
from analysis.scoring import intelligent_score,intelligent_score_sp500
from alpaca_trade_api.rest import REST
from news.sentiment import get_news_headlines, analyze_sentiment_gpt

LOOKBACK_DAYS = 100

# Ensure cache folder exists
os.makedirs("cache", exist_ok=True)


def get_cached_news(ticker):
    cache_file = f'cache/{ticker}_news.json'
    if os.path.exists(cache_file):
        try:
            with open(cache_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error reading cache for {ticker}: {e}")

    headlines = get_news_headlines(ticker)
    if not headlines:
        return []

    time.sleep(2)
    with open(cache_file, 'w') as f:
        json.dump(headlines, f)
    return headlines


def run_sp500_analysis():
    from data.sp500_list import get_sp500_tickers

    keys = load_keys()
    alpaca = REST(keys["api_key"], keys["secret_key"], base_url=keys["base_url"])
    tickers = get_sp500_tickers()
    fundamentals_dict = get_fundamentals(tickers)

    rows = []
    for tk in tickers:
        df = fetch_stock_history(tk, alpaca, lookback_days=LOOKBACK_DAYS)
        if df.empty:
            continue

        df = add_indicators(df)
        latest = df.iloc[-1]
        technicals = check_technical_signals(latest)
        fundamentals = fundamentals_dict.get(tk, {})

        score, reason = intelligent_score_sp500(technicals, fundamentals)
        action = score_to_action(score)

        rows.append({
            "Ticker": tk,
            "RSI": round(latest['RSI'], 2),
            "MACD": round(latest['MACD'], 2),
            "Trend": trend(latest['MA20'], latest['MA50']),
            "Score": score,
            "Reason": reason,
            "Action": action
        })

    return pd.DataFrame(rows)


def run_analysis():
    keys = load_keys()
    alpaca = REST(keys["api_key"], keys["secret_key"], base_url=keys["base_url"])
    twelve_key = keys["twelve_api_key"]
    openai_key = keys["openai_api_key"]

    df, stocks_df, crypto_df = load_portfolio()
    all_tickers = df[df['Classification'] == 'Stock']['Symbol'].dropna().unique().tolist()
    portfolio = build_portfolio(stocks_df, crypto_df)

    # Fundamentals
    fundamentals_dict = get_fundamentals(all_tickers)
    for tk in all_tickers:
        headlines = get_cached_news(tk)
        sentiment, summary = analyze_sentiment_gpt(tk, headlines, openai_key)
        fundamentals_dict[tk]["sentiment"] = sentiment

    # Prices
    price_data = {}
    asset_values = {}
    category_values = {}
    total_value = 0

    for cat in ['stocks', 'crypto']:
        cat_val = 0
        for tk, qty in portfolio[cat].items():
            df_hist = (
                fetch_stock_history(tk, alpaca, LOOKBACK_DAYS)
                if cat == 'stocks'
                else fetch_crypto_history(tk, twelve_key, LOOKBACK_DAYS)
            )
            if df_hist.empty:
                continue

            df_hist = add_indicators(df_hist)
            price_data[tk] = df_hist

            val = qty * df_hist['close'].iloc[-1]
            asset_values[tk] = val
            cat_val += val

        category_values[cat] = cat_val
        total_value += cat_val

    # Add bonds and currencies
    for fixed in ['bonds', 'currencies']:
        category_values[fixed] = portfolio[fixed]
        total_value += portfolio[fixed]
    
    #Health Summary
    health_summary = []
    for cat in ['stocks', 'crypto', 'bonds', 'currencies']:
        act_val = category_values.get(cat, 0)
        tgt_pct = target_allocation.get(cat, 0)
        act_pct = (act_val / total_value) * 100 if total_value else 0
        drift = act_pct - tgt_pct

        health_summary.append({
            "Category": cat,
            "Curr %": round(act_pct, 2),
            "Tgt %": round(tgt_pct, 2),
            "Drift": round(drift, 2)
        })

    # Final recommendations
    recommendations = []

    for cat in ['stocks', 'crypto']:
        tgt_pct = target_allocation[cat]
        act_val = category_values[cat]

        for tk, qty in portfolio[cat].items():
            df_hist = price_data.get(tk)
            if df_hist is None:
                continue

            val = asset_values[tk]
            latest = df_hist.iloc[-1]

            alloc_pct = val / total_value * 100
            tgt_asset_pct = tgt_pct * (val / act_val) if act_val else 0

            technicals = check_technical_signals(latest)
            fundamentals = fundamentals_dict.get(tk, {})
            score, reason = intelligent_score(technicals, fundamentals, 0, alloc_pct, tgt_asset_pct)
            action = score_to_action(score)

            recommendations.append({
                "Category": cat,
                "Ticker": tk,
                "Qty": qty,
                "Curr $": round(val, 2),
                "Curr %": round(alloc_pct, 2),
                "Tgt %": round(tgt_asset_pct, 2),
                "Drift %": round(alloc_pct - tgt_asset_pct, 2),
                "RSI": round(latest['RSI'], 2),
                "MACD": round(latest['MACD'], 2),
                "Market": "Bull" if latest["MACD"] > latest["MACD_Signal"] else "Bear",
                "Trend": trend(latest['MA20'], latest['MA50']),
                "BB U": round(latest['BB_Upper'], 2),
                "BB L": round(latest['BB_Lower'], 2),
                "Vol20d": round(latest['Vol_20d'], 2),
                "Score": score,
                "Action": action,
                "Sentiment": fundamentals.get("sentiment", "Neutral")
            })


    return pd.DataFrame(recommendations), pd.DataFrame(health_summary)


if __name__ == "__main__":
    print("📈 Easeli Portfolio Advisor - Smart Rebalance MVP")
    final_df = run_analysis()
    print("\n📊 Smart Rebalancing Recommendations:\n")
    print(final_df.to_string(index=False))
