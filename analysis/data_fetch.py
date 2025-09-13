# analysis/data_fetch.py
from datetime import datetime, timedelta
import pandas as pd
import requests
from alpaca_trade_api.rest import REST  # using stable alpaca-trade-api v2.3.0


def fetch_crypto_history(symbol, twelve_key, days=100):
    symbol = symbol.replace('-', '/')  # Convert BTC-USD → BTC/USD for Twelve Data  
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": "1day",
        "outputsize": days,
        "apikey": twelve_key
    }
    try:
        r = requests.get(url, params=params).json()
        if "values" not in r:
            print(f"❌ No crypto data for {symbol}: {r}")
            return pd.DataFrame()
        df = pd.DataFrame(r["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)
        df = df.sort_index()
        df["close"] = df["close"].astype(float)
        return df[["close"]]
    except Exception as e:
        print(f"❌ Crypto fetch error ({symbol}): {e}")
        return pd.DataFrame()


def fetch_stock_history(symbol, alpaca, lookback_days=100):
    end = datetime.now()
    start = end - timedelta(days=lookback_days)

    try:
        bars = alpaca.get_bars(
            symbol,
            timeframe="1Day",
            start=start.strftime('%Y-%m-%d'),
            end=end.strftime('%Y-%m-%d'),
            feed='iex'  # use free IEX feed
        ).df

        if bars.empty:
            print(f"⚠️ No data for {symbol} on IEX")
            return pd.DataFrame()

        bars = bars.tz_localize(None)
        bars = bars.rename(columns={"close": "close"})
        return bars[["close"]]

    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return pd.DataFrame()
