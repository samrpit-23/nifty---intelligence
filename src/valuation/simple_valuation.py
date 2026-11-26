import numpy as np


def estimate_valuation(history, fundamentals):
    """Very conservative placeholder: valuation is only computed when uploaded EPS is provided.
    This is a PE-based estimate, NOT DCF. DCF belongs in later phase after reliable statements."""
    close = float(history['Close'].iloc[-1])
    eps = fundamentals.get('eps')
    pe_fair = fundamentals.get('fair_pe')
    if eps is None or pe_fair is None or not np.isfinite(float(eps)) or not np.isfinite(float(pe_fair)):
        return {'fair_value':None, 'mos_pct':None, 'note':'Fair value is N/A. Upload fundamentals CSV with EPS and fair_pe. Phase 1 does not fabricate DCF values.'}
    fair_value = max(0, float(eps) * float(pe_fair))
    mos = ((fair_value-close)/fair_value*100) if fair_value else None
    return {'fair_value':fair_value, 'mos_pct':mos, 'note':'PE-based fair value = EPS × user-provided fair PE. This is not a DCF valuation.'}
