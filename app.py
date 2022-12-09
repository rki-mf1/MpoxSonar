import dash
from dash import Dash
from dash import html
import dash_bootstrap_components as dbc

from pages.util_footer_table import row1

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

table_body = [html.Tbody([row1])]

table = dbc.Table(table_body, bordered=True)

app.layout = html.Div(
    [
        html.H1("MPox Radar", style={"display": "inline-block"}),
        html.Img(
            src=r"assets/hpi_logo.png",
            alt="Img_HPI",
            style={"float": "right", "height": "10%", "width": "10%"},
            className="responsive",
        ),
        html.Img(
            src=r"assets/rki_logo.png",
            alt="Img_RKI",
            style={"float": "right", "height": "10%", "width": "10%"},
            className="responsive",
        ),
        html.Img(
            src=r"assets/DAKI-FWS_logo.png",
            alt="Img_DAKI-FWS",
            style={"float": "right", "height": "10%", "width": "10%"},
            className="responsive",
        ),
        html.Div("A genomic surveiillance dashboard for MonkeyPox."),
        html.Br(),
        html.Div(
            [
                dbc.Button(
                    "About",
                    href="About",
                    outline=True,
                    color="primary",
                    className="me-1",
                ),
                dbc.Button(
                    "Tool", href="Tool", outline=True, color="primary", className="me-1"
                ),
                dbc.Button(
                    "Help", href="Help", outline=True, color="primary", className="me-1"
                ),
                dbc.Button(
                    "Imprint & Privacy Policy",
                    href="Imprint",
                    outline=True,
                    color="primary",
                    className="me-1",
                ),
                dbc.Button(
                    "Contact",
                    href="Contact",
                    outline=True,
                    color="primary",
                    className="me-1",
                ),
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
        html.Div([html.Hr(), html.Footer([dbc.Table(table)])], className="app_footer"),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
