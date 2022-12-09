import dash
from dash import dcc
from dash import html
from dash import Input
from dash import Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from pages.util_tool_checklists import card
from pages.util_tool_checklists import checklist_1
from pages.util_tool_checklists import checklist_2
from pages.util_tool_checklists import checklist_3
from pages.util_tool_checklists import checklist_4


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


@app.callback(
    Output("checklist-output", "children"),
    [
        Input("checklist-input", "value"),
    ],
)
def on_form_change(radio_items_value, checklist_value, switches_value):
    template = "checklist item{} selected."

    n_checkboxes = len(checklist_value)
    n_switches = len(switches_value)

    output_string = template.format(
        radio_items_value,
        n_checkboxes,
        "s" if n_checkboxes != 1 else "",
        n_switches,
        "es" if n_switches != 1 else "",
    )
    return output_string


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
        # # check box with references
        # html.Div(
        #     style={'width': '10%', 'height': '100%', 'float': 'left'},
        #     children=[
        #         dcc.Checklist(
        #             className='checkbox_1',
        #             id='references-list',
        #             options=[
        #                 {'label': 'some-ref-gen', 'value': 'I1ST2'},
        #                 {'label': 'some-ref-gen', 'value': 'I2ST2'},
        #                 {'label': 'some-ref-gen', 'value': 'I3ST2'},
        #                 {'label': 'ssome-ref-gen', 'value': 'I4ST2'},
        #             ],
        #             labelStyle={'display': 'block'}
        #         )
        #     ]
        # ),
        # # checkbox with mutations
        # html.Div(
        #     style={'width': '10%', 'height': '100%', 'float': 'left'},
        #     children=[
        #         dcc.Checklist(
        #             className='checkbox_1',
        #             id='mutation-list',
        #             options=[
        #                 {'label': 'some mutation', 'value': 'I1ST2'},
        #                 {'label': 'some mutation', 'value': 'I2ST2'},
        #                 {'label': 'some mutation', 'value': 'I3ST2'},
        #                 {'label': 'some mutation', 'value': 'I4ST2'},
        #             ],
        #             labelStyle={'display': 'block'}
        #         )
        #     ]
        # ),
        # html.Div(
        #     style={'width': '15%', 'height': '190%', 'float': 'left'},
        #     children=[
        #         dcc.Checklist(
        #             className='checkbox_1',
        #             id='vizual-method-list',
        #             options=[
        #                 {'label': 'visualization-method', 'value': 'I1MT'},
        #                 {'label': 'visualization-method', 'value': 'I2MT'},
        #                 {'label': 'visualization-method', 'value': 'I3MT'}
        #             ],
        #             value=['I1MT'],
        #             labelStyle={'display': 'block'}
        #         )
        #     ]
        # ),
        card,
        html.Br(style={"line-height": "10"}),
        # html.Div(
        #    [
        #        html.Div(
        #            [
        #                "direct MPXSonar query: ",
        #                html.Br(),
        #                dcc.Input(
        #                    id="my-input", type="text", size="100"
        #                ),
        #            ]
        #        ),
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
