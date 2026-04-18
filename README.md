# Stream_Analytics-Group_7

Real-time food delivery streaming simulation project.

This project simulates a real-time food delivery marketplace (orders, couriers, lifecycle events) and implements:

- Synthetic streaming event generation
- AVRO schemas and serialization
- Configurable realism knobs (peaks, weekend effects, surge, promo periods)
- Edge-case injection for streaming correctness testing
- Streaming validation and QA tools

---

## Project Structure

generator/            → Event generators, CLI framework, edge cases, validation  
schemas/              → AVRO schemas  
data/sample_json/     → Generated JSON sample batches  
data/sample_avro/     → Generated AVRO sample batches  
docs/                 → Documentation (AVRO versioning, design notes)  
requirements.txt      → Python dependencies  
README.md             → Project documentation  

---

## Setup (from scratch)

Clone the repository and create a virtual environment:

python -m venv venv  
source venv/bin/activate  
pip install -r requirements.txt  

Python 3.10+ recommended.

---

## Generate Sample Data

Run the generator with configurable parameters:

python -m generator.run_generator --duration-min 5 --orders-per-min 6  

This generates:

- data/sample_json/order_events.jsonl  
- data/sample_json/courier_events.jsonl  
- data/sample_avro/order_events.avro  
- data/sample_avro/courier_events.avro  

---

## Realism Features

The generator includes:

- Lunch demand peak  
- Dinner demand peak  
- Weekend demand multiplier  
- Zone-level demand skew  
- Surge demand periods  
- Promotional periods  
- Poisson arrival process  
- Configurable edge-case probabilities  

All parameters are configurable through the configuration file.

---

## Streaming Correctness & QA

Edge-case injection supports:

- Duplicate events ratio  
- Out-of-order ingestion delay  
- Missing lifecycle steps  
- Impossible durations (negative or unrealistic timestamps)  

To validate generated samples:

python generator/validate_samples.py  

Expected output:

VALIDATION OK ✅  

The validator checks:

- Required fields presence  
- Enum validity  
- Timestamp sanity (event_ts / ingest_ts)  
- Join ID consistency (order_id, courier_id, zone_id)  

---

## AVRO Support

- Schemas stored in schemas/  
- AVRO utilities implemented in generator/avro_utils.py  
- Versioning guidelines documented in docs/avro_versioning.md  

Sample AVRO batches are generated automatically with the CLI.

---

## Authors & Responsibilities

Feed A (Orders): Angel Benito 
Feed B (Couriers): Juan Muñoz
AVRO & Versioning: Bruno Sanchis
Generator Framework & Realism: Francisco Javier Roca 
Streaming Correctness & QA: Yago Moreno
Integration & Documentation: Andrés Ramírez

---

## Milestone 1 Completion

The project includes:

- Two streaming feeds  
- AVRO schemas and serialization  
- Configurable generator framework  
- Realistic event simulation  
- Edge-case injection  
- Validation tools  
- Sample JSON and AVRO batches  

All components are integrated and validated.
