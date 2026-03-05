
Each state transition is emitted as an independent immutable event.

This design reflects real-world event-driven architectures used in production systems, where systems communicate through events rather than state updates.

The lifecycle-based modeling enables:

- Time-based performance analysis  
- State reconstruction  
- SLA monitoring  
- Bottleneck identification  

---

## 3. Schema Design Considerations

The AVRO schema was designed following production-grade streaming principles.

### a) Event-Time Processing

Two timestamps are included:

- `event_ts` → when the event actually occurred (event-time)
- `ingest_ts` → when the event was generated/ingested (processing-time)

This distinction enables:

- Event-time windowing
- Watermark handling
- Late data management
- Accurate SLA calculations

---

### b) Deduplication Support

- `event_id` is globally unique.
- Enables idempotent processing in streaming systems.
- Allows downstream systems to drop duplicates safely.

---

### c) Stream Joins

Identifiers included:

- `order_id`
- `restaurant_id`
- `courier_id`
- `zone_id`

These support:

- Stream-table joins with reference datasets
- Zone-level aggregations
- Restaurant performance benchmarking
- Courier performance tracking

---

### d) Schema Evolution & Robustness

The schema includes:

- A `version` field for forward compatibility.
- Enum type for `event_type` to prevent invalid states.
- Optional `courier_id` (nullable) to reflect lifecycle progression.
- Logical type `timestamp-millis` for proper time semantics.

This ensures future evolution without breaking consumers.

---

## 4. Realism and Data Distribution

The generator introduces realistic marketplace patterns.

### Demand Peaks

Order volume increases during:

- Lunch peak (13:00–15:00)
- Dinner peak (20:00–22:00)

This simulates real-world demand surges.

---

### Zone-Level Skew

Zones are weighted differently to simulate urban density patterns.

For example:

- “center” zone has higher demand concentration.
- Peripheral zones have lower order frequency.

This enables supply-demand imbalance analysis.

---

### Cancellation Logic

Cancellation probability increases with estimated wait time.

Longer delivery times result in higher cancellation risk, reflecting real customer behavior.

---

## 5. Streaming Correctness & Edge Cases

To properly test streaming systems (e.g., Spark Structured Streaming), the generator intentionally produces:

- Out-of-order events  
- Duplicate events  
- Missing lifecycle steps  
- Impossible durations (e.g., delivered before created)  
- Late ingestion timestamps  

These edge cases allow demonstration of:

- Watermarks  
- Event-time windowing  
- Stateful processing  
- Deduplication strategies  
- Data quality validation  

---

## 6. Analytical Use Cases Enabled

This stream enables:

- Windowed order volume metrics  
- Average preparation and delivery time  
- Cancellation rate by zone  
- SLA breach detection  
- Restaurant performance benchmarking  
- Anomaly detection  
- Demand forecasting  
- Revenue estimation  

---

## 7. Conclusion

The `order_events` feed models the operational backbone of a food delivery marketplace.

It combines:

- Business realism  
- Proper event-time modeling  
- Schema evolution readiness  
- Streaming correctness challenges  

This design ensures the feed is suitable for real-time analytics pipelines and production-grade stream processing systems.