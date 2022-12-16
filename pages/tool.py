import dash
from dash import html
from dash import dcc
from dash import State
from dash import dash_table
from dash import callback_context

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

import plotly.express as px
import pandas as pd

from pages.tool_page_components import user_query_input
#from src.covsonar.app_controller import get_freq_mutation
#from src.covsonar.app_controller import match_controller
#from src.covsonar.app_controller import sonarBasics
#from src.covsonar.sonar import parse_args



dash.register_page(__name__, path="/Tool")


############## TEST DATA EXPERIMENT ################
note_data = pd.read_csv('data/Data.csv')
coord_data = pd.read_csv('data/location_coordinates.csv')

result = pd.merge(note_data, coord_data, left_on='COUNTRY', right_on='name')

mutation_list = ['del:3-9', 'del:2-20', 'del:16', 'del:20']

result['number'] = [len(x.split(',')) for x in result['NUC_PROFILE']]
new_res = result.groupby(['COUNTRY', 'lon', 'lat', 'RELEASE_DATE'])['number'].sum().reset_index()

fig0 = px.scatter_mapbox(
    new_res,
    lat="lat",
    lon="lon",
    size="number",
    #size_max=15,
    animation_frame="RELEASE_DATE",
    zoom=10,
    mapbox_style="carto-positron"
)
####################################################



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
                        {'label': 'MT903344.1', 'value': 'MT903344.1'},
                        {'label': 'NC_063383.1', 'value': 'NC_063383.1'},
                        {'label': 'ON563414.3', 'value': 'ON563414.3'},
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
            style={'width':'15%', 'height':'190%','float':'left'},
            children=[
                dcc.Checklist(
                    className ='checkbox_1',
                    id='vizual-method-list',
                    options=[
                            {'label': 'Frequencies', 'value': 'freq'},
                            {'label': 'Increasing Trend', 'value': 'trend-inc'},
                            {'label': 'Decreasing Trend', 'value': 'trend-dec'},
                            {'label': 'Constant Trend', 'value': 'trend-const'}
                    ],
                    value=['I1MT'],
                    labelStyle={'display': 'block'}
                )
            ]
        ),

        html.Br(style={'line-height': '10'}),
        html.Br(style={'line-height': '10'}),
        user_query_input,
        html.Br(style={'line-height': '10'}),

        html.Div(id="user-output", children=""),
        html.Div(
            [
                dash_table.DataTable(
                    id="my-output-df",
                    page_current=0,
                    page_size=10,
                    style_table={
                        'maxHeight': '50ex',
                        'overfrlowY': 'scroll',
                        'width': '40%',
                        'minWidth': '40%'
                    }
                ),
            ]
        ),
        html.Div(
            [
                html.Br(),
                html.H1("Here is a map"),
                dcc.Graph(figure=fig0),
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


'''
@app.callback(
    Output(component_id="user-output", component_property="children"),
    Output(component_id="my-output-df", component_property="data"),
    Output(component_id="my-output-df", component_property="columns"),
    Input("btn-1", "n_clicks"),
    State("my-input", "value"),
)
def update_output_sonar(n_clicks, commands):
    # calls backend
    _list = commands.split()
    print(_list)
    # need to implement mini parser
    data = None
    columns = None
    try:
        args = parse_args(_list)
        output = ""
        if args.tool == "list-prop":
            df = sonarBasicsChild.list_prop()
            columns = [{"name": col, "id": col} for col in df.columns]
            data = df.to_dict(orient="records")
        elif args.tool == "match":
            _tmp_output = match_controller(args)
            if type(_tmp_output) == int:
                output = _tmp_output
            else:
                df = _tmp_output
                columns = [{"name": col, "id": col} for col in df.columns]
                data = df.to_dict(orient="records")
        elif args.tool == "dev":
            get_freq_mutation(args)
        else:

            output = "This command is not available."
    except argparse.ArgumentError as exc:
        output = exc.message
    except SystemExit:
        output = "error: unrecognized arguments/commands"
    return output, data, columns
'''
