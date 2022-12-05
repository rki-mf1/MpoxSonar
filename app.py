import dash
from dash import Input, Output
from dash import Dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

row1 = html.Tr([
    html.Td(
        html.Ul([
                html.Li(
                    [html.A("About MPXRadar", href="About", style={'color': 'black'})]),
                html.Li(
                    [html.A("Tool", href="Tool", style={'color': 'black'})]),
                html.Li(
                    [html.A("Help", href="Help", style={'color': 'black'})]),
                html.Li(
                    [html.A("Imprint", href="Home", style={'color': 'black'})]),
                html.Li(
                    [html.A("Contact Us", href="Contact", style={'color': 'black'})])
                ], style={'list-style-type': 'none'}), style={'text-align': 'left'}),
    html.Td(
        html.Ul([
                html.Li([html.Div(children="Supported by:")]),
                html.Li([html.Img(src=r'assets/Bundesministerium_für_Wirtschaft_und_Energie_Logo.svg.png', alt='Img_RKI',
                                  style={'height': 'auto', 'width': '50%', 'min-width': '100px'})]),
                html.Li([html.Div(children="on the basis of a decision")]),
                html.Li([html.Div(children="by the German Bundestag")]),
                ], style={'list-style-type': 'none'})),
    html.Td(html.Img(src=r'assets/denbi_cloud_logo.png', alt='Img_RKI',
                         style={'float': 'right', 'height': 'auto', 'width': '80%', 'min-width': '100px', 'margin-top': '200px'}),)], style={'border': 'none'})
table_body = [html.Tbody([row1])]

table = dbc.Table(table_body, bordered=True)

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
        html.Footer([dbc.Table(table)]),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
