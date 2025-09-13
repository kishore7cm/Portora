def get_portfolio_recommendations():
    # You already have this logic in your main.py — extract and return the df
    from main import run_analysis
    df = run_analysis(mode="portfolio")
    return df
