import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm
import click



dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

# df = pd.read_csv(
#     prefix + 'yellow_tripdata_2021-01.csv.gz',
#     # reads first 100 rows
#     # nrows=1000,
#     # sets the data types of the different columns according to the d_types dictionary above
#     dtype=dtype,
#     # ensures the tpep_pickup_datetime and tpep_dropoff_datetime are in datetime format during read time
#     parse_dates=parse_dates
# )


# # Get DDL schema for the database
# print(pd.io.sql.get_schema(df, name = 'yellow_taxi_data', con =engine))

# use click to parse the arguments in CLI
@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL username')
@click.option('--pg-pass', default='root', help='PostgreSQL password')
@click.option('--pg-host', default='localhost', help='PostgreSQL host')
@click.option('--pg-port', default='5432', help='PostgreSQL port')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name')
@click.option('--year', default=2021, type=int, help='Year of the data')
@click.option('--month', default=1, type=int, help='Month of the data')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for ingestion')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')

def run(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, chunksize, target_table):
    # DB parameters
    pg_user = 'root'
    pg_pass = 'root'
    pg_host = 'localhost'
    pg_port = 5432
    pg_db = 'ny_taxi'

    year = 2021
    month = 1
    target_table = target_table
    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
    url = f'{prefix}yellow_tripdata_{year}-{month:02d}.csv.gz'

    # create engine
    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    chunksize = 100000

    df_iter = pd.read_csv(

        url,
        dtype =dtype,
        parse_dates = parse_dates,
        iterator = True,
        chunksize = chunksize
    )

    first = True

    for df_chunk in tqdm(df_iter):
        if first:
            # create the table with no data first
            df_chunk.head(n=0).to_sql(
                name = target_table, 
                con = engine, 
                if_exists = 'replace')
            first = False
        df_chunk.to_sql(
            name =  target_table, 
            con =  engine, 
            if_exists = 'append')


if __name__ == '__main__':
    run()
