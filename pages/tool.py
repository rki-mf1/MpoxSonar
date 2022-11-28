import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

import plotly.express as px
import pandas as pd


dash.register_page(__name__, path="/Tool")

url = "https://raw.githubusercontent.com/hflabs/city/master/city.csv"
geodata = pd.read_csv(url)

####example data for example map######
Sample_data = px.data.carshare()

fig = px.scatter_mapbox(
    Sample_data,
    lat="centroid_lat",
    lon="centroid_lon",
    color="peak_hour", size="car_hours",
    color_continuous_scale=px.colors.cyclical.IceFire,
    size_max=15,
    zoom=10,
    mapbox_style="carto-positron"
)
#######################################

####example data for example 2map######
Sample_data = px.data.carshare()

fig_ = px.scatter_mapbox(
    geodata,
    lat="geo_lat",
    lon="geo_lon",
    size="population",
    color_continuous_scale=px.colors.cyclical.IceFire,
    size_max=15,
    zoom=10,
    mapbox_style="carto-positron"
)
#######################################

layout = html.Div(
    [
        #check box with references
        html.Div(
            style={'width':'10%', 'height':'100%','float':'left'},
            children=[
                dcc.Checklist(
                    className ='checkbox_1',
                    id='references-list',
                    options=[
                        {'label': 'some-ref-gen', 'value': 'I1ST2'},
                        {'label': 'some-ref-gen', 'value': 'I2ST2'},
                        {'label': 'some-ref-gen', 'value': 'I3ST2'},
                        {'label': 'ssome-ref-gen', 'value': 'I4ST2'},
                    ],
                    labelStyle={'display': 'block'}
            )
        ]
    ),

        #checkbox with mutations
        html.Div(
            style={'width':'10%', 'height':'100%','float':'left'},
            children=[
                dcc.Checklist(
                    className ='checkbox_1',
                    id='mutation-list',
                    options=[
                        {'label': 'some mutation', 'value': 'I1ST2'},
                        {'label': 'some mutation', 'value': 'I2ST2'},
                        {'label': 'some mutation', 'value': 'I3ST2'},
                        {'label': 'some mutation', 'value': 'I4ST2'},
                    ],
                    labelStyle={'display': 'block'}
            )
        ]
    ),

        html.Div(
            style={'width':'10%', 'height':'190%','float':'left'},
            children=[
                dcc.Checklist(
                    className ='checkbox_1',
                    id='vizual-method-list',
                    options=[
                            {'label': 'visualization-method', 'value': 'I1MT'},
                            {'label': 'visualization-method', 'value': 'I2MT'},
                            {'label': 'visualization-method', 'value': 'I3MT'}
                    ],
                    value=['I1MT'],
                    labelStyle={'display': 'block'}
                )
            ]
        ),
        html.Br(style={'line-height': '10'}),
        html.Div(
            [
                html.Div(
                    [
                        "direct MPXSonar query: ",
                        html.Br(),
                        dcc.Input(
                            id="my-input", type="text", size="100"
                        ),
                    ]
                ),
                html.Br(),
                html.H1("Here is a map"),
                dcc.Graph(figure=fig_),
                html.Br(),
                html.Div(
                    [
                        html.Button('Download CSV', id='csv-download'),
                        dcc.Download(id='df-download')
                    ]
                )
            ]
        )
    ]
)