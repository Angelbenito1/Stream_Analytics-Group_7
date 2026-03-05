from datetime import datetime

def demand_multiplier(timestamp_ms):
    hour = datetime.fromtimestamp(timestamp_ms / 1000).hour

    # Lunch peak
    if 13 <= hour <= 15:
        return 2.0

    # Dinner peak
    if 20 <= hour <= 22:
        return 2.5

    return 1.0


def cancellation_probability(wait_time_minutes):
    if wait_time_minutes > 40:
        return 0.30
    if wait_time_minutes > 25:
        return 0.15
    return 0.05