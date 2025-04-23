import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load the CSV file
df = pd.read_csv("./actualDataTeamProject.csv")

# PostgreSQL credentials Update This
db_user = 'postgres'
db_password = 'Titanic29!'

# --- SET THESE ---
db_user = 'postgres'
db_password = 'Titanic29!'
db_host = 'localhost'
db_port = '5432'
db_name = 'trends_db'  # The target database to create

# --- Step 1: Connect to default 'postgres' DB and create the target DB if needed ---
try:
    # Connect to default database to create a new one
    conn = psycopg2.connect(
        dbname='postgres',
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Create the new database
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"✅ Database '{db_name}' created.")
    else:
        print(f"ℹ️ Database '{db_name}' already exists.")

    cursor.close()
    conn.close()
except Exception as e:
    print("❌ Failed to create database:", e)
    exit()

# --- Step 2: Load CSV and Upload to Target Database ---
df = pd.read_csv("actualDataTeamProject.csv")

# Create connection engine to the new database
engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Upload to table
table_name = 'google_trends_international_cleaned'
df.to_sql(table_name, engine, index=False, if_exists='replace')

print(f"✅ Data uploaded to table '{table_name}' in database '{db_name}'.")
