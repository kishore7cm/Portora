target_allocation = {
    "stocks": 40,
    "crypto": 10,
    "bonds": 20,
    "currencies": 30
}

portfolio = {
    "stocks": {},
    "crypto": {},
    "bonds": 15000,
    "currencies": 37960.68
}

def build_portfolio(stocks_df, crypto_df):
    portfolio["stocks"] = {row.Symbol: row._3 for row in stocks_df.itertuples()}
    portfolio["crypto"] = {row.Symbol: row._3 for row in crypto_df.itertuples()}
    return portfolio