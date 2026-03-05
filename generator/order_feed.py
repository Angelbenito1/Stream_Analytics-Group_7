import uuid
import random
import time
from generator.distributions import cancellation_probability


def current_millis():
    return int(time.time() * 1000)


def create_event(order_id, event_type, event_ts, restaurant, zone_id, courier_id=None):
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
        "is_promo": random.random() < 0.2,
        "estimated_delivery_minutes": random.randint(20, 50),
        "version": 1
    }


def generate_order_lifecycle(order_id, restaurant, courier,
                             duplicate_prob=0.05,
                             missing_step_prob=0.05,
                             impossible_duration_prob=0.02):
    
    events = []
    base_time = current_millis()

    prep_time_ms = restaurant["avg_prep_time"] * 60 * 1000
    delivery_time_ms = random.randint(10, 30) * 60 * 1000

    # --- Normal lifecycle ---
    created = create_event(order_id, "created", base_time, restaurant, restaurant["zone_id"])
    accepted = create_event(order_id, "accepted", base_time + 60000, restaurant, restaurant["zone_id"])
    prep_started = create_event(order_id, "prep_started", base_time + 120000, restaurant, restaurant["zone_id"])
    ready = create_event(order_id, "ready_for_pickup", base_time + prep_time_ms, restaurant, restaurant["zone_id"], courier["courier_id"])
    picked = create_event(order_id, "picked_up", base_time + prep_time_ms + 60000, restaurant, restaurant["zone_id"], courier["courier_id"])
    delivered = create_event(order_id, "delivered", base_time + prep_time_ms + delivery_time_ms, restaurant, restaurant["zone_id"], courier["courier_id"])

    lifecycle = [created, accepted, prep_started, ready, picked, delivered]

    # --- Cancellation logic ---
    wait_minutes = (prep_time_ms + delivery_time_ms) / (1000 * 60)
    if random.random() < cancellation_probability(wait_minutes):
        cancel_time = base_time + random.randint(3, 8) * 60 * 1000
        cancelled = create_event(order_id, "cancelled", cancel_time, restaurant, restaurant["zone_id"])
        lifecycle = [created, cancelled]

    # --- Missing step ---
    if random.random() < missing_step_prob and len(lifecycle) > 3:
        lifecycle = [e for e in lifecycle if e["event_type"] != "picked_up"]

    # --- Impossible duration ---
    if random.random() < impossible_duration_prob and lifecycle[-1]["event_type"] == "delivered":
        lifecycle[-1]["event_ts"] = lifecycle[0]["event_ts"] - 300000  # delivered before created

    # --- Duplicates ---
    if random.random() < duplicate_prob:
        lifecycle.append(random.choice(lifecycle))

    # Simulate late arrival
    for event in lifecycle:
        if random.random() < 0.1:
            event["ingest_ts"] += random.randint(5, 30) * 60 * 1000
    
    
    # --- Out-of-order ---
    random.shuffle(lifecycle)

    return lifecycle