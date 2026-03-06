import uuid
import random
import time
import json
from fastavro import writer, parse_schema
from generator.reference_data import generate_couriers, ZONES

DEFAULT_N_COURIERS = 60
DUPLICATE_PROB = 0.05
LATE_INGEST_PROB = 0.1
OFFLINE_MID_DELIVERY_PROB = 0.05

ZONE_COORDS = {
    "north": (40.450, -3.700),
    "south": (40.380, -3.700),
    "east": (40.410, -3.650),
    "west": (40.410, -3.750),
    "center": (40.4168, -3.7038),
}

def current_millis():
    return int(time.time() * 1000)

def jitter_location(zone_id):
    base_lat, base_lon = ZONE_COORDS.get(zone_id, ZONE_COORDS["center"])
    return (
        round(base_lat + random.uniform(-0.01, 0.01), 6),
        round(base_lon + random.uniform(-0.01, 0.01), 6),
    )

def create_event(
    courier_id,
    event_type,
    courier_status,
    event_ts,
    zone_id,
    order_id=None,
    latitude=0.0,
    longitude=0.0,
):
    return {
        "event_id": str(uuid.uuid4()),
        "courier_id": courier_id,
        "event_type": event_type,
        "courier_status": courier_status,
        "event_ts": event_ts,
        "ingest_ts": current_millis(),
        "zone_id": zone_id,
        "order_id": order_id,
        "latitude": latitude,
        "longitude": longitude,
        "version": 1,
    }

def simulate_courier_activity(courier):
    events = []
    courier_id = courier["courier_id"]
    zone_id = courier.get("zone_id", random.choice(ZONES))
    base_time = current_millis()

    events.append(create_event(
        courier_id, "status_change", "idle", base_time, zone_id
    ))

    if random.random() < 0.7:
        order_id = str(uuid.uuid4())

        events.append(create_event(
            courier_id,
            "assignment",
            "moving_to_pickup",
            base_time + 5000,
            zone_id,
            order_id=order_id
        ))

        for i in range(3):
            lat, lon = jitter_location(zone_id)
            events.append(create_event(
                courier_id,
                "location_update",
                "moving_to_pickup",
                base_time + 10000 + i * 5000,
                zone_id,
                order_id=order_id,
                latitude=lat,
                longitude=lon
            ))

        events.append(create_event(
            courier_id,
            "status_change",
            "waiting_at_restaurant",
            base_time + 30000,
            zone_id,
            order_id=order_id
        ))

        if random.random() < OFFLINE_MID_DELIVERY_PROB:
            events.append(create_event(
                courier_id,
                "status_change",
                "offline",
                base_time + 40000,
                zone_id,
                order_id=order_id
            ))
        else:
            events.append(create_event(
                courier_id,
                "status_change",
                "delivering",
                base_time + 40000,
                zone_id,
                order_id=order_id
            ))

            lat, lon = jitter_location(zone_id)
            events.append(create_event(
                courier_id,
                "location_update",
                "delivering",
                base_time + 50000,
                zone_id,
                order_id=order_id,
                latitude=lat,
                longitude=lon
            ))

            events.append(create_event(
                courier_id,
                "unassignment",
                "idle",
                base_time + 60000,
                zone_id,
                order_id=order_id
            ))

    if random.random() < DUPLICATE_PROB:
        events.append(random.choice(events).copy())

    for e in events:
        if random.random() < LATE_INGEST_PROB:
            e["ingest_ts"] += random.randint(5, 20) * 60 * 1000

    random.shuffle(events)

    return events

def generate_courier_events(n_couriers=DEFAULT_N_COURIERS):
    couriers = generate_couriers(n_couriers)
    all_events = []

    for courier in couriers:
        events = simulate_courier_activity(courier)
        all_events.extend(events)

    return all_events

def save_json(events):
    with open("data/sample_json/courier_events.jsonl", "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

def save_avro(events):
    with open("schemas/courier_events_v1.avsc") as f:
        schema = parse_schema(json.load(f))

    with open("data/sample_avro/courier_events.avro", "wb") as out:
        writer(out, schema, events)

if __name__ == "__main__":
    events = generate_courier_events()
    save_json(events)
    save_avro(events)
    print(f"Generated {len(events)} courier events.")

    