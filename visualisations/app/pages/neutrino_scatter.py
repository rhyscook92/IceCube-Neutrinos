from dash import Dash, dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
from utils.chart import build_event_fig
from utils.data import get_data, get_top_5_interactions, get_data_text, get_how_to_text

train, train_meta, sensor_geometry = get_data()
event_list = train_meta.event_id.unique()

data_text = get_data_text()
how_to_text = get_how_to_text()


def content(app):
    @app.callback(
        Output("scatter_3d", "figure"),
        [Input("event_dropdown", "value"), Input("auxiliary_dropdown", "value")],
    )
    def get_figure(event_id, aux_filter):
        figure = build_event_fig(
            event_id, sensor_geometry, train, train_meta, aux_filter
        )
        return figure

    @app.callback(
        Output("top_5_table", "children"),
        Input("event_dropdown", "value"),
    )
    def get_table(event_id):
        df = get_top_5_interactions(train, sensor_geometry, event_id)
        table = dbc.Table.from_dataframe(df, striped=True, bordered=True)
        return table

    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.Div("header"),
                    width=12,
                    style={"height": "4vh"},
                    class_name="bg-secondary",
                )
            ),
            dbc.Row(
                [
                    dbc.Col(width=0.5, class_name="bg-default"),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H1("Overview"),
                                    html.H4("Data"),
                                    dcc.Markdown(data_text),
                                    html.H4("How To"),
                                    dcc.Markdown(how_to_text),
                                ]
                            ),
                            color="light",
                            class_name="m-1",
                            style={"height": "95%"},
                        )
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H1("Visualisation"),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.H4("Select Event ID"),
                                                    dcc.Dropdown(
                                                        options=event_list,
                                                        value=1128590,
                                                        id="event_dropdown",
                                                    ),
                                                ]
                                            ),
                                            dbc.Col(
                                                [
                                                    html.H4("Select Auxiliary Filter"),
                                                    dcc.Dropdown(
                                                        options=[
                                                            "True Only",
                                                            "False Only",
                                                            "Either True or False",
                                                        ],
                                                        value="Either True or False",
                                                        id="auxiliary_dropdown",
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.H4("Event Animation"),
                                    dbc.Spinner(dcc.Graph(id="scatter_3d")),
                                    html.H4("Event Top 5 Interactions by Charge"),
                                    html.Div(id="top_5_table"),
                                ]
                            ),
                            color="light",
                            class_name="m-1",
                            style={"height": "95%"},
                        )
                    ),
                    dbc.Col(width=0.5, class_name="bg-default"),
                ],
                style={"height": "100%"},
            ),
            dbc.Row(
                dbc.Col(
                    html.Div("header"),
                    width=12,
                    style={"height": "6vh"},
                    class_name="bg-secondary",
                ),
            ),
        ],
        fluid=True
    )
