import json
from copy import deepcopy
from typing import Any, Dict, Optional

DEFAULT_CONFIG: Dict[str, Any] = {
    "simulation": {"duration_minutes": 60, "orders_per_minute": 6, "start_iso": None, "seed": 42},
    "entities": {"n_restaurants": 30, "n_couriers": 60},
    "realism": {
        "weekend_multiplier": 1.15,
        "peaks": [
            {"name": "lunch", "start": "13:00", "end": "15:00", "multiplier": 2.0},
            {"name": "dinner", "start": "20:00", "end": "22:00", "multiplier": 2.5},
        ],
        "zone_weights": {"center": 0.40, "north": 0.20, "south": 0.15, "east": 0.15, "west": 0.10},
        "promo_periods": [{"start": "20:00", "end": "22:00", "promo_probability": 0.55}],
        "surge_periods": [{"start": "21:00", "end": "21:30", "multiplier": 1.5}],
    },
    "edge_cases": {
        "orders": {
            "duplicate_prob": 0.05,
            "missing_step_prob": 0.05,
            "impossible_duration_prob": 0.02,
            "late_ingest_prob": 0.10,
            "cancel_multiplier": 1.0,
        }
    },
    "output": {"write_json": True, "write_avro": True, "out_dir_json": "data/sample_json", "out_dir_avro": "data/sample_avro"},
}

def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = deepcopy(base)
    for k, v in override.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return deepcopy(DEFAULT_CONFIG)
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return _deep_merge(DEFAULT_CONFIG, cfg)