# Urban Flow Monitor --- Real-Time Food Delivery Analytics

Group 7 · Spring 2026

------------------------------------------------------------------------

## Project Overview

This project implements a real-time data pipeline for food delivery analytics.

It processes two main data streams: - Orders (customer demand) - Delivery (courier activity)

The goal is to simulate a real system and generate useful business insights.

------------------------------------------------------------------------

## Architecture

Data Generator → Event Hubs → Spark → Bronze → Silver → Gold → Dashboard

### Components

1.  **Data Generator (Python)**\
    Creates synthetic order and courier data.

2.  **Azure Event Hubs**\
    Receives streaming data.\
    Topics:

    -   `group_7_orders`
    -   `group_7_delivery`

3.  **Spark Structured Streaming**\
    Reads data from Event Hubs and processes it.

4.  **Azure Blob Storage**\
    Stores processed data (Gold layer).

5.  **Streamlit Dashboard**\
    Displays KPIs and analytics.

------------------------------------------------------------------------

## Data Layers

### Bronze

-   Raw ingested data
-   Stored as Parquet
-   Minimal processing

### Silver

-   Cleaned data
-   Valid schema
-   Filtered records

### Gold

#### Orders KPIs (5-minute windows)

-   orders_total
-   unique_orders
-   delivered_orders
-   cancelled_orders
-   avg_order_value
-   total_revenue
-   cancel_rate

#### Demand vs Supply

-   waiting_orders
-   available_couriers
-   demand_supply_ratio

#### Delivery Anomalies

-   avg_delivery_minutes
-   p95_delivery_minutes
-   anomaly_flag

#### System KPIs

-   order_events
-   delivery_events
-   total_events
-   active_zones

#### Business KPIs (global)

-   unique_orders
-   delivered_orders
-   cancelled_orders
-   total_revenue
-   cancel_rate

------------------------------------------------------------------------

## How to Run the Pipeline

### 1. Activate environment

``` bash
source venv/bin/activate
```

### 2. Generate data

``` bash
python -m generator.run_generator --duration-min 10 --orders-per-min 6
```

### 3. Send data to Event Hubs

``` bash
python producers/orders_eventhub_producer.py
python producers/couriers_eventhub_producer.py
```

### 4. Run ingestion notebook

Open: `notebooks/01_eventhub_spark_ingestion.ipynb`

-   Connects to Event Hubs\
-   Parses events\
-   Writes Bronze data

### 5. Run analytics notebooks

Basic and intermediate: `notebooks/02_analytics_use_cases.ipynb`

Advanced: `notebooks/03_advanced_analytics.ipynb`

### 6. Build Silver and Gold

`notebooks/04_gold_outputs_and_blob.ipynb`

-   Creates Silver data\
-   Builds Gold datasets\
-   Writes to Azure Blob\
-   Exports local data for dashboard

### 7. Run dashboard

``` bash
streamlit run dashboard/app.py
```

------------------------------------------------------------------------

## Dashboard

The dashboard shows:

### Business KPIs

-   Unique Orders
-   Delivered Orders
-   Total Revenue
-   Cancellation Rate

### System KPIs

-   Order Events
-   Delivery Events
-   Total Events
-   Active Zones

### Visualizations

-   Orders over time
-   Demand vs supply
-   Delivery anomalies

------------------------------------------------------------------------

## Key Concepts

-   Event data is not the same as business data\
    (one order generates multiple events)
-   Unique orders represent real activity
-   Gold layer is used for reporting
-   Dashboard reads Gold data for stability

------------------------------------------------------------------------

## Project Structure

```         
.
├── generator/
├── producers/
├── notebooks/
│   ├── 01_eventhub_spark_ingestion.ipynb
│   ├── 02_analytics_use_cases.ipynb
│   ├── 03_advanced_analytics.ipynb
│   └── 04_gold_outputs_and_blob.ipynb
├── dashboard/
│   └── app.py
├── data/
│   ├── bronze/
│   ├── gold/
├── schemas/
├── requirements.txt
└── README.md
```

------------------------------------------------------------------------

## Use Cases

### Basic

-   KPI aggregation

### Intermediate

-   Demand vs supply

### Advanced

-   Delivery anomaly detection

------------------------------------------------------------------------

## Notes

-   The dashboard uses event-time data
-   Data is synthetic but realistic
-   The pipeline is fully functional end-to-end

------------------------------------------------------------------------

## Team

Group 7 · Spring 2026
