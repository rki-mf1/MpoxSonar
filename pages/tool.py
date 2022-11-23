import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc


dash.register_page(__name__)
card = dbc.Card(
        dbc.CardBody(
            html.Div(
                style={'width':'10%', 'height':'100%','float':'left'},
                children=[
                    dcc.Checklist(className ='checkbox_1',
                                  options=[
                                      {'label': 'some-ref-gen', 'value': 'I1ST1'},
                                      {'label': 'some-ref-gen', 'value': 'I2ST1'},
                                      {'label': 'some-ref-gen', 'value': 'I3ST1'},
                                      {'label': 'some-ref-gen', 'value': 'I4ST1'},
                                  ],
                                  value=['I1ST1', 'I2ST1'],
                                  labelStyle = {'display': 'block'}
                                  ),
                ]
            )
        ),
    outline=True,
)

card_bord = dbc.Row(
    [
        dbc.Col(card, width=9)
    ]
)

layout = html.Div([
    html.Br(),
    card_bord,
    html.Div(
        style={'width':'10%', 'height':'100%','float':'left'},
        children=[
            dcc.Checklist(className ='checkbox_1',
                    options=[
                        {'label': 'some mutation', 'value': 'I1ST2'},
                        {'label': 'some mutation', 'value': 'I2ST2'},
                        {'label': 'some mutation', 'value': 'I3ST2'},
                        {'label': 'some mutation', 'value': 'I4ST2'},
                            ],
                    labelStyle = {'display': 'block'}
                            )
        ]
    ),
    html.Div(
        style={'width':'10%', 'height':'190%','float':'left'},
        children=[
            dcc.Checklist(className ='checkbox_1',
                    options=[
                        {'label': 'visualization-method', 'value': 'I1MT'},
                        {'label': 'visualization-method', 'value': 'I2MT'},
                        {'label': 'visualization-method', 'value': 'I3MT'}
                            ],
                    value=['I1MT'],
                    labelStyle = {'display': 'block'}
                )
        ]
    ),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(style={'line-height': '5'}),
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
        html.H1("PLACE FOR THE MAP"),
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