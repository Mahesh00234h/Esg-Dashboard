import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import os


data_file_path = "data/processed_esg_data.csv"

if not os.path.exists(data_file_path):
    raise FileNotFoundError(f"Data file not found: {data_file_path}")

esg_data = pd.read_csv(data_file_path)


print("Columns in ESG Data:", esg_data.columns)


required_columns = ["Country Name", "CountryCode", "Indicator Name_x", "Indicator Code"]
years_columns = [col for col in esg_data.columns if col.isdigit()]  

if not all(col in esg_data.columns for col in required_columns) or not years_columns:
    raise ValueError("Required columns or year data are missing in the dataset!")


esg_data = esg_data.melt(
    id_vars=required_columns,
    value_vars=years_columns,
    var_name="Year",
    value_name="Value"
)


esg_data['Value'] = pd.to_numeric(esg_data['Value'], errors='coerce')

app = dash.Dash(__name__)


categories = esg_data["Indicator Name_x"].dropna().unique()
years = sorted(esg_data["Year"].dropna().unique())


app.layout = html.Div([
    html.H1("ESG Data Dashboard", style={"textAlign": "center", "padding": "20px"}),

    
    html.Div([
        html.Label("Select ESG Category:"),
        dcc.Dropdown(
            id="category-filter",
            options=[{"label": cat, "value": cat} for cat in categories],
            value=categories[0],
            placeholder="Select a category"
        ),
        html.Label("Select Year:"),
        dcc.Dropdown(
            id="year-filter",
            options=[{"label": str(year), "value": str(year)} for year in years],
            value=str(years[0]),
            placeholder="Select a year"
        ),
    ], style={"width": "50%", "margin": "auto", "padding": "20px"}),

    
    dcc.Graph(id="world-map"),
    dcc.Graph(id="bar-chart"),
])


@app.callback(
    [Output("world-map", "figure"), Output("bar-chart", "figure")],
    [Input("category-filter", "value"), Input("year-filter", "value")]
)
def update_dashboard(selected_category, selected_year):
    
    filtered_data = esg_data[
        (esg_data["Indicator Name_x"] == selected_category) &
        (esg_data["Year"] == selected_year)
    ]

    
    if filtered_data.empty:
        empty_fig = px.scatter(title="No Data Available")
        return empty_fig, empty_fig

    
    map_fig = px.choropleth(
        filtered_data,
        locations="CountryCode", 
        color="Value", 
        hover_name="Country Name",
        title=f"World ESG Data Map ({selected_category} - {selected_year})",
        color_continuous_scale="Viridis",  
        template="plotly_dark",  
    )


    bar_fig = px.bar(
        filtered_data,
        x="Country Name",
        y="Value",
        title=f"ESG Comparison by Country ({selected_category} - {selected_year})",
        labels={"Value": "ESG Score", "Country Name": "Country"},
        color="Country Name",  
        template="plotly_dark",  
    )

    return map_fig, bar_fig


if __name__ == "__main__":
    app.run_server(debug=True)
