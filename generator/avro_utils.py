import json
from fastavro import parse_schema, writer, reader

def load_schema(schema_path: str):
    with open(schema_path, "r", encoding="utf-8") as f:
        return parse_schema(json.load(f))

def write_avro_batch(records, schema_path: str, out_path: str):
    schema = load_schema(schema_path)
    with open(out_path, "wb") as out:
        writer(out, schema, records)

def read_avro_batch(avro_path: str):
    with open(avro_path, "rb") as f:
        return [r for r in reader(f)]