import random
import copy
from typing import List, Dict


def inject_duplicates(events: List[Dict], ratio: float) -> List[Dict]:
    if ratio <= 0:
        return events

    n = int(len(events) * ratio)
    duplicates = [copy.deepcopy(random.choice(events)) for _ in range(n)]
    return events + duplicates


def inject_out_of_order(events: List[Dict], max_delay_ms: int) -> List[Dict]:
    if max_delay_ms <= 0:
        return events

    for e in events:
        if random.random() < 0.3:
            e["ingest_ts"] += random.randint(1, max_delay_ms)

    random.shuffle(events)
    return events


def inject_missing_steps(events: List[Dict], probability: float) -> List[Dict]:
    if probability <= 0:
        return events

    filtered = []
    for e in events:
        if e.get("event_type") == "picked_up" and random.random() < probability:
            continue
        filtered.append(e)

    return filtered


def inject_impossible_durations(events: List[Dict], probability: float) -> List[Dict]:
    if probability <= 0:
        return events

    for e in events:
        if e.get("event_type") == "delivered" and random.random() < probability:
            e["event_ts"] -= random.randint(60_000, 300_000)

    return events