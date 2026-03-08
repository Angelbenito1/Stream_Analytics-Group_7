import uuid
import random
import time
from generator.distributions import cancellation_probability

def current_millis():
    return int(time.time() * 1000)

def create_event(order_id, event_type, event_ts, restaurant, zone_id, courier_id=None, is_promo=None):
    return {
        "event_id": str(uuid.uuid4()),
        "order_id": order_id,
        "event_type": event_type,
        "event_ts": event_ts,
        "ingest_ts": current_millis(),
        "restaurant_id": restaurant["restaurant_id"],
        "zone_id": zone_id,
        "courier_id": courier_id,
        "order_value": round(random.uniform(10, 45), 2),
        "is_promo": is_promo if is_promo is not None else (random.random() < 0.2),
        "estimated_delivery_minutes": random.randint(20, 50),
        "version": 1
    }

def generate_order_lifecycle(
    order_id,
    restaurant,
    courier,
    duplicate_prob=0.05,
    missing_step_prob=0.05,
    impossible_duration_prob=0.02,
    late_ingest_prob=0.10,
    cancel_multiplier=1.0,
    base_time_ms=None,
    is_promo_override=None,
):
    base_time = base_time_ms if base_time_ms is not None else current_millis()
    zone_id = restaurant["zone_id"]
    is_promo = is_promo_override

    prep_time_ms = restaurant["avg_prep_time"] * 60 * 1000
    delivery_time_ms = random.randint(10, 30) * 60 * 1000

    created = create_event(order_id, "created", base_time, restaurant, zone_id, is_promo=is_promo)
    accepted = create_event(order_id, "accepted", base_time + 60000, restaurant, zone_id, is_promo=is_promo)
    prep_started = create_event(order_id, "prep_started", base_time + 120000, restaurant, zone_id, is_promo=is_promo)
    ready = create_event(order_id, "ready_for_pickup", base_time + prep_time_ms, restaurant, zone_id, courier["courier_id"], is_promo=is_promo)
    picked = create_event(order_id, "picked_up", base_time + prep_time_ms + 60000, restaurant, zone_id, courier["courier_id"], is_promo=is_promo)
    delivered = create_event(order_id, "delivered", base_time + prep_time_ms + delivery_time_ms, restaurant, zone_id, courier["courier_id"], is_promo=is_promo)

    lifecycle = [created, accepted, prep_started, ready, picked, delivered]

    wait_minutes = (prep_time_ms + delivery_time_ms) / (1000 * 60)
    p_cancel = min(1.0, cancellation_probability(wait_minutes) * float(cancel_multiplier))
    if random.random() < p_cancel:
        cancel_time = base_time + random.randint(3, 8) * 60 * 1000
        cancelled = create_event(order_id, "cancelled", cancel_time, restaurant, zone_id, is_promo=is_promo)
        lifecycle = [created, cancelled]

    if random.random() < missing_step_prob and len(lifecycle) > 3:
        lifecycle = [e for e in lifecycle if e["event_type"] != "picked_up"]

    if random.random() < impossible_duration_prob and lifecycle[-1]["event_type"] == "delivered":
        lifecycle[-1]["event_ts"] = lifecycle[0]["event_ts"] - 300000

    if random.random() < duplicate_prob:
        lifecycle.append(random.choice(lifecycle).copy())

    for ev in lifecycle:
        if random.random() < late_ingest_prob:
            ev["ingest_ts"] += random.randint(5, 30) * 60 * 1000

    random.shuffle(lifecycle)
    return lifecycle