# Module 2 – Workflow Orchestration with Kestra (ELT / ETL)

This module focuses on **workflow orchestration** and **pipeline automation** using **Kestra**, with an emphasis on modern **ELT-based data engineering patterns**.

The goal is to move beyond one-off scripts and understand how production data pipelines are **scheduled, monitored, retried, and backfilled** in real-world systems.

---

## Overview

In this module, we explored how orchestration tools coordinate data pipelines by defining **flows** made up of tasks, triggers, and dependencies.

Key questions addressed:

- How do we automate data pipelines reliably?
- When should we use ETL vs ELT?
- How do we schedule, backfill, and recover failed workflows?
- How do orchestration tools fit into modern cloud-based data platforms?

---

## Technologies Used

- **Kestra** – Workflow orchestration
- **PostgreSQL** – Metadata and state storage
- **Docker & Docker Compose** – Local orchestration environment
- **Google Cloud Storage (conceptual)** – Data lake
- **BigQuery (conceptual)** – Cloud data warehouse

---

## ETL vs ELT: Design Decisions

A key learning outcome of this module was understanding the **trade-offs between ETL and ELT**.

### ELT (Extract → Load → Transform)
Best suited for:
- Large-scale datasets
- Cloud-native architectures
- Analytics-focused workloads

Typical flow:
1. Extract raw data
2. Load directly into a data lake or warehouse (e.g. GCS → BigQuery)
3. Transform data using warehouse compute

**Advantages:**
- Faster ingestion
- Cheaper storage
- Scales well with large datasets
- Leverages cloud-native compute

---

### ETL (Extract → Transform → Load)
Best suited for:
- Smaller datasets
- Sensitive data (PII removal before storage)
- Strict data validation before persistence

**Advantages:**
- More control over data before storage
- Useful when transformations must happen early

---

## Workflow Orchestration with Kestra

Kestra allows pipelines to be defined as **flows**, which describe:

- Tasks to execute
- Dependencies between tasks
- Scheduling rules
- Retry and failure behavior

Each flow represents a complete data pipeline lifecycle.

### Core Concepts

- **Flows**: Define how tasks are executed
- **Tasks**: Individual steps (e.g. extract, load, transform)
- **Triggers**:
  - Time-based (cron schedules)
  - Manual execution
  - Input-based
- **Backfills**:
  - Re-running historical data
  - Recovering from missed schedules

---

## Scheduling and Backfills

One of the most important aspects of production data pipelines is **time-based execution**.

Using Kestra, workflows can be:
- Scheduled via cron expressions
- Backfilled to process historical data
- Re-run safely after failures

This enables:
- Reliable daily/hourly pipelines
- Recovery from downtime
- Consistent data availability for downstream consumers

---

## Pipeline Architecture (Conceptual)

```text
+------------------+
|  Source Data     |
|  (CSV / API)     |
+------------------+
          |
          v
+------------------+
|  Kestra Flow     |
|  (Orchestration)|
+------------------+
          |
          v
+------------------+
|  Data Lake       |
|  (GCS)           |
+------------------+
          |
          v
+------------------+
|  Data Warehouse  |
|  (BigQuery)      |
+------------------+
          |
          v
+------------------+
| Analytics / BI   |
+------------------+
