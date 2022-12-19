import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State


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

# example data for example map
note_data = pd.read_csv('data/Data.csv')

coord_data = pd.read_csv('data/location_coordinates.csv')
data = pd.read_csv('data/data.csv')
print(data.columns)
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
        html.Div(id='app-1-display-value', children=''),
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
        html.Div(id='test_output', children=''),
        query_card,
        html.Br(style={"line-height": "10"}),

        html.Div(dcc.Input(id='input-box', type='text')),
        html.Button('Submit', id='button-example-1'),
        html.Div(
            id='output-container-button',
            children='Enter a value and press submit'
        ),

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
    Output('output-container-button', 'children'),
    [Input('button-example-1', 'n_clicks')],
    [State('input-box', 'value')],
    prevent_initial_call=True,)
def update_output(n_clicks, value):
    return 'The input value was "{}" and the button has been clicked {} times'.format\
            (
            len(value),
            n_clicks
        )

