# UrbanEats — Real-Time Food Delivery Analytics

Group 7 · Spring 2026

---

## Project Overview

This project implements a real-time data pipeline for food delivery analytics.

It processes two main data streams:
- Orders (customer demand)
- Delivery (courier activity)

The goal is to simulate a real system and generate useful business insights.

---

## Architecture

Data Generator → Event Hubs → Spark → Bronze → Silver → Gold → Dashboard

### Components

1. **Data Generator (Python)**  
   Creates synthetic order and courier data.

2. **Azure Event Hubs**  
   Receives streaming data.  
   Topics:
   - `group_7_orders`
   - `group_7_delivery`

3. **Spark Structured Streaming**  
   Reads data from Event Hubs and processes it.

4. **Azure Blob Storage**  
   Stores processed data (Gold layer).

5. **Streamlit Dashboard**  
   Displays KPIs and analytics.

---

## Data Layers

### Bronze
- Raw ingested data
- Stored as Parquet
- Minimal processing

### Silver
- Cleaned data
- Valid schema
- Filtered records

### Gold

#### Orders KPIs (5-minute windows)
- orders_total
- unique_orders
- delivered_orders
- cancelled_orders
- avg_order_value
- total_revenue
- cancel_rate

#### Demand vs Supply
- waiting_orders
- available_couriers
- demand_supply_ratio

#### Delivery Anomalies
- avg_delivery_minutes
- p95_delivery_minutes
- anomaly_flag

#### System KPIs
- order_events
- delivery_events
- total_events
- active_zones

#### Business KPIs (global)
- unique_orders
- delivered_orders
- cancelled_orders
- total_revenue
- cancel_rate

---

## Dashboard

The dashboard shows:

### Business KPIs
- Unique Orders
- Delivered Orders
- Total Revenue
- Cancellation Rate

### System KPIs
- Order Events
- Delivery Events
- Total Events
- Active Zones

### Visualizations
- Orders over time
- Demand vs supply
- Delivery anomalies

---

## Key Concepts

- Event data is not the same as business data  
  (one order generates multiple events)
- Unique orders represent real activity
- Gold layer is used for reporting
- Dashboard reads Gold data for stability


---

## Use Cases

### Basic
- KPI aggregation

### Intermediate
- Demand vs supply

### Advanced
- Delivery anomaly detection

---

## Notes

- The dashboard uses event-time data
- Data is synthetic but realistic
- The pipeline is fully functional end-to-end

---

## Team

Group 7 · Spring 2026