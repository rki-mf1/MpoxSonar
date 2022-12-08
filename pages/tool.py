import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

import plotly.express as px
import pandas as pd


dash.register_page(__name__, path="/Tool")

#####experiment on NOTE data#######
note_data = pd.read_csv('data/Data.csv')
coord_data = pd.read_csv('data/location_coordinates.csv')

result = pd.merge(note_data, coord_data, left_on='COUNTRY', right_on='name')

#print(note_data.columns)

result['number'] = [len(x.split(',')) for x in result['NUC_PROFILE']]
new_res = result.groupby(['COUNTRY', 'lon', 'lat'])['number'].sum().reset_index()
print(new_res.columns)

fig0 = px.scatter_mapbox(
    new_res,
    lat="lat",
    lon="lon",
    size="number",
    #size_max=15,
    zoom=10,
    mapbox_style="carto-positron"
)

print(new_res)
###########

###mutations and countries####
new_data = pd.read_csv('/home/ivan/MPXRadar-frontend/pages/out.csv')

new_fig = px.scatter_geo(
    new_data,
    locations='COUNTRY',
    locationmode='country names',
    color='MUTATION',
    size='OCCURENCES'
)
##############################

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
    mapbox_style="carto-positron"
)
#######################################


card = dbc.Card(
    dbc.CardBody(
        [
            html.Div(
                [
                    html.Div(
                        [
                            "direct MPXSonar query: ",
                            html.Br(),
                            dcc.Input(
                                id="my-input", type="text", size="100"
                            ),
                            html.Button('Run direct MPXSonar query', id='btn-1', n_clicks=0),
                        ]
                    )
                ]
            )
        ]
    ),
    style={"width": "18rem"},
)



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
        card,
        html.Br(style={'line-height': '10'}),
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
