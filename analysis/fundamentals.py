from finvizfinance.quote import finvizfinance

def get_fundamentals(tickers):
    fundamentals_dict = {}
    for tk in tickers:
        try:
            stock = finvizfinance(tk)
            fundamentals_dict[tk] = stock.ticker_fundament()
        except:
            fundamentals_dict[tk] = {}
    return fundamentals_dict