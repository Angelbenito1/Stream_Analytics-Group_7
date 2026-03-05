import json
import uuid
from fastavro import writer, parse_schema
from generator.reference_data import generate_restaurants, generate_couriers
from generator.order_feed import generate_order_lifecycle


def generate_orders(n_orders=100):
    import random
    from generator.distributions import demand_multiplier
    import time

    restaurants = generate_restaurants()
    couriers = generate_couriers()

    all_events = []

    now = int(time.time() * 1000)
    multiplier = demand_multiplier(now)

    adjusted_orders = int(n_orders * multiplier)

    for _ in range(adjusted_orders):
        order_id = str(uuid.uuid4())
        restaurant = random.choice(restaurants)
        courier = random.choice(couriers)

        events = generate_order_lifecycle(order_id, restaurant, courier)
        all_events.extend(events)

    return all_events


def random_choice(lst):
    import random
    return random.choice(lst)


def save_json(events):
    with open("data/sample_json/order_events.jsonl", "w") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")


def save_avro(events):
    with open("schemas/order_events_v1.avsc") as f:
        schema = parse_schema(json.load(f))

    with open("data/sample_avro/order_events.avro", "wb") as out:
        writer(out, schema, events)


if __name__ == "__main__":
    events = generate_orders(200)
    save_json(events)
    save_avro(events)
    print(f"Generated {len(events)} events successfully.")