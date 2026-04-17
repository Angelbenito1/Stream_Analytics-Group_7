import io
import json
import time
from pathlib import Path

from dotenv import load_dotenv
from confluent_kafka import Producer
from fastavro import parse_schema, schemaless_writer

import os


load_dotenv()

EVENT_HUB_NAMESPACE = os.getenv("EVENT_HUB_NAMESPACE")
EVENT_HUB_CONNECTION_STRING = os.getenv("EVENT_HUB_ORDERS_CONNECTION_STRING")
EVENT_HUB_ORDERS_NAME = os.getenv("EVENT_HUB_ORDERS_NAME", "group_7_orders")

if not EVENT_HUB_NAMESPACE or not EVENT_HUB_CONNECTION_STRING:
    raise ValueError("Missing EVENT_HUB_NAMESPACE or EVENT_HUB_CONNECTION_STRING in .env")

KAFKA_BOOTSTRAP = f"{EVENT_HUB_NAMESPACE}.servicebus.windows.net:9093"

producer_config = {
    "bootstrap.servers": KAFKA_BOOTSTRAP,
    "security.protocol": "SASL_SSL",
    "sasl.mechanism": "PLAIN",
    "sasl.username": "$ConnectionString",
    "sasl.password": EVENT_HUB_CONNECTION_STRING,
    "client.id": "group_7_orders_producer",
    "linger.ms": 50,
    "batch.num.messages": 100,
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
        print(
            f"Delivered to topic={msg.topic()} partition={msg.partition()} offset={msg.offset()} key={msg.key().decode('utf-8') if msg.key() else None}"
        )


def send_jsonl_file(
    jsonl_path: str,
    schema_path: str = "schemas/order_events_v1.avsc",
    topic: str = EVENT_HUB_ORDERS_NAME,
    sleep_ms: int = 100,
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
            key = str(event["order_id"]).encode("utf-8")

            producer.produce(topic=topic, key=key, value=payload, callback=delivery_report)
            producer.poll(0)

            if sleep_ms > 0:
                time.sleep(sleep_ms / 1000.0)

    producer.flush()


if __name__ == "__main__":
    path = "data/sample_json/order_events.jsonl"
    if not Path(path).exists():
        raise FileNotFoundError(f"{path} not found. Generate sample data first.")
    send_jsonl_file(path)
    print("Orders events sent successfully.")
    