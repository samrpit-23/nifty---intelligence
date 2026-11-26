import streamlit as st
import pandas as pd
from src.data.universe import load_universe
from src.data.prices import load_prices
from src.analysis.technicals import indicators, technical_score
from src.analysis.scoring import score_stock
from src.valuation.simple_valuation import estimate_valuation

st.set_page_config(page_title='Nifty 500 Intelligence', page_icon='📈', layout='wide')
st.title('📈 Nifty 500 Stock Intelligence Scanner')
st.caption('Personal swing research • 5–20 trading sessions • Free data / CSV fallback')

with st.sidebar:
    st.header('Scan settings')
    max_symbols = st.slider('Maximum stocks to scan', 10, 500, 50, step=10)
    period = st.selectbox('Price history', ['1y', '2y', '5y'], index=1)
    min_score = st.slider('Minimum opportunity score', 0, 100, 60)
    refresh = st.button('🔄 Refresh data', type='primary')
    st.markdown('**Data note:** yfinance is an unofficial source. Personal use only; data may be delayed, missing, or inaccurate.')

uploaded_universe = st.sidebar.file_uploader('Upload stock universe CSV (symbol column)', type='csv')
uploaded_fundamentals = st.sidebar.file_uploader('Upload fundamentals CSV (optional)', type='csv')

if uploaded_universe:
    try:
        universe_df = pd.read_csv(uploaded_universe)
        symbols = universe_df['symbol'].dropna().astype(str).str.strip().tolist()
        if 'company' in universe_df.columns:
            company_map = dict(zip(universe_df['symbol'], universe_df['company']))
        else:
            company_map = {}
    except Exception as e:
        st.error(f'Could not read universe CSV: {e}')
        symbols, company_map = load_universe(), {}
else:
    symbols, company_map = load_universe(), {}

if uploaded_fundamentals:
    try:
        fundamentals = pd.read_csv(uploaded_fundamentals)
        fundamentals['symbol'] = fundamentals['symbol'].astype(str).str.upper().str.strip()
        fundamentals = fundamentals.set_index('symbol').to_dict('index')
    except Exception as e:
        st.error(f'Fundamentals CSV error: {e}')
        fundamentals = {}
else:
    fundamentals = {}

symbols = list(dict.fromkeys(symbols))[:max_symbols]
if not symbols:
    st.warning('No symbols loaded. Upload a universe CSV to begin.')
    st.stop()

@st.cache_data(ttl=3600, show_spinner=False)
def run_scan(symbol_list, period, fundamentals_map):
    results = []
    for i, symbol in enumerate(symbol_list):
        try:
            hist = load_prices(symbol, period=period)
            if hist is None or len(hist) < 80:
                continue
            tech = indicators(hist)
            fund = fundamentals_map.get(symbol.upper(), {})
            val = estimate_valuation(hist, fund)
            scores = score_stock(fund, tech, val)
            row = {
                'Symbol': symbol, 'Close': round(float(hist['Close'].iloc[-1]), 2),
                'RSI': round(float(tech.get('rsi', float('nan'))), 1),
                'Trend': tech.get('trend', 'Unknown'),
                'Fundamental': scores['fundamental'], 'Valuation': scores['valuation'],
                'Technical': scores['technical'], 'Risk': scores['risk'],
                'Score': scores['composite'], 'Fair Value': val.get('fair_value'),
                'MOS %': val.get('mos_pct'), 'Setup': tech.get('setup', 'No setup'),
                'Data Confidence': scores['confidence'],
            }
            results.append(row)
        except Exception:
            continue
    return pd.DataFrame(results)


if refresh:
    run_scan.clear()

with st.spinner(f'Scanning {len(symbols)} symbols… (first run can take a while)'):
    results = run_scan(tuple(symbols), period, fundamentals)

if results.empty:
    st.error('No scan results. Try fewer symbols, check connectivity, or upload data files.')
    st.stop()

results = results.sort_values('Score', ascending=False)
qualified = results[results['Score'] >= min_score]

c1,c2,c3,c4 = st.columns(4)
c1.metric('Scanned successfully', len(results))
c2.metric('Score ≥ threshold', len(qualified))
c3.metric('Avg score', round(results['Score'].mean(), 1))
c4.metric('Attractive MOS candidates', int((results['MOS %'].fillna(-999) >= 15).sum()))

st.subheader('🏆 Highest ranked stocks')
show_cols = ['Symbol','Close','Score','Fundamental','Valuation','Technical','Risk','Fair Value','MOS %','RSI','Trend','Setup','Data Confidence']
st.dataframe(qualified[show_cols].head(30), use_container_width=True, hide_index=True)

st.subheader('🔎 Full screener')
sector_filter = st.text_input('Filter symbol (contains)', '')
filtered = results[results['Symbol'].str.contains(sector_filter.upper(), na=False)] if sector_filter else results
st.dataframe(filtered[show_cols], use_container_width=True, hide_index=True)

selected = st.selectbox('Select a stock for detail', results['Symbol'].tolist())
if selected:
    st.subheader(f'📌 {selected} analysis')
    hist = load_prices(selected, period=period)
    tech = indicators(hist)
    val = estimate_valuation(hist, fundamentals.get(selected.upper(), {}))
    a,b,c,d = st.columns(4)
    a.metric('Close', f"₹{float(hist['Close'].iloc[-1]):,.2f}")
    b.metric('Fair value estimate', f"₹{val['fair_value']:,.2f}" if val.get('fair_value') else 'N/A')
    c.metric('Margin of safety', f"{val['mos_pct']:.1f}%" if val.get('mos_pct') is not None else 'N/A')
    d.metric('RSI', f"{tech.get('rsi',float('nan')):.1f}")
    st.plotly_chart(tech['chart'], use_container_width=True)
    st.markdown('**Valuation methodology / caveat**')
    st.info(val.get('note','Valuation data incomplete. Provide financials CSV for a meaningful estimate.'))
    st.json({k:v for k,v in tech.items() if k not in ['chart']})

st.download_button('⬇️ Download ranking CSV', results.to_csv(index=False).encode('utf-8'), 'nifty500_scan.csv', 'text/csv')
st.caption('Research tool only, not a buy/sell recommendation. Scores depend on data completeness and model assumptions. Confirm prices and fundamentals before trading.')
