# news/sentiment.py
import openai
from finvizfinance.quote import finvizfinance
import time

def get_news_headlines(ticker):
    try:
        stock = finvizfinance(ticker)
        news = stock.ticker_news()

        # Check if news is a list and contains dicts with "Title" keys
        if not isinstance(news, list):
            raise ValueError("News is not a list")
        headlines = [item['Title'] for item in news if isinstance(item, dict) and 'Title' in item]

        # Limit to top 3 headlines
        return headlines[:3]

    except Exception as e:
        print(f"⚠️ Failed to fetch news for {ticker}: {e}")
        return []

def analyze_sentiment_gpt(ticker, headlines, openai_key):
    if not headlines:
        return "Neutral", "No major news headlines found."

    prompt = f"""
Analyze the sentiment of these headlines for the stock {ticker}:

1. {headlines[0]}
2. {headlines[1] if len(headlines) > 1 else ""}
3. {headlines[2] if len(headlines) > 2 else ""}

Classify the sentiment as Positive, Negative, or Neutral. Provide a brief one-line summary as justification.
Return in the format: "Sentiment: <Positive/Neutral/Negative> - Summary: <short explanation>"
"""

    try:
        openai.api_key = openai_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        reply = response.choices[0].message["content"]
        if "Sentiment:" in reply:
            parts = reply.split("Sentiment:")[1].strip().split(" - Summary:")
            sentiment = parts[0].strip()
            summary = parts[1].strip() if len(parts) > 1 else ""
            return sentiment, summary
        return "Neutral", "No clear sentiment detected."
    except Exception as e:
        print(f"⚠️ GPT error for {ticker}: {e}")
        return "Neutral", "Failed to analyze sentiment."
