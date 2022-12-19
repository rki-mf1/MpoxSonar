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
                Thank you for using our tool! We would love to get your feedback and improve over time. Please don't hesitate to contact us per E-mail using the following address: <a href="mailto:FuchsS@rki.de">FuchsS (at) rki.de</a>. 
            """
            ),
            html.Br(),
            html.Div(
                children="""
                If you have any questions or wishes regarding the functionalities of the website, please open an issue on our GitHub repository.
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
        ],
    ),
)
