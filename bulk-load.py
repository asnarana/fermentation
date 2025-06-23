import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
#load environment variables from .env (e.g., DB_URL, CSV_FOLDER)
load_dotenv()
#create a SQLAlchemy engine using the DB_URL environment variable
engine = create_engine(os.getenv("DB_URL"))
# get the folder path where CSV files are stored
folder = os.getenv("CSV_FOLDER")
# iterate over every file in the CSV folder
for fname in os.listdir(folder):
    # skipping non csv files
    if not fname.lower().endswith(".csv"): continue
    # get the table name by removing the .csv extension
    table = os.path.splitext(fname)[0]
    # build the full path to the CSV file
    path  = os.path.join(folder, fname)
    print(f"Loading {table} …")

    # read the CSV into a DataFrame
    df = pd.read_csv(path)
    # writing  the df to the database, replacing any existing table
    df.to_sql(table, engine, if_exists="replace", index=False)
    print(f" → {len(df)} rows into `{table}`")