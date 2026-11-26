import yfinance as yf
import pandas as pd


def load_prices(symbol: str, period='2y'):
    ticker = symbol if symbol.endswith('.NS') else f'{symbol}.NS'
    data = yf.download(ticker, period=period, interval='1d', auto_adjust=True, progress=False, threads=False)
    if data is None or data.empty:
        return None
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data = data.dropna(subset=['Close']).copy()
    return data
