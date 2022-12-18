import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/About")

layout = html.Div(
    children=[
        html.H1(children="Project Description"),
        html.Div(
            children="""
                        Monkeypox is an infectious disease caused by a smallpox virus, recently spreading in multiple countries with over 16,500 cases and declared a global emergency by the World Health Organization (citation).
                        Normally, the virus is rarely observed outside of Africa, but in recent months it has occurred in over 11 countries in other continents [CITATION].
                        This alarming behavior demands action and highlights the need for genomic surveillance and spatio-temporal analyses.
                        Therefore, the Robert Koch Institute (RKI) together with the Hasso Platter Institute (HPI) joined forces to and adapted the tool covSonar - a database framework developed at the RKI for SARS-CoV-2 - to Monkeypox.
                    """
        ),
        html.H1(children="Who are we?"),
        dbc.Card(
            [
                dbc.CardImg(
                    src="assets/Prof. Dr. Bernhard Renard.jpeg",
                    top=True,
                    style={"width": "238px", "height": "300px"},
                    className="align-self-center",
                ),
                dbc.CardBody(
                    [
                        html.P("Prof. Dr. Bernhard Renard", className="card-title"),
                    ]
                ),
            ],
            style={
                "width": "15rem",
                "margin-left": "2rem",
                "margin-right": "5rem",
                "display": "inline-block",
            },
        ),
        dbc.Card(
            [
                dbc.CardImg(
                    src="assets/Dr. Stephan Fuchs.png",
                    top=True,
                    style={"width": "238px", "height": "300px"},
                    className="align-self-center",
                ),
                dbc.CardBody(
                    [
                        html.P("Dr. Stephan Fuchs", className="card-text"),
                    ]
                ),
            ],
            style={"width": "15rem", "margin-right": "5rem", "display": "inline-block"},
        ),
        dbc.Card(
            [
                dbc.CardImg(
                    src="assets/Dr. Anna-Juliane Schmachtenberg.jpeg",
                    top=True,
                    style={"width": "238px", "height": "300px"},
                    className="align-self-center",
                ),
                dbc.CardBody(
                    [
                        html.P("Dr. Anna-Juliane Schmachtenberg"),
                    ]
                ),
            ],
            style={"width": "15rem", "margin-right": "5rem", "display": "inline-block"},
        ),
        dbc.Card(
            [
                dbc.CardImg(
                    src="assets/Alice Wittig.jpeg",
                    top=True,
                    style={"width": "238px", "height": "300px"},
                    className="align-self-center",
                ),
                dbc.CardBody(
                    [
                        html.P("Alice Wittig"),
                    ]
                ),
            ],
            style={
                "width": "15rem",
                "margin-top": "1rem",
                "margin-left": "2rem",
                "margin-right": "5rem",
                "display": "inline-block",
            },
        ),
        dbc.Card(
            [
                dbc.CardImg(
                    src="assets/Ferdous Nasri.jpeg",
                    top=True,
                    style={"width": "238px", "height": "300px"},
                    className="align-self-center",
                ),
                dbc.CardBody(
                    [
                        html.P("Ferdous Nasri"),
                    ]
                ),
            ],
            style={
                "width": "15rem",
                "margin-top": "1rem",
                "margin-right": "5rem",
                "display": "inline-block",
            },
        ),
        dbc.Card(
            [
                dbc.CardImg(
                    src="https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png",
                    top=True,
                    style={"width": "238px", "height": "300px"},
                    className="align-self-center",
                ),
                dbc.CardBody(
                    [
                        html.P("Kunaphas Kongkitimanon"),
                    ]
                ),
            ],
            style={
                "width": "15rem",
                "margin-top": "1rem",
                "margin-right": "5rem",
                "display": "inline-block",
            },
        ),
        dbc.Card(
            [
                dbc.CardImg(
                    src="https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png",
                    top=True,
                    style={"width": "238px", "height": "300px"},
                    className="align-self-center",
                ),
                dbc.CardBody(
                    [
                        html.P("Jorge Sanchez-Cortes"),
                    ]
                ),
            ],
            style={
                "width": "15rem",
                "margin-top": "1rem",
                "margin-left": "2rem",
                "margin-right": "5rem",
                "display": "inline-block",
            },
        ),
        dbc.Card(
            [
                dbc.CardImg(
                    src="assets/Injun Park.jpeg",
                    top=True,
                    style={"width": "238px", "height": "300px"},
                    className="align-self-center",
                ),
                dbc.CardBody(
                    [
                        html.P("Injun Park"),
                    ]
                ),
            ],
            style={
                "width": "15rem",
                "margin-top": "1rem",
                "margin-right": "5rem",
                "display": "inline-block",
            },
        ),
        dbc.Card(
            [
                dbc.CardImg(
                    src="assets/Ivan Tunov.png",
                    top=True,
                    style={"width": "238px", "height": "300px"},
                    className="align-self-center",
                ),
                dbc.CardBody(
                    [
                        html.P("Ivan Tunov"),
                    ]
                ),
            ],
            style={
                "width": "15rem",
                "margin-top": "1rem",
                "margin-right": "5rem",
                "display": "inline-block",
            },
        ),
        dbc.Card(
            [
                dbc.CardImg(
                    src="assets/Pavlo Konoplev.png",
                    top=True,
                    style={"width": "238px", "height": "300px"},
                    className="align-self-center",
                ),
                dbc.CardBody(
                    [
                        html.P("Pavlo Konoplev"),
                    ]
                ),
            ],
            style={
                "width": "15rem",
                "margin-top": "1rem",
                "margin-left": "2rem",
                "margin-right": "5rem",
                "display": "inline-block",
            },
        ),
        html.H1(children="Data sources:"),
        html.Div(
            children="""
                        ...
                    """
        ),
        html.H1(children="Link to code:"),
        dcc.Link(
            html.A("Link to Github"),
            href=("https://github.com/ferbsx/MPXRadar-frontend"),
            target="_blank",
        ),
        html.H1(children="Acknowledgements:"),
        html.Div(
            children="""
                        ...
                    """
        ),
    ]
)
