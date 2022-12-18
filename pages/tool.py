import os

import dash
from dash import dash_table
from dash import dcc
from dash import html
import pandas as pd
import plotly.express as px

from pages.tool_page_components import user_query_input

# from src.covsonar.app_controller import get_freq_mutation
# from src.covsonar.app_controller import match_controller
# from src.covsonar.app_controller import sonarBasics
# from src.covsonar.sonar import parse_args


dash.register_page(__name__, path="/Tool")


# TEST DATA EXPERIMENT
note_data = pd.read_csv(os.getcwd()+"/"+"data/Data.csv")
coord_data = pd.read_csv(os.getcwd()+"/"+"data/location_coordinates.csv")

result = pd.merge(note_data, coord_data, left_on="COUNTRY", right_on="name")

mutation_list = ["del:3-9", "del:2-20", "del:16", "del:20"]

result["number"] = [len(x.split(",")) for x in result["NUC_PROFILE"]]
new_res = (
    result.groupby(["COUNTRY", "lon", "lat", "RELEASE_DATE"])["number"]
    .sum()
    .reset_index()
)

fig0 = px.scatter_mapbox(
    new_res,
    lat="lat",
    lon="lon",
    size="number",
    # size_max=15,
    animation_frame="RELEASE_DATE",
    zoom=0.5,
    mapbox_style="carto-positron",
)
#



######### added by Jorge ##########
## inspired by covradar/server.py ##
#
from data import load_all_sql_files, get_database_connection
#
# possible ToDo's:
#
#    pickle files
#    register_callbacks_report_latest 
#    register_dashapp (see covradar/frontend/app/__init__.py)
#
if 'MYSQL_DB' in os.environ:
    db_name = os.environ.get('MYSQL_DB')
    db_connection = get_database_connection(db_name)
    df_dict_mpox = load_all_sql_files(db_name)
else:
    df_dict_mpox = pd.read_csv("df_mpox['propertyView'].csv")
#
#### shaping the data for the map:
#### and experimentation !
## db = mpox_testdata@asusdebian ##
import numpy as np
mpox_testdata = df_dict_mpox['propertyView']
alpha = mpox_CONTRY_absolute_counts = mpox_testdata[mpox_testdata['property.name'] == 'COUNTRY']['value_text'].value_counts()
betha = pd.DataFrame(data=np.array([alpha.index, alpha.values]), index = ['COUNTRY', 'OCCURRENCES']).T
betha['OCCURRENCES'] = betha['OCCURRENCES'].astype(str).astype(int)
#
mpox_fig = px.scatter_geo(
    betha,
    locations='COUNTRY',
    locationmode='country names',
    #color='MUTATION',
    size='OCCURRENCES'#,
#    title="first sample on"+QUERY+"last sample on"+QUERY
)
mpox_fig_2 = px.choropleth(
    data_frame=betha,
    locations='COUNTRY',
    locationmode='country names',
    color='OCCURRENCES',
    color_continuous_scale='sunsetdark', # brwnyl burg burgyl darkmint jet oranges reds sunsetdark turbo ylorbr matter balance
    center=None#,
#    center=dict(lat=51.5, lon=10.5), 
#    hover_name=None, hover_data=None, custom_data=None,
#    animation_frame=None, animation_group=None,
#    category_orders=None, labels=None, color_discrete_sequence=None, color_discrete_map=None,
#    range_color=None, color_continuous_midpoint=None,projection=None, scope=None, 
#    fitbounds=None, basemap_visible=None, title=None, template=None, width=None, height=None
)
import plotly.graph_objects as go
mpox_fig_3 = go.Figure(
    data = go.Choropleth(
        locations = betha['COUNTRY'],
        z = betha['OCCURRENCES'],
        locationmode = 'country names',
        colorscale = 'Reds',
        colorbar_title = 'OCCURRENCES'
))
mpox_fig_2.update_layout(
    geo=dict(scope='world'),
#    autosize=False,
    margin=dict(l=30,r=0,b=0,t=30)#,
)
##################################



layout = html.Div(
    [
        # check box with references
        html.Div(
            style={"width": "10%", "height": "100%", "float": "left"},
            children=[
                dcc.Checklist(
                    className="checkbox_1",
                    id="references-list",
                    options=[
                        {"label": "MT903344.1", "value": "MT903344.1"},
                        {"label": "NC_063383.1", "value": "NC_063383.1"},
                        {"label": "ON563414.3", "value": "ON563414.3"},
                    ],
                    labelStyle={"display": "block"},
                )
            ],
        ),
        # checkbox with mutations
        html.Div(
            style={"width": "10%", "height": "100%", "float": "left"},
            children=[
                dcc.Checklist(
                    className="checkbox_1",
                    id="mutation-list",
                    options=[
                        {"label": "some mutation", "value": "I1ST2"},
                        {"label": "some mutation", "value": "I2ST2"},
                        {"label": "some mutation", "value": "I3ST2"},
                        {"label": "some mutation", "value": "I4ST2"},
                    ],
                    labelStyle={"display": "block"},
                )
            ],
        ),
        html.Div(
            style={"width": "15%", "height": "190%", "float": "left"},
            children=[
                dcc.Checklist(
                    className="checkbox_1",
                    id="vizual-method-list",
                    options=[
                        {"label": "Frequencies", "value": "freq"},
                        {"label": "Increasing Trend", "value": "trend-inc"},
                        {"label": "Decreasing Trend", "value": "trend-dec"},
                        {"label": "Constant Trend", "value": "trend-const"},
                    ],
                    value=["I1MT"],
                    labelStyle={"display": "block"},
                )
            ],
        ),
        html.Br(style={"line-height": "10"}),
        html.Br(style={"line-height": "10"}),
        user_query_input,
        html.Br(style={"line-height": "10"}),
        html.Div(id="user-output", children=""),
        html.Div(
            [
                dash_table.DataTable(
                    id="my-output-df",
                    page_current=0,
                    page_size=10,
                    style_table={
                        "maxHeight": "50ex",
                        "overfrlowY": "scroll",
                        "width": "40%",
                        "minWidth": "40%",
                    },
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
                        html.Button("Download CSV", id="csv-download"),
                        dcc.Download(id="df-download"),
                    ]
                ),
            ]
        ),
    ]
)


"""
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
"""
