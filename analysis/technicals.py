import numpy as np
import pandas as pd
import plotly.graph_objects as go


def indicators(df):
    close = df['Close'].astype(float)
    high, low, vol = df['High'].astype(float), df['Low'].astype(float), df['Volume'].astype(float)
    sma20, sma50, sma200 = close.rolling(20).mean(), close.rolling(50).mean(), close.rolling(200).mean()
    ema20, ema50 = close.ewm(span=20, adjust=False).mean(), close.ewm(span=50, adjust=False).mean()
    delta = close.diff()
    gain, loss = delta.clip(lower=0), -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100/(1+rs))
    macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    signal = macd.ewm(span=9, adjust=False).mean()
    tr = pd.concat([high-low, (high-close.shift()).abs(), (low-close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    latest = float(close.iloc[-1])
    last_rsi = float(rsi.iloc[-1]) if pd.notna(rsi.iloc[-1]) else 50
    trend = 'Bullish' if latest > float(sma50.iloc[-1]) and float(sma50.iloc[-1]) > float(sma200.iloc[-1]) else ('Bearish' if latest < float(sma50.iloc[-1]) else 'Mixed')
    avgvol = vol.rolling(20).mean().iloc[-1]
    relvol = float(vol.iloc[-1] / avgvol) if pd.notna(avgvol) and avgvol else np.nan
    setup = 'Pullback' if latest >= float(sma200.iloc[-1]) and 0.97*float(ema20.iloc[-1]) <= latest <= 1.03*float(ema20.iloc[-1]) else ('Breakout watch' if latest > float(close.iloc[-20:-1].max()) else 'No setup')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=close, name='Close'))
    fig.add_trace(go.Scatter(x=df.index, y=sma20, name='SMA 20'))
    fig.add_trace(go.Scatter(x=df.index, y=sma50, name='SMA 50'))
    fig.add_trace(go.Scatter(x=df.index, y=sma200, name='SMA 200'))
    fig.update_layout(height=450, title='Price and moving averages', xaxis_title='Date', yaxis_title='Price (₹)', legend_orientation='h')
    return {'close':latest, 'rsi':last_rsi, 'trend':trend, 'setup':setup, 'rel_volume':relvol, 'sma20':float(sma20.iloc[-1]), 'sma50':float(sma50.iloc[-1]), 'sma200':float(sma200.iloc[-1]), 'ema20':float(ema20.iloc[-1]), 'ema50':float(ema50.iloc[-1]), 'macd':float(macd.iloc[-1]), 'macd_signal':float(signal.iloc[-1]), 'atr':float(atr.iloc[-1]), 'chart':fig}


def technical_score(t):
    score = 0
    score += 8 if t['trend']=='Bullish' else (4 if t['trend']=='Mixed' else 0)
    score += 5 if 45 <= t['rsi'] <= 65 else (2 if 35 <= t['rsi'] <= 70 else 0)
    score += 4 if t['macd'] > t['macd_signal'] else 0
    score += 3 if t['setup'] in ('Pullback','Breakout watch') else 0
    score += 2 if t.get('rel_volume',0) >= 1.2 else 0
    score += 2 if t.get('close',0) > t.get('ema50',0) else 0
    score += 1 if t.get('close',0) > t.get('sma200',0) else 0
    return min(25, score)
