import random
from faker import Faker

fake = Faker()

ZONES = ["north", "south", "east", "west", "center"]

ZONE_WEIGHTS = {
    "center": 0.40,
    "north": 0.20,
    "south": 0.15,
    "east": 0.15,
    "west": 0.10,
}

def weighted_zone(zone_weights=None):
    zw = zone_weights or ZONE_WEIGHTS
    zones = list(zw.keys())
    weights = list(zw.values())
    return random.choices(zones, weights=weights, k=1)[0]

def generate_restaurants(n=30, zone_weights=None):
    restaurants = []
    for i in range(n):
        z = weighted_zone(zone_weights)
        restaurants.append({
            "restaurant_id": f"rest_{i}",
            "name": fake.company(),
            "zone_id": z,
            "avg_prep_time": random.randint(10, 25)
        })
    return restaurants

def generate_couriers(n=60, zone_weights=None):
    couriers = []
    for i in range(n):
        z = weighted_zone(zone_weights)
        couriers.append({
            "courier_id": f"courier_{i}",
            "zone_id": z
        })
    return couriers