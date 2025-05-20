import os
import re
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from dotenv import load_dotenv

# ─── Setup DB connection ─────────────────────────────────────────────────────
load_dotenv()
engine = create_engine(os.getenv("DB_URL"))

# ─── Output directory ─────────────────────────────────────────────────────────
out_dir = "pages"
os.makedirs(out_dir, exist_ok=True)

# ─── BAR-CHART KPIs configuration ─────────────────────────────────────────────
BAR_MAP = {
    "Batches per year":               {"table": "Batches_per_year_forecast",               "image": "BatchesPerYear.jpg"},
    "GFP Concentration (gL)":         {"table": "GFP_Concentration__gL__forecast",         "image": "GFPConcentration(gL).jpg"},
    "Total GFP (g)":                  {"table": "Total_GFP__g__forecast",                  "image": "TotalGFP.jpg"},
    "Final OD600":                    {"table": "Final_OD600_forecast",                    "image": "FinalOD600.jpg"},
    "Initial Glucose (gL)":           {"table": "Initial_Glucose__gL__forecast",           "image": "InitialGlucose.jpg"},
    "Volumetric productivity (ghrL)": {"table": "Volumetric_productivity__ghrL__forecast", "image": "volumeProductivity.jpg"},
    "ProductBiomass (gg)":            {"table": "ProductBiomass__gg__forecast",            "image": "ProductBiomass.jpg"},
    "SpecificGrowth Rate (1hr)":      {"table": "SpecificGrowth_Rate__1hr__forecast",      "image": "specificgrowthrate - Copy.jpg"}
}

# ─── TIME-SERIES KPIs configuration ──────────────────────────────────────────
TS_MAP = {
    "Aeration":        {"table": "Aeration_ts_forecast",       "image": "Aeration.jpg",        "metric": "Air_Sparge_PV"},
    "Agitation":       {"table": "Agitation_ts_forecast",      "image": "Agitation.jpg",       "metric": "Agitation_PV"},
    "Dissolved Oxygen":{"table": "Dissolved_Oxygen_ts_forecast","image": "DissolvedOxygen.jpg","metric": "DO_PV"},
    "OD600":           {"table": "OD600_ts_forecast",          "image": "OD600Time.jpg",       "metric": "OD600"},
    "Glucose":         {"table": "Glucose_ts_forecast",        "image": "GlucoseTime.jpg",     "metric": "Sum_of_Glucose"},
    "pH":              {"table": "pH_ts_forecast",             "image": "pH.jpg",             "metric": "pH_PV"},
    "Temperature_PV":  {"table": "Temperature_PV_ts_forecast", "image": "TempPV.jpg",          "metric": "Temperature_PV"},
    "Pressure_PV":     {"table": "Pressure_PV_ts_forecast",    "image": "pressurePV.jpg",      "metric": "Pressure_PV"},
    "Weight_PV":       {"table": "Weight_PV_ts_forecast",      "image": "WeightPV.jpg",        "metric": "Weight_PV"}
}

# ─── HTML template generator ─────────────────────────────────────────────────
def make_html(display_name, img_file, df_fc, metric=None):
    # Always show the snapshot image
    title = display_name
    html = f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>{title} Forecast</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; }}
    h1 {{ text-align: center; }}
    .container {{ max-width: 800px; margin: auto; }}
    .snapshot {{ width: 100%; height: auto; margin: 20px 0; }}
    .forecast-text {{ font-size: 1.2em; line-height: 1.4; }}
  </style>
</head>
<body>
  <div class=\"container\">
    <h1>{title}</h1>
    <img src=\"../assets/{img_file}\" alt=\"{title}\" class=\"snapshot\" />
    <div class=\"forecast-text\">"""

    # If forecast data exists, show next forecast; otherwise show a no-data message
    if not df_fc.empty:
        df_fc["ds"] = pd.to_datetime(df_fc["ds"])
        nxt = df_fc.iloc[0]
        next_x, next_y = nxt["ds"].date(), nxt["yhat"]
        html += f"      <p>The model forecasts that by <strong>{next_x}</strong>, " \
                f"the value will be around <strong>{next_y:.2f}</strong>.</p>\n"
    else:
        html += "      <p><em>No forecast data available.</em></p>\n"

    # Close HTML
    html += """
    </div>
  </div>
</body>
</html>
"""
    return html

# ─── Generate bar HTML pages ──────────────────────────────────────────────────
for name, info in BAR_MAP.items():
    table = info["table"]
    img = info["image"]
    print(f"Generating bar HTML for {name} from table {table}")
    df_fc = pd.read_sql_table(table, engine)
    page = make_html(name, img, df_fc)
    path = os.path.join(out_dir, f"{table}.html")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(page)
    print(f" → Wrote {path}")

# ─── Generate time-series HTML pages ──────────────────────────────────────────
for name, info in TS_MAP.items():
    table = info["table"]
    img = info["image"]
    metric = info["metric"]
    print(f"Generating TS HTML for {name} from table {table}")
    df_fc = pd.read_sql_table(table, engine)
    if "metric" in df_fc.columns and metric:
        df_fc = df_fc[df_fc["metric"] == metric]
    page = make_html(name, img, df_fc, metric)
    path = os.path.join(out_dir, f"{table}.html")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(page)
    print(f" → Wrote {path}")