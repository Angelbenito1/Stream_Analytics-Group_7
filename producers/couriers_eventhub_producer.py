import io
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from confluent_kafka import Producer
from fastavro import parse_schema, schemaless_writer

import os
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

EVENT_HUB_NAMESPACE = os.getenv("EVENT_HUB_NAMESPACE")
EVENT_HUB_CONNECTION_STRING = os.getenv("EVENT_HUB_DELIVERY_CONNECTION_STRING")
EVENT_HUB_COURIERS_NAME = os.getenv("EVENT_HUB_COURIERS_NAME", "group_7_delivery")

if not EVENT_HUB_NAMESPACE or not EVENT_HUB_CONNECTION_STRING:
    raise ValueError("Missing EVENT_HUB_NAMESPACE or EVENT_HUB_CONNECTION_STRING in .env")

KAFKA_BOOTSTRAP = f"{EVENT_HUB_NAMESPACE}.servicebus.windows.net:9093"

producer_config = {
    "bootstrap.servers": KAFKA_BOOTSTRAP,
    "security.protocol": "SASL_SSL",
    "sasl.mechanism": "PLAIN",
    "sasl.username": "$ConnectionString",
    "sasl.password": EVENT_HUB_CONNECTION_STRING,
    "client.id": "group_7_delivery_producer",
}


def load_avro_schema(schema_path: str):
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    return parse_schema(schema)


def encode_avro(record: dict, schema) -> bytes:
    buf = io.BytesIO()
    schemaless_writer(buf, schema, record)
    return buf.getvalue()


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()} partition={msg.partition()}")


def send_jsonl_file(
    jsonl_path: str,
    schema_path: str = "schemas/courier_events_v1.avsc",
):
    schema = load_avro_schema(schema_path)
    producer = Producer(producer_config)

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            event = json.loads(line)
            payload = encode_avro(event, schema)
            key = str(event["courier_id"]).encode("utf-8")

            producer.produce(
                topic=EVENT_HUB_COURIERS_NAME,
                key=key,
                value=payload,
                callback=delivery_report,
            )

            producer.poll(0)
            time.sleep(0.05)

    producer.flush()


if __name__ == "__main__":
    path = "data/sample_json/courier_events.jsonl"
    if not Path(path).exists():
        raise FileNotFoundError(f"{path} not found")

    send_jsonl_file(path)
    print("Delivery events sent successfully.")
