import pandas as pd
from sqlalchemy import create_engine

# Load the CSV file
df = pd.read_csv("./actualDataTeamProject.csv")

# PostgreSQL credentials Update This
db_user = 'your_username'
db_password = 'your_password'
db_host = 'localhost'
db_port = '5432'
db_name = 'your_database'

# Create connection engine
engine = create_engine(f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Upload the dataframe to PostgreSQL
table_name = 'google_trends_international_cleaned'
df.to_sql(table_name, engine, index=False, if_exists='replace')

print(f"✅ Data uploaded to table '{table_name}' in database '{db_name}'.")
