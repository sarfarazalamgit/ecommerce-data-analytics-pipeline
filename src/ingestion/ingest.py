import os
import pandas as pd
import logging
import time
import argparse
from sqlalchemy import create_engine


# Ensure logs folder exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    filename='logs/ingestion_db.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def ingest_db_in_chunks(file_path, table_name, engine, chunksize=2000):
    first_chunk = True
    total_rows = 0
    start_time = time.time()

    logging.info(f"Starting ingestion for file: {file_path} into table: {table_name}")

    try:
        for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunksize), start=1):

            # Clean column names (important for SQL compatibility)
            chunk.columns = [col.strip().lower().replace(" ", "_") for col in chunk.columns]

            if_exists_option = 'replace' if first_chunk else 'append'

            chunk.to_sql(
                table_name,
                con=engine,
                if_exists=if_exists_option,
                index=False,
                method='multi'
            )

            rows = len(chunk)
            total_rows += rows

            logging.info(f"Chunk {i}: Inserted {rows} rows into table {table_name}")

            print(f"Chunk {i}: {rows} rows inserted")

            first_chunk = False

        elapsed_time = time.time() - start_time

        logging.info(f"Finished ingestion for file: {file_path}")
        logging.info(f"Total rows ingested: {total_rows}")
        logging.info(f"Time taken: {elapsed_time:.2f} seconds")

        print(f"\n✅ Ingestion complete! Total rows: {total_rows}")
        print(f"⏱ Time taken: {elapsed_time:.2f} seconds")

    except Exception as e:
        logging.error(f"Error ingesting data: {e}")
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest CSV into PostgreSQL in chunks with logging"
    )

    parser.add_argument("file_path", help="Path to the CSV file")
    parser.add_argument("table_name", help="Target database table name")
    parser.add_argument("db_url", help="Database connection string (SQLAlchemy format)")
    parser.add_argument("--chunksize", type=int, default=2000, help="Rows per chunk")

    args = parser.parse_args()

    # Create database engine
    engine = create_engine(args.db_url)

    # Run ingestion
    ingest_db_in_chunks(
        args.file_path,
        args.table_name,
        engine,
        args.chunksize
    )