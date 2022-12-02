import dash
from dash import Input, Output
from dash import Dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(
    [
        html.H1("MPox Radar", style={'display': 'inline-block'}),

        html.Img(src=r'assets/hpi_logo.png', alt='Img_HPI',
                 style={'float': 'right', 'height': '10%', 'width': '10%'}, className='responsive'),
        html.Img(src=r'assets/rki_logo.png', alt='Img_RKI',
                 style={'float': 'right', 'height': '10%', 'width': '10%'}, className='responsive'),
        html.Img(src=r'assets/DAKI-FWS_logo.png', alt='Img_DAKI-FWS',
                 style={'float': 'right', 'height': '10%', 'width': '10%'}, className='responsive'),

        html.Div("A genomic surveiillance dashboard for MonkeyPox."),
        html.Br(),
        html.Div(
            [
                dbc.Button("About", href="About", outline=True,
                           color="primary", className="me-1"),
                dbc.Button("Tool", href="Tool", outline=True,
                           color="primary", className="me-1"),
                dbc.Button("Help", href="Help", outline=True,
                           color="primary", className="me-1"),
                dbc.Button("Imprint & Privacy Policy", href="Imprint", outline=True,
                           color="primary", className="me-1"),
                dbc.Button("Contact", href="Contact", outline=True,
                           color="primary", className="me-1"),
            ]
        ),
        # html.Div(
        #     [
        #         html.Div(
        #             dcc.Link(
        #                 html.A(f"{page['name']}"), href=page["relative_path"], style={'color':'black', 'display':'inline-block'}
        #             )
        #                 #f"{page['name']}", href=page["relative_path"]
        #         )
        #         for page in dash.page_registry.values()
        #     ]
        # ),
        html.Br(),
        html.Br(),
        dash.page_container,
        html.Hr(),
        html.Br(),
        # style={'height':'99999999px;', 'width':'100%', 'bottom':'0', 'left':'0', 'position':'absolute'}
        html.Footer([
            html.A("About MPXRadar", href="About", style={
                   'color': 'black', 'display': 'inline-block'}),
            html.Div(children="Supported by:", style={
                     'float': 'right', "margin-right": "250px"}),
            html.Br(),
            html.A("Contact Us", href="Contact", style={'color': 'black'}),
            html.Br(),
            html.A("Imprint", href="Home", style={'color': 'black'}),
            html.Br(),
            html.A("App:", href="Tool", style={'color': 'black'}),



            html.Div(children="on the basis of a decision"),
            html.Div(children="by the German Bundestag"),
            html.Img(src=r'assets/Bundesministerium_für_Wirtschaft_und_Energie_Logo.svg.png', alt='Img_RKI', style={'float': 'right', 'height': '10%', 'width': '10%'}, className='responsive'),]),
        html.Br(),
        html.Img(src=r'assets/denbi_cloud_logo.png', alt='Img_RKI',
                     style={'float': 'right', 'height': '10%', 'width': '10%'}, className='responsive'),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
