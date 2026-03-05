import random
from faker import Faker

fake = Faker()

ZONES = ["north", "south", "east", "west", "center"]

ZONE_WEIGHTS = {
    "center": 0.4,
    "north": 0.2,
    "south": 0.15,
    "east": 0.15,
    "west": 0.1
}
def generate_restaurants(n=30):
    restaurants = []
    for i in range(n):
        restaurants.append({
            "restaurant_id": f"rest_{i}",
            "name": fake.company(),
            "zone_id": random.choices(ZONES, weights=ZONE_WEIGHTS.values())[0],
            "avg_prep_time": random.randint(10, 25)  # minutes
        })
    return restaurants

def generate_couriers(n=60):
    couriers = []
    for i in range(n):
        couriers.append({
            "courier_id": f"courier_{i}",
            "zone_id": random.choice(ZONES)
        })
    return couriers