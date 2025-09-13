import pandas as pd

def add_indicators(df):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    roll_up = gain.rolling(window=14, min_periods=14).mean()
    roll_down = loss.rolling(window=14, min_periods=14).mean()
    rs = roll_up / roll_down
    df['RSI'] = 100 - (100 / (1 + rs))
    df['MA20'] = df['close'].rolling(20).mean()
    df['MA50'] = df['close'].rolling(50).mean()
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    std20 = df['close'].rolling(20).std()
    df['BB_Upper'] = df['MA20'] + 2 * std20
    df['BB_Lower'] = df['MA20'] - 2 * std20
    df['Vol_20d'] = std20
    return df