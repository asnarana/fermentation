import os, re
from dash import Dash, html, dcc, Input, Output
from dotenv import load_dotenv

# ─── 1) Setup ─────────────────────────────────────────────────────────────────
load_dotenv()
app = Dash(__name__)

# ─── 2) KPI categories ─────────────────────────────────────────────────────────
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

TS_TABLES = [
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

# ─── 3) Map display names to HTML detail pages ────────────────────────────────
# Bar-chart pages (_forecast.html)
BAR_PAGES = {
    name: f"pages/{re.sub(r'[^0-9A-Za-z_]', '_', name)}_forecast.html"
    for name in BAR_TABLES
}
# Time-series pages (_ts_forecast.html)
TS_PAGES = {
    name: f"pages/{re.sub(r'[^0-9A-Za-z_]', '_', name)}_ts_forecast.html"
    for name in TS_TABLES
}
# Combine mappings
DETAIL_PAGES = {**BAR_PAGES, **TS_PAGES}

# Combined list for dropdown
TABLES = BAR_TABLES + TS_TABLES

# ─── 4) Layout ─────────────────────────────────────────────────────────────────
app.layout = html.Div(style={"padding": "20px", "fontFamily": "Arial, sans-serif"}, children=[
    html.H1("Fermentation KPI Viewer"),
    dcc.Dropdown(
        id='table-selector',
        options=[{'label': t, 'value': t} for t in TABLES],
        placeholder='Select a KPI...',
        style={'width': '50%', 'marginBottom': '20px'}
    ),
    html.Div(id='output-container')
])

# ─── 5) Callback: embed HTML pages for both bar and time-series ──────────────
@app.callback(
    Output('output-container', 'children'),
    Input('table-selector', 'value')
)
def render_content(table_name):
    if not table_name:
        return html.P("Please select a KPI from the dropdown.")

    page_path = DETAIL_PAGES.get(table_name)
    if page_path and os.path.exists(page_path):
        with open(page_path, 'r', encoding='utf-8') as f:
            html_src = f.read()
        return html.Iframe(
            srcDoc=html_src,
            style={'width': '100%', 'height': '600px', 'border': 'none'}
        )

    return html.P(f"Detail page not found for '{table_name}' at {page_path}.")

# ─── 6) Run the server ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)