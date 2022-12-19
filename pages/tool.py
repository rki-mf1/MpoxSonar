import dash
from dash import dcc
from dash import html

from dash.dependencies import Input, Output, State

from dash import callback
from dash import callback_context

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


sql_query = "" \
            "SELECT t6.value_text, t1.label, value_date, count(*)" \
            "FROM " \
            "variant t1 " \
            "JOIN alignment2variant t2 ON t1.id = t2.variant_id " \
            "JOIN alignment t3 ON t2.alignment_id = t3.id " \
            "JOIN sequence t4 ON t3.seqhash = t4.seqhash " \
            "JOIN sample t5 ON t4.seqhash = t5.seqhash" \
            "JOIN sample2property t6 ON t5.id = t6.sample_id" \
            "WHERE" \
            "t1.label LIKE 'del%'" \
            "GROUP BY" \
            "t6.value_text, t1.label, value_date" \
            "limit 250" \
            ";"




# example data for example map
note_data = pd.read_csv('data/Data.csv')

coord_data = pd.read_csv('data/location_coordinates.csv')
data = pd.read_csv('data/data.csv')
result = pd.merge(data, coord_data, left_on='value_text', right_on='name')

fig = px.scatter_mapbox(
    result,
    lat="lat",
    lon="lon",
    color='label',
    size="count(*)",
    #animation_frame='value_date',
    #size_max=15,
    zoom=0.75,
    mapbox_style="carto-positron"
)

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



@callback(
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



@callback(Output("query_output", "children"), [Input("query_input", "value")])
def output_text(value):
    return value
