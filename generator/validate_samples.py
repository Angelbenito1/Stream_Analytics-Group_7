import json
import os
import sys
from datetime import datetime, timezone

ORDER_PATH = "data/sample_json/order_events.jsonl"
COURIER_PATH = "data/sample_json/courier_events.jsonl"

REQUIRED_COMMON = ["event_id", "event_ts", "ingest_ts"]

def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)

def _read_jsonl(path):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append((i, json.loads(line)))
            except Exception as e:
                raise ValueError(f"{path}: invalid JSON at line {i}: {e}")
    return rows

def _check_required_fields(path, rows, required):
    errors = []
    for line_no, r in rows:
        for k in required:
            if k not in r or r[k] is None:
                errors.append(f"{path}: line {line_no}: missing required field '{k}'")
    return errors

def _check_ts_sanity(path, rows):
    errors = []
    now_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    for line_no, r in rows:
        for k in ["event_ts", "ingest_ts"]:
            if k in r and r[k] is not None:
                if not _is_int(r[k]):
                    errors.append(f"{path}: line {line_no}: {k} must be int epoch millis")
                else:
                    if r[k] < 0:
                        errors.append(f"{path}: line {line_no}: {k} negative")
                    if r[k] > now_ms + 7 * 24 * 3600 * 1000:
                        errors.append(f"{path}: line {line_no}: {k} too far in future")
        if "event_ts" in r and "ingest_ts" in r and _is_int(r.get("event_ts")) and _is_int(r.get("ingest_ts")):
            if r["ingest_ts"] < r["event_ts"] - 60 * 60 * 1000:
                errors.append(f"{path}: line {line_no}: ingest_ts way before event_ts (sanity)")
    return errors

def _check_join_ids(path, rows, keys):
    errors = []
    for line_no, r in rows:
        for k in keys:
            if k not in r or r[k] in (None, ""):
                errors.append(f"{path}: line {line_no}: missing join id '{k}'")
    return errors

def _check_enums(path, rows, field, allowed):
    errors = []
    for line_no, r in rows:
        if field in r and r[field] is not None and r[field] not in allowed:
            errors.append(f"{path}: line {line_no}: invalid {field}='{r[field]}' (allowed={sorted(list(allowed))})")
    return errors

def main():
    ok = True
    all_errors = []

    order_rows = _read_jsonl(ORDER_PATH)
    courier_rows = _read_jsonl(COURIER_PATH)

    if not order_rows:
        all_errors.append(f"{ORDER_PATH}: file missing or empty")
        ok = False
    else:
        all_errors += _check_required_fields(ORDER_PATH, order_rows, REQUIRED_COMMON + ["order_id", "restaurant_id", "zone_id"])
        all_errors += _check_ts_sanity(ORDER_PATH, order_rows)
        all_errors += _check_join_ids(ORDER_PATH, order_rows, ["order_id", "restaurant_id", "zone_id"])
        all_errors += _check_enums(ORDER_PATH, order_rows, "event_type", {
        "created",
        "accepted",
        "prep_started",
        "ready_for_pickup",
        "picked_up",
        "delivered",
        "cancelled",
        })

    if not courier_rows:
        all_errors.append(f"{COURIER_PATH}: file missing or empty")
        ok = False
    else:
        all_errors += _check_required_fields(COURIER_PATH, courier_rows, REQUIRED_COMMON + ["courier_id", "zone_id"])
        all_errors += _check_ts_sanity(COURIER_PATH, courier_rows)
        all_errors += _check_join_ids(COURIER_PATH, courier_rows, ["courier_id", "zone_id"])
        all_errors += _check_enums(COURIER_PATH, courier_rows, "event_type", {
            "status_change", "location_update", "assignment", "unassignment"
        })

    if all_errors:
        ok = False
        print("VALIDATION FAILED ❌")
        for e in all_errors[:200]:
            print("-", e)
        if len(all_errors) > 200:
            print(f"... +{len(all_errors)-200} more")
    else:
        print("VALIDATION OK ✅")
        print(f"- orders: {len(order_rows)} events")
        print(f"- couriers: {len(courier_rows)} events")

    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()