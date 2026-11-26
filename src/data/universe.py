import pandas as pd


# Small fallback universe for first launch. Upload a symbol CSV for broader coverage.
FALLBACK_SYMBOLS = [
    'RELIANCE','TCS','HDFCBANK','ICICIBANK','INFY','SBIN','BHARTIARTL','ITC','LT','HINDUNILVR',
    'AXISBANK','KOTAKBANK','BAJFINANCE','MARUTI','SUNPHARMA','TATAMOTORS','NTPC','POWERGRID','ONGC',
    'TATASTEEL','JSWSTEEL','ULTRACEMCO','ASIANPAINT','TITAN','BEL','HAL','TRENT','DMART','PIDILITIND',
    'RRKABEL','MUTHOOTFIN','APTUS','DATAPATTERN','WELCORP'
]

def load_universe():
    """Returns a modest fallback list. Use uploaded CSV with 'symbol' column for Nifty 500."""
    return FALLBACK_SYMBOLS.copy(), {}
