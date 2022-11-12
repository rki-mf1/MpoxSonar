import argparse

from apps.app_controller import get_freq_mutation
from apps.app_controller import match_controller
from apps.app_controller import sonarBasicsChild
from dash import Dash
from dash import dash_table
from dash import dcc
from dash import html
from dash import Input
from dash import Output
from dash import State
import dash_bootstrap_components as dbc
from mpxsonar.sonar import parse_args

# stylesheet with the .dbc class
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])
custom_cmd_cards = html.Div(
    [
        dbc.Card(
            [
                dbc.CardHeader([html.H3("MPXsonar command!")]),
                dbc.CardBody(
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            "sonar: ",
                                            dcc.Input(
                                                id="my-input",
                                                value="match --count",
                                                type="text",
                                                size="100",
                                            ),
                                        ]
                                    ),
                                    html.Br(),
                                    html.Label("MPXSonar command:"),
                                    html.Div(id="my-command", children=""),
                                ]
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        dbc.Button(
                                            id="submit-button-state",
                                            n_clicks=0,
                                            children="Submit",
                                            color="primary",
                                            className="mb-2",
                                        ),
                                    ),
                                ]
                            ),
                        ]
                    ),
                ),
            ],
            className="mb-3",
        ),
        dbc.Card(
            [
                html.Label("Output:"),
                html.Div(id="my-output", children=""),
                html.Div(
                    [
                        dash_table.DataTable(
                            id="my-output-df",
                            page_current=0,
                            page_size=10,
                            style_data={
                                "whiteSpace": "normal",
                                "height": "auto",
                            },
                            style_table={"overflowX": "auto"},
                            export_format="csv",
                        ),
                    ]
                ),
            ],
            body=True,
        ),
    ]
)

app.layout = dbc.Container(
    [
        dbc.Row([]),
        html.Hr(),
        dbc.Row(
            [
                custom_cmd_cards,
                html.Br(),
            ]
        ),
    ]
)


@app.callback(
    Output(component_id="my-command", component_property="children"),
    Input(component_id="my-input", component_property="value"),
)
def update_output_div(input_value):
    return f"sonar {input_value}"


@app.callback(
    Output(component_id="my-output", component_property="children"),
    Output(component_id="my-output-df", component_property="data"),
    Output(component_id="my-output-df", component_property="columns"),
    Input("submit-button-state", "n_clicks"),
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


if __name__ == "__main__":
    app.run_server(debug=True, host="127.0.0.1")
