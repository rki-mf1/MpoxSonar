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
note_data = pd.read_csv('data/Data.csv')
coord_data = pd.read_csv('data/location_coordinates.csv')

result = pd.merge(note_data, coord_data, left_on='COUNTRY', right_on='name')

#print(note_data.columns)

result['number'] = [len(x.split(',')) for x in result['NUC_PROFILE']]
new_res = result.groupby(['COUNTRY', 'lon', 'lat', 'RELEASE_DATE'])['number'].sum().reset_index()
print(new_res.columns)

fig = px.scatter_mapbox(
    new_res,
    lat="lat",
    lon="lon",
    size="number",
    animation_frame='RELEASE_DATE',
    #size_max=15,
    zoom=10,
    mapbox_style="carto-positron"
)

print(new_res)

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
