# NYC Taxi Data Engineering - November 2025

This project demonstrates a complete **end-to-end data engineering pipeline** for NYC taxi data. The workflow includes **data ingestion from CSV and Parquet**, preprocessing, storing the data in a PostgreSQL database, and running everything inside **Docker containers**.

---

## Table of Contents

- [Project Overview](#project-overview)  
- [Project Structure](#project-structure)  
- [Setup and Environment](#setup-and-environment)  
- [Ingesting Data](#ingesting-data)  
- [Dockerizing the Pipeline](#dockerizing-the-pipeline)  
- [Running the Pipeline](#running-the-pipeline)  
- [Jupyter Notebook](#jupyter-notebook)  
- [SQL Queries](#sql-queries)  
- [Architecture Diagram](#architecture-diagram)

---

## Project Overview

We are working with **NYC Green and Yellow Taxi data** for November 2025.  

Goals:

1. Pull taxi data in CSV or Parquet format from public URLs.  
2. Preprocess data:  
   - Convert date columns to `datetime`  
   - Convert numeric IDs from `float` to `int`  
   - Handle missing values (`NaN` / `<NA>`)  
3. Ingest data into a **PostgreSQL database** using **SQLAlchemy**.  
4. Perform analytical queries such as:
   - Count of trips by distance  
   - Pickup zones with the largest revenue  
   - Dropoff zones with the largest tips  

All scripts are CLI-friendly using `click` for easy parameterization.

---

## Project Structure

```
homework1-ingest/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
├── homework1-nov-ingest.py       # Main ingestion script
├── homework1-lookup-ingest.py    # CSV lookup table ingestion
├── notebooks/                     # Optional Jupyter notebooks
└── README.md
```

---

## Setup and Environment

We use **uv** (Universal Virtual Environment) to manage dependencies and virtual environments.

### Install `uv`

```bash
pip install uv
```

### Create virtual environment and install dependencies

```bash
uv sync --locked
```

- This creates a `.venv` folder and installs all dependencies from `pyproject.toml` and `uv.lock`.  
- Activate the environment:

```bash
uv activate
```

---

## Ingesting Data

The ingestion script supports both **CSV** and **Parquet** files.  

### CLI Parameters

- `--pipeline [parquet|csv]` (required)  
- `--pg-user` PostgreSQL username  
- `--pg-pass` PostgreSQL password  
- `--pg-host` PostgreSQL host  
- `--pg-port` PostgreSQL port  
- `--pg-db` PostgreSQL database  
- `--year` Year of data  
- `--month` Month of data  
- `--chunksize` Chunk size for ingestion  
- `--target-table` Target SQL table name  
- `--csv-url` URL for CSV data (only if using CSV pipeline)

### Example Usage

#### Parquet

```bash
python homework1-nov-ingest.py \
  --pipeline parquet \
  --pg-user root \
  --pg-pass root \
  --pg-host pgdatabase \
  --pg-port 5432 \
  --pg-db ny_taxi \
  --year 2025 \
  --month 11 \
  --chunksize 100000 \
  --target-table yellow_taxi_trips_nov_2025
```

#### CSV

```bash
python homework1-lookup-ingest.py \
  --pipeline csv \
  --pg-user root \
  --pg-pass root \
  --pg-host pgdatabase \
  --pg-port 5432 \
  --pg-db ny_taxi \
  --chunksize 100000 \
  --target-table taxi_lookup \
  --csv-url https://someurl.com/lookup.csv
```

---

## Dockerizing the Pipeline

We created a **Docker image for ingestion** which builds a container to run the pipeline.

### Dockerfile Overview

```dockerfile
# Start with slim Python 3.13 image for smaller size
FROM python:3.13.11-slim

# Copy uv binary from official uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Set working directory inside container
WORKDIR /app

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy dependency files first (better caching)
COPY "pyproject.toml" "uv.lock" ".python-version" ./

# Install all dependencies (pandas, sqlalchemy, psycopg2)
RUN uv sync --locked

# Copy ingestion script
COPY homework1-nov-ingest.py homework1-nov-ingest.py

# Set entry point to run the ingestion script
ENTRYPOINT [ "python", "homework1-nov-ingest.py" ]
```

- The image builds a virtual environment, installs all Python dependencies, and copies the ingestion script.
- Running a container from this image **performs the ingestion automatically** with the parameters passed via CLI.

### docker-compose.yml Overview

Services:

- **pgdatabase**: PostgreSQL instance  
- **pgadmin**: Admin interface for PostgreSQL  
- **volumes**: Persist database and pgAdmin data  

Ports:

- PostgreSQL exposed on `localhost:5433`  
- pgAdmin exposed on `localhost:8085`

---

## Running the Pipeline with Docker

### Build Docker Image

```bash
docker build -t homework1:v001 .
```

### Start PostgreSQL and pgAdmin

```bash
docker-compose up -d
```

### Run Ingestion Container

```bash
docker run -it --rm \
  --network=homework1_default \
  homework1:v001 \
  --pipeline parquet \
  --pg-user root \
  --pg-pass root \
  --pg-host pgdatabase \
  --pg-port 5432 \
  --pg-db ny_taxi \
  --year 2025 \
  --month 11 \
  --chunksize 100000 \
  --target-table yellow_taxi_trips_nov_2025
```

- This container will download the data, process it in chunks, and ingest it into PostgreSQL.
- CSV ingestion works similarly using the lookup ingestion script.

---

## Jupyter Notebook

- Installed in the virtual environment via `uv`  
- Run:

```bash
uv run jupyter notebook
```

- Access notebooks in your browser to explore datasets, inspect columns, and verify preprocessing.

---

## SQL Queries

### Question 3: Trips ≤ 1 mile

```sql
SELECT COUNT(trip_distance)
FROM public.green_taxi_trips_nov_2025
WHERE trip_distance <= 1
  AND lpep_pickup_datetime BETWEEN '2025-11-01' AND '2025-12-01';
```

### Question 4: Pickup day with longest trip (≤100 miles)

```sql
SELECT date_trunc('day', lpep_pickup_datetime) AS pickup_day,
       trip_distance
FROM public.green_taxi_trips_nov_2025
WHERE trip_distance <= 100
ORDER BY trip_distance DESC
LIMIT 1;
```

### Question 5: Pickup zone with largest total_amount (Nov 18, 2025)

```sql
SELECT SUM(g.total_amount) AS total_amount,
       l."Borough",
       l."Zone",
       date_trunc('day', g.lpep_pickup_datetime) AS d
FROM public.green_taxi_trips_nov_2025 g
JOIN public.taxi_lookup l
  ON g."PULocationID" = l."LocationID"
WHERE date_trunc('day', g.lpep_pickup_datetime) = DATE '2025-11-18'
GROUP BY l."Borough", l."Zone", d
ORDER BY total_amount DESC
LIMIT 5;
```

### Question 6: Dropoff zone with largest tip from "East Harlem North"

```sql
SELECT do_l."Borough" AS dropoff_borough,
       do_l."Zone"    AS dropoff_zone,
       g.tip_amount
FROM public.green_taxi_trips_nov_2025 g
JOIN public.taxi_lookup pu
  ON g."PULocationID" = pu."LocationID"
JOIN public.taxi_lookup do_l
  ON g."DOLocationID" = do_l."LocationID"
WHERE pu."Zone" = 'East Harlem North'
  AND g.lpep_pickup_datetime >= '2025-11-01'
  AND g.lpep_pickup_datetime <  '2025-12-01'
ORDER BY g.tip_amount DESC
LIMIT 1;
```

---

## Architecture Diagram

```text
 +----------------+       +-----------------+       +----------------+
 | CSV / Parquet  |  -->  | Ingest Container|  -->  | PostgreSQL DB  |
 |  Source Data   |       | (Docker)        |       |  (pgdatabase)  |
 +----------------+       +-----------------+       +----------------+
         |                                                   |
         v                                                   v
   Optional Jupyter Notebook                          Admin UI via pgAdmin
   for Data Exploration                                 (pgadmin container)
```

- The **Docker image** encapsulates all dependencies and the ingestion logic.
- Running a container from the image ingests data automatically.
- pgAdmin allows for easy database inspection and query execution.

---

**End of README**

