import dash
from dash import dcc
from dash import html
from dash import Input
from dash import Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from pages.util_tool_checklists import checklist_1
from pages.util_tool_checklists import checklist_2
from pages.util_tool_checklists import checklist_3
from pages.util_tool_checklists import checklist_4
from pages.util_tool_checklists import query_card


dash.register_page(__name__, path="/Tool")

app = dash.Dash(__name__)

# example data for example map
Sample_data = px.data.carshare()

fig = px.scatter_mapbox(
    Sample_data,
    lat="centroid_lat",
    lon="centroid_lon",
    color="peak_hour",
    size="car_hours",
    color_continuous_scale=px.colors.cyclical.IceFire,
    size_max=15,
    zoom=10,
    mapbox_style="carto-positron",
)

# example data for example 2map
url = "https://raw.githubusercontent.com/hflabs/city/master/city.csv"
geodata = pd.read_csv(url)

fig_ = px.scatter_mapbox(
    geodata,
    lat="geo_lat",
    lon="geo_lon",
    size="population",
    color_continuous_scale=px.colors.cyclical.IceFire,
    size_max=15,
    zoom=10,
    mapbox_style="carto-positron",
)
#######################################


inputs = html.Div(
    [
        dbc.Form([checklist_1]),
        dbc.Form([checklist_2]),
        dbc.Form([checklist_3]),
        dbc.Form([checklist_4]),
        html.P(id="radioitems-checklist-output"),
    ]
)

layout = html.Div(
    [
        html.Div(
            [
                dbc.Form(
                    [checklist_1],
                    style={
                        "display": "inline-block",
                        "width": "23%",
                        "margin-right": "3%",
                    },
                    className="relative",
                ),
                dbc.Form(
                    [checklist_2],
                    style={
                        "display": "inline-block",
                        "width": "23%",
                        "margin-right": "3%",
                    },
                    className="relative",
                ),
                dbc.Form(
                    [checklist_3],
                    style={
                        "display": "inline-block",
                        "width": "23%",
                        "margin-right": "3%",
                    },
                    className="relative",
                ),
                dbc.Form(
                    [checklist_4],
                    style={"display": "inline-block", "width": "22%"},
                    className="relative",
                ),
            ]
        ),
        html.P(id="radioitems-checklist-output"),
        query_card,
        html.Br(style={"line-height": "10"}),
        html.Div(
            [
                html.Br(),
                html.H1("Here is a map"),
                dcc.Graph(figure=fig),
                html.Br(),
                html.Div(
                    [
                        html.Button("Download CSV", id="csv-download"),
                        dcc.Download(id="df-download"),
                    ]
                ),
            ]
        ),
    ]
)


@app.callback(
    Output("checklist-output", "children"),
    [
        Input("1_checklist_input", "value"),
        Input("2_checklist_input", "value"),
        Input("3_checklist_input", "value"),
        Input("4_checklist_input", "value"),
    ],
)
def select_all_none(all_selected, options):
    all_or_none = []
    all_or_none = [option["value"] for option in options if all_selected]
    return all_or_none


@app.callback(Output("query_output", "children"), [Input("query_input", "value")])
def output_text(value):
    return value
