# simple finance data fetcher for turkish stocks
# still in early stage, will improve later

import yfinance as yf
import pandas as pd

def get_stock_data(symbol="GARAN.IS"):
    # download last 30 days data
    data = yf.download(symbol, period="30d")
    
    # just return close prices for now
    return data["Close"]

def basic_analysis(prices):
    # very simple analysis, nothing fancy
    change = prices.iloc[-1] - prices.iloc[0]
    pct = (change / prices.iloc[0]) * 100
    
    result = {
        "start_price": float(prices.iloc[0]),
        "end_price": float(prices.iloc[-1]),
        "change": float(change),
        "pct_change": float(pct)
    }
    
    return result
