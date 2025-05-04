import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# === CONFIG: read from environment (.env) ===
DB_ADMIN_DB = os.getenv("DB_ADMIN_DB", "postgres")             # initial admin DB
DB_USER     = os.getenv("DB_USER")                            # e.g. postgres
DB_PASS     = os.getenv("DB_PASS")                            # your admin password
DB_HOST     = os.getenv("DB_HOST", "localhost")              
DB_PORT     = os.getenv("DB_PORT", "5432")                   
TARGET_DB   = os.getenv("DB_NAME", "trends_db")               # the DB to create/use
CSV_PATH    = os.getenv("CSV_PATH", "./actualDataTeamProject.csv")
TABLE_NAME  = os.getenv("TABLE_NAME", "google_trends_international_cleaned")

# === STEP 1: create target database if it doesn’t exist ===
try:
    admin_conn = psycopg2.connect(
        dbname=DB_ADMIN_DB,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    admin_cur = admin_conn.cursor()

    admin_cur.execute(
        "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
        (TARGET_DB,)
    )
    if not admin_cur.fetchone():
        admin_cur.execute(f"CREATE DATABASE {TARGET_DB}")
        print(f"✅ Database '{TARGET_DB}' created.")
    else:
        print(f"ℹ️ Database '{TARGET_DB}' already exists.")

    admin_cur.close()
    admin_conn.close()

except Exception as e:
    print("❌ Failed to create/check database:", e)
    exit(1)

# === STEP 2: load CSV ===
try:
    df = pd.read_csv(CSV_PATH)
    print(f"✅ Loaded CSV from '{CSV_PATH}'.")
except Exception as e:
    print(f"❌ Failed to read CSV at '{CSV_PATH}':", e)
    exit(1)

# === STEP 3: upload to Postgres ===
engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{TARGET_DB}"
)

try:
    df.to_sql(
        TABLE_NAME,
        engine,
        index=False,
        if_exists='replace'
    )
    print(f"✅ Data uploaded to table '{TABLE_NAME}' in database '{TARGET_DB}'.")
except Exception as e:
    print(f"❌ Failed to upload data to '{TABLE_NAME}':", e)
    exit(1)
