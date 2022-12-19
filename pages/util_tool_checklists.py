from dash import html
import dash_bootstrap_components as dbc


checklist_1 = dbc.Card(
    dbc.CardBody(
        [
            dbc.Label("Reference genome: "),
            dbc.Checklist(
                options=[
                    {"label": "MPXV-COG_2003_358", "value": 1},
                    {"label": "MPXV-USA_2003_039", "value": 2},
                    {"label": "MPXV-xxx", "value": 3},
                    {"label": "...", "value": 4},
                ],
                value=[],
                id="1_checklist_input",
            ),
        ]
    )
)

checklist_2 = dbc.Card(
    dbc.CardBody(
        [
            dbc.Label("Mutatioins displayed: "),
            dbc.Checklist(
                options=[
                    {"label": "All", "value": 1},
                    {"label": "Mutation 1", "value": 2},
                    {"label": "Mutation 2", "value": 3},
                    {"label": "...", "value": 4},
                ],
                value=[],
                id="2_checklist_input",
            ),
        ],
    )
)

checklist_3 = dbc.Card(
    dbc.CardBody(
        [
            dbc.Label("Visualisatioin method: "),
            dbc.Checklist(
                options=[
                    {"label": "Frequencies", "value": 1},
                    {"label": "Increasing Trend", "value": 2},
                    {"label": "Decreasing Trend", "value": 3},
                    {"label": "Constant Trend", "value": 4},
                ],
                value=[],
                id="3_checklist_input",
            ),
        ],
    )
)

checklist_4 = dbc.Card(
    dbc.CardBody(
        [
            dbc.Label("Sequencing Technology used: "),
            dbc.Checklist(
                options=[
                    {"label": "All", "value": 1},
                    {"label": "Illumina", "value": 2},
                    {"label": "Nanopore", "value": 3},
                    {"label": "...", "value": 4},
                ],
                value=[],
                id="4_checklist_input",
            ),
        ],
    )
)


query_card = dbc.Card(
    dbc.CardBody(
        [
            html.Div(
                [
                    dbc.Checklist(
                        options=[
                            {"label": "Direct MPXSonar query input: ", "value": 1}
                        ],
                        id="query=input",
                    )
                ]
            ),
            html.Div(
                [
                    dbc.Input(
                        id="query_input",
                        placeholder="Type here MPXSonar query...",
                        type="text",
                        size="100%",
                    ),
                ]
            ),
        ]
    ),
    style={"width": "100%"},
    className="relative",
)