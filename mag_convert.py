
import datetime as _dt

_PERIODS = [
    ((1900,1,1), (1965,12,31),  {'ge7': (1.06, -0.58), 'lt7': (0.74, 1.64)}),
    ((1966,1,1), (1975,12,31),  {'ge7': (1.05, -0.90), 'lt7': (0.62, 2.13)}),
    ((1976,1,1), (2015,12,31),  {'ge7': (1.28, -2.42), 'lt7': (0.86, 0.59)}),
]

def _parse_date_ddmmyyyy(date_str: str) -> _dt.date:
    s = str(date_str).strip().replace('/', '').replace('-', '')
    if len(s) != 8 or not s.isdigit():
        raise ValueError("Event date must be DDMMYYYY, e.g., 12071927.")
    d, m, y = int(s[:2]), int(s[2:4]), int(s[4:])
    return _dt.date(y, m, d)

def _period_params(date_str: str):
    d = _parse_date_ddmmyyyy(date_str)
    for (a, b, params) in _PERIODS:
        start = _dt.date(*a); end = _dt.date(*b)
        if start <= d <= end: return params
    return _PERIODS[-1][2]

def ms_to_mw(ms: float, date_str: str) -> float:
    params = _period_params(date_str)
    a, b = params['ge7'] if ms >= 7.0 else params['lt7']
    return a*float(ms) + b

def mw_to_ms(mw: float, date_str: str) -> float:
    params = _period_params(date_str)
    a_ge, b_ge = params['ge7']; ms_ge = (float(mw) - b_ge)/a_ge
    if ms_ge >= 7.0: return ms_ge
    a_lt, b_lt = params['lt7']; return (float(mw) - b_lt)/a_lt
