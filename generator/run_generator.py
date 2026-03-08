import argparse
import os
import json
import uuid
import random
from datetime import datetime, timedelta

import numpy as np

from generator.config import load_config
from generator.distributions import demand_multiplier, promo_probability
from generator.reference_data import generate_restaurants, generate_couriers
from generator.order_feed import generate_order_lifecycle
from generator.avro_utils import write_avro_batch

def _ensure_dirs(*paths: str) -> None:
    for p in paths:
        os.makedirs(p, exist_ok=True)

def _parse_start(start_iso: str | None) -> datetime:
    if start_iso:
        return datetime.fromisoformat(start_iso)
    return datetime.now()

def _pick_restaurant(restaurants, zone_weights):
    zones = list(zone_weights.keys())
    weights = list(zone_weights.values())
    z = random.choices(zones, weights=weights, k=1)[0]
    candidates = [r for r in restaurants if r["zone_id"] == z]
    return random.choice(candidates) if candidates else random.choice(restaurants)

def _pick_courier(couriers, zone_id):
    candidates = [c for c in couriers if c["zone_id"] == zone_id]
    return random.choice(candidates) if candidates else random.choice(couriers)

def write_jsonl(records: list[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

def generate_orders_stream(cfg: dict) -> list[dict]:
    sim = cfg["simulation"]
    ent = cfg["entities"]
    real = cfg["realism"]
    edge = cfg["edge_cases"]["orders"]

    start_dt = _parse_start(sim.get("start_iso"))
    duration = int(sim["duration_minutes"])
    base_rate = float(sim["orders_per_minute"])

    restaurants = generate_restaurants(ent["n_restaurants"], zone_weights=real["zone_weights"])
    couriers = generate_couriers(ent["n_couriers"], zone_weights=real["zone_weights"])

    events: list[dict] = []

    for minute in range(duration):
        now_dt = start_dt + timedelta(minutes=minute)
        mult = demand_multiplier(now_dt, real["peaks"], real["weekend_multiplier"], real["surge_periods"])
        lam = max(0.0, base_rate * mult)
        n_orders = int(np.random.poisson(lam))

        promo_p = promo_probability(now_dt, real["promo_periods"], base=0.2)

        for _ in range(n_orders):
            order_id = str(uuid.uuid4())
            restaurant = _pick_restaurant(restaurants, real["zone_weights"])
            courier = _pick_courier(couriers, restaurant["zone_id"])

            is_promo = (random.random() < promo_p)
            base_time_ms = int(now_dt.timestamp() * 1000) + random.randint(0, 59) * 1000

            order_events = generate_order_lifecycle(
                order_id,
                restaurant,
                courier,
                duplicate_prob=edge["duplicate_prob"],
                missing_step_prob=edge["missing_step_prob"],
                impossible_duration_prob=edge["impossible_duration_prob"],
                late_ingest_prob=edge["late_ingest_prob"],
                cancel_multiplier=edge["cancel_multiplier"],
                base_time_ms=base_time_ms,
                is_promo_override=is_promo,
            )
            events.extend(order_events)

    return events

def main():
    ap = argparse.ArgumentParser(description="Food-delivery synthetic generator (orders feed).")
    ap.add_argument("--config", type=str, default=None, help="Path to JSON config.")
    ap.add_argument("--seed", type=int, default=None, help="Override seed.")
    ap.add_argument("--duration-min", type=int, default=None, help="Override duration minutes.")
    ap.add_argument("--orders-per-min", type=float, default=None, help="Override base orders/minute.")
    ap.add_argument("--start-iso", type=str, default=None, help="Override start time ISO (YYYY-MM-DDTHH:MM:SS).")
    ap.add_argument("--no-json", action="store_true", help="Disable JSON output.")
    ap.add_argument("--no-avro", action="store_true", help="Disable AVRO output.")
    args = ap.parse_args()

    cfg = load_config(args.config)

    if args.seed is not None:
        cfg["simulation"]["seed"] = args.seed
    if args.duration_min is not None:
        cfg["simulation"]["duration_minutes"] = args.duration_min
    if args.orders_per_min is not None:
        cfg["simulation"]["orders_per_minute"] = args.orders_per_min
    if args.start_iso is not None:
        cfg["simulation"]["start_iso"] = args.start_iso

    seed = int(cfg["simulation"]["seed"])
    random.seed(seed)
    np.random.seed(seed)

    out_json_dir = cfg["output"]["out_dir_json"]
    out_avro_dir = cfg["output"]["out_dir_avro"]
    _ensure_dirs(out_json_dir, out_avro_dir)

    events = generate_orders_stream(cfg)

    if cfg["output"]["write_json"] and not args.no_json:
        write_jsonl(events, os.path.join(out_json_dir, "order_events.jsonl"))

    if cfg["output"]["write_avro"] and not args.no_avro:
        write_avro_batch(events, "schemas/order_events_v1.avsc", os.path.join(out_avro_dir, "order_events.avro"))

    print(f"Generated {len(events)} order events.")

if __name__ == "__main__":
    main()