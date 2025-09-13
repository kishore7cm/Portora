import pandas as pd

def load_portfolio(file_path='portfolio/robinhood_portfolio_combined2.csv'):
    df = pd.read_csv(file_path)
    stocks_df = df[df['Classification'].isin(['Stock', 'ETF'])]
    crypto_df = df[df['Classification'] == 'Crypto']
    return df, stocks_df, crypto_df