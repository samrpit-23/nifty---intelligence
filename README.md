# Nifty 500 Stock Intelligence Scanner — Phase 1

Personal research dashboard for swing-trading candidates (5–20 sessions). Uses free price data through yfinance and optional CSV fundamentals.\n

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## CSV inputs

### Universe CSV
Required column: `symbol` (NSE symbol without `.NS`, e.g. RELIANCE). Optional `company` column.

### Fundamentals CSV
Required column: `symbol`; optional columns: `eps`, `fair_pe`, `roce`, `roe`, `sales_growth`, `profit_growth`, `debt_equity`.
All growth/return values should be percentages (e.g. 18 for 18%). `eps` is rupees per share and `fair_pe` is the user's chosen reasonable PE.

A sample template is in `data/fundamentals_template.csv`.

## Data limitations

- Default universe is a small starter list, not all Nifty 500. Upload a current Nifty 500 universe CSV to scan the full index.
- Yahoo/yfinance is unofficial and data can be missing, delayed, adjusted or inaccurate. Confirm data-source terms and personal-use restrictions.
- Phase 1 has technical indicators and a simple user-input PE valuation. It intentionally does NOT fabricate DCF values. DCF requires reliable financial statements, debt, diluted shares, cash flow and capex inputs.
- Scores are research signals only, not predictions or trade recommendations. Missing fundamentals lower confidence and make valuation unavailable.

## Deploy on Streamlit Community Cloud
1. Push repository to GitHub.
2. On Streamlit Community Cloud, create an app from the repository and set `app.py` as entrypoint.
3. Set Python version compatible with dependencies.
4. Deploy. No API keys are required for this starter build.

