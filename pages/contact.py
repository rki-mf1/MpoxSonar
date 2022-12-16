import dash
from dash import dcc
from dash import html

dash.register_page(__name__, path="/Contact")

layout = (
    html.Div(
        children=[
            html.H1(children="Contact us"),
            html.Div(
                children="""
                Please open an issue on our GitHub repository. if you find a bug or if something is unclear.
            """
            ),
            html.Br(),
            html.Div(
                [
                    "GitHub repository link: ",
                    dcc.Link(
                        html.A("Link to Github"),
                        href=("https://github.com/ferbsx/MPXRadar-frontend"),
                        target="_blank",
                    ),
                ]
            ),
            html.Br(),
            html.Div(
                children="""
                You can also email us using the following address: monkeyporadar-team@xx.xx
            """
            ),
        ],
    ),
)
