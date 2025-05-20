import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DB_URL"))
folder = os.getenv("CSV_FOLDER")

for fname in os.listdir(folder):
    if not fname.lower().endswith(".csv"): continue
    table = os.path.splitext(fname)[0]
    path  = os.path.join(folder, fname)
    print(f"Loading {table} …")
    df = pd.read_csv(path)
    df.to_sql(table, engine, if_exists="replace", index=False)
    print(f" → {len(df)} rows into `{table}`")