import os
import re
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from prophet import Prophet

# ─── 1) Setup DB connection ────────────────────────────────────────────────────
load_dotenv()
engine = create_engine(os.getenv("DB_URL"))

# ─── 2) Define table groups ─────────────────────────────────────────────────────
BAR_TABLES = [
    "Batches per year",
    "GFP Concentration (gL)",
    "Total GFP (g)",
    "Final OD600",
    "Initial Glucose (gL)",
    "Volumetric productivity (ghrL)",
    "ProductBiomass (gg)",
    "SpecificGrowth Rate (1hr)"
]

TIME_SERIES_TABLES = [
    "Aeration",
    "Agitation",
    "Dissolved Oxygen",
    "OD600",
    "Glucose",
    "pH",
    "Temperature_PV",
    "Pressure_PV",
    "Weight_PV"
]

# ─── 3) Date extraction util for batch IDs ─────────────────────────────────────
def extract_ds(batch_str):
    m = re.search(r"(\d{8})", batch_str)
    if m:
        return datetime.strptime(m.group(1), "%Y%m%d")
    m = re.search(r"(\d{6})", batch_str)
    if m:
        return datetime.strptime(m.group(1), "%y%m%d")
    return pd.NaT

# ─── 4) Forecast bar tables ────────────────────────────────────────────────────
for table in BAR_TABLES:
    print(f"\n=== Forecasting bar-table {table!r} ===")
    df = pd.read_sql_table(table, engine)
    # choose ds & freq
    if "Year" in df.columns:
        df["ds"] = pd.to_datetime(df["Year"], format="%Y")
        freq = "Y"
    else:
        batch_col = next(c for c in df.columns if re.search(r"batch", c, re.I))
        df["ds"] = df[batch_col].apply(extract_ds)
        freq = "M"
    # pick y
    num_cols = df.select_dtypes(include="number").columns.tolist()
    ycol = next(c for c in num_cols if c != "Year")
    hist = df[["ds", ycol]].dropna().rename(columns={ycol: "y"})
    # fit & forecast
    m = Prophet(yearly_seasonality=True)
    m.fit(hist)
    future = m.make_future_dataframe(periods=5, freq=freq)
    fc = m.predict(future)[["ds","yhat","yhat_lower","yhat_upper"]]
    # write back
    safe = re.sub(r"[^0-9A-Za-z_]","_", table)
    out_table = f"{safe}_forecast"
    fc.to_sql(out_table, engine, if_exists="replace", index=False)
    print(f" → Wrote {len(fc)} rows to '{out_table}'")

# ─── 5) Forecast time-series tables ─────────────────────────────────────────────
for table in TIME_SERIES_TABLES:
    print(f"\n=== Forecasting time-series {table!r} ===")
    df = pd.read_sql_table(table, engine)
    # identify time col, batch col, numeric cols
    time_col = next((c for c in df.columns if re.search(r"time", c, re.I)), df.columns[0])
    batch_col = next((c for c in df.columns if re.search(r"batch", c, re.I)), None)
    df[time_col] = pd.to_numeric(df[time_col], errors="coerce")
    # choose ds by converting numeric hours to timestamp starting today
    # here we treat 'time' as hours offset
    start = datetime.now().replace(minute=0,second=0,microsecond=0)
    df["ds"] = df[time_col].apply(lambda h: start + pd.Timedelta(hours=h))
    freq = "H"
    # pick y
    num_cols = df.select_dtypes(include="number").columns.tolist()
    ycols = [c for c in num_cols if c not in [time_col]]
    # for each batch (or all data)
    all_fc = []
    if batch_col:
        for batch, grp in df.groupby(batch_col):
            grp = grp.sort_values("ds")
            hist = grp[["ds"] + ycols].melt("ds", var_name="metric", value_name="y").dropna()
            for metric, sub in hist.groupby("metric"):
                m = Prophet(yearly_seasonality=False, daily_seasonality=True)
                m.fit(sub.rename(columns={"ds":"ds","y":"y"}))
                fut = m.make_future_dataframe(periods=24, freq=freq)
                pred = m.predict(fut)[["ds","yhat","yhat_lower","yhat_upper"]]
                pred["batch"] = batch
                pred["metric"] = metric
                all_fc.append(pred)
    else:
        hist = df[["ds"] + ycols].melt("ds", var_name="metric", value_name="y").dropna()
        for metric, sub in hist.groupby("metric"):
            m = Prophet(daily_seasonality=True)
            m.fit(sub)
            fut = m.make_future_dataframe(periods=24, freq=freq)
            pred = m.predict(fut)[["ds","yhat","yhat_lower","yhat_upper"]]
            pred["metric"] = metric
            all_fc.append(pred)
    # concatenate & write
    fc_all = pd.concat(all_fc, ignore_index=True)
    safe = re.sub(r"[^0-9A-Za-z_]","_", table)
    out_table = f"{safe}_ts_forecast"
    fc_all.to_sql(out_table, engine, if_exists="replace", index=False)
    print(f" → Wrote {len(fc_all)} rows to '{out_table}'")