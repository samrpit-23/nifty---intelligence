import math
from .technicals import technical_score


def _num(f, key, default=None):
    try:
        x = f.get(key, default)
        if x is None or x == '': return default
        return float(x)
    except (ValueError, TypeError):
        return default


def score_stock(fund, tech, val):
    # Fundamental 25/100. Missing metrics do not get silently rewarded.
    fscore, known = 0, 0
    roce = _num(fund,'roce'); roe = _num(fund,'roe'); salesg = _num(fund,'sales_growth'); patg = _num(fund,'profit_growth'); de = _num(fund,'debt_equity')
    for metric, pts in [(roce,8),(roe,5),(salesg,5),(patg,5),(de,2)]:
        if metric is not None:
            known += pts
    if roce is not None: fscore += 8 * max(0,min(1,roce/25))
    if roe is not None: fscore += 5 * max(0,min(1,roe/20))
    if salesg is not None: fscore += 5 * max(0,min(1,salesg/20))
    if patg is not None: fscore += 5 * max(0,min(1,patg/25))
    if de is not None: fscore += 2 * max(0,min(1,(1.5-de)/1.5))
    # Fundamental score normalized to 25 only when completeness is sufficient.
    fundamental = round(fscore,1)
    vscore = 0
    mos = val.get('mos_pct')
    if mos is not None: vscore = round(max(0,min(25,(mos+10)/40*25)),1)
    tscore = technical_score(tech)
    risk = 15
    close = float(tech.get('close',0) or 0)
    atr = float(tech.get('atr',0) or 0)
    if close and atr/close > .06: risk -= 3
    if tech.get('trend') == 'Bearish': risk -= 4
    if tech.get('setup') == 'No setup': risk -= 2
    confidence = round((known/25)*100) if known else 0
    # Weight scores without treating missing fundamental/valuation as zero-quality data.
    raw_total = fundamental + vscore + tscore + max(0, risk)  # raw maximum = 90
    composite = round((raw_total / 90) * 100)
    return {'fundamental':fundamental,'valuation':vscore,'technical':tscore,'risk':max(0,risk),'composite':min(100,composite),'confidence':confidence}
