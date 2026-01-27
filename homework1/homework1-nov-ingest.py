import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import pyarrow.parquet as pq
import requests
from tqdm import tqdm
import click

# parquet_ingestion
def ingest_parquet(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, chunksize, target_table):
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet"
    local_file = "data.parquet"

    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    # Download parquet file
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)

    pq_file = pq.ParquetFile(local_file)
    total_rows = pq_file.metadata.num_rows

    # Read in batches with progress bar
    with tqdm(total=total_rows, unit="rows", desc="Ingesting parquet") as pbar:
        for batch in pq_file.iter_batches(batch_size=chunksize):
            df = batch.to_pandas()

            # Example preprocessing
            df["passenger_count"] = df["passenger_count"].astype("Int64")

            df.to_sql(target_table, engine, if_exists="append", index=False)
            pbar.update(len(df))

# CSV ingestion
def ingest_csv(pg_user, pg_pass, pg_host, pg_port, pg_db, chunksize, target_table, url):
    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    # Read CSV in chunks with progress bar
    df_iter = pd.read_csv(url, chunksize=chunksize, iterator=True)

    with tqdm(total=None, desc="Ingesting CSV") as pbar:
        for df in df_iter:
            # Example preprocessing
            df.to_sql(target_table, engine, if_exists="append", index=False)
            pbar.update(len(df))

# -----------------------------
# CLI entrypoint
# -----------------------------
@click.command()
@click.option('--pipeline', type=click.Choice(['parquet', 'csv']), required=True)
@click.option('--pg-user', default='root')
@click.option('--pg-pass', default='root')
@click.option('--pg-host', default='pgdatabase')
@click.option('--pg-port', default=5432, type=int)
@click.option('--pg-db', default='ny_taxi')
@click.option('--year', default=2021, type=int)
@click.option('--month', default=1, type=int)
@click.option('--chunksize', default=100_000, type=int)
@click.option('--target-table', default='yellow_taxi_trips')
@click.option('--csv-url', default=None, help='URL for CSV ingestion (only needed if pipeline=csv)')
def run(pipeline, pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, chunksize, target_table, csv_url):
    if pipeline == 'parquet':
        ingest_parquet(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, chunksize, target_table)
    elif pipeline == 'csv':
        if csv_url is None:
            raise ValueError("CSV URL must be provided for CSV pipeline")
        ingest_csv(pg_user, pg_pass, pg_host, pg_port, pg_db, chunksize, target_table, csv_url)


if __name__ == '__main__':
    run()



