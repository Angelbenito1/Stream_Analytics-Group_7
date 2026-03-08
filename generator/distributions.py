from datetime import datetime

def _hhmm_to_minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)

def _tod_minutes(dt: datetime) -> int:
    return dt.hour * 60 + dt.minute

def _in_window(t: int, start: int, end: int) -> bool:
    if start <= end:
        return start <= t <= end
    return t >= start or t <= end

def weekend_multiplier(dt: datetime, weekend_mult: float) -> float:
    return weekend_mult if dt.weekday() >= 5 else 1.0

def peak_multiplier(dt: datetime, peaks: list) -> float:
    t = _tod_minutes(dt)
    mult = 1.0
    for p in peaks:
        s = _hhmm_to_minutes(p["start"])
        e = _hhmm_to_minutes(p["end"])
        if _in_window(t, s, e):
            mult *= float(p.get("multiplier", 1.0))
    return mult

def surge_multiplier(dt: datetime, surges: list) -> float:
    t = _tod_minutes(dt)
    mult = 1.0
    for s in surges:
        start = _hhmm_to_minutes(s["start"])
        end = _hhmm_to_minutes(s["end"])
        if _in_window(t, start, end):
            mult *= float(s.get("multiplier", 1.0))
    return mult

def promo_probability(dt: datetime, promo_periods: list, base: float = 0.2) -> float:
    t = _tod_minutes(dt)
    p = base
    for pr in promo_periods:
        start = _hhmm_to_minutes(pr["start"])
        end = _hhmm_to_minutes(pr["end"])
        if _in_window(t, start, end):
            p = max(p, float(pr.get("promo_probability", p)))
    return min(max(p, 0.0), 1.0)

def demand_multiplier(dt: datetime, peaks: list, weekend_mult: float, surges: list) -> float:
    return weekend_multiplier(dt, weekend_mult) * peak_multiplier(dt, peaks) * surge_multiplier(dt, surges)

def cancellation_probability(wait_time_minutes: float) -> float:
    if wait_time_minutes > 40:
        return 0.30
    if wait_time_minutes > 25:
        return 0.15
    return 0.05