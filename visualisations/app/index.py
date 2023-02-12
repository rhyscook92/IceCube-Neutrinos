from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from app import app, server
from pages import neutrino_scatter

app.layout = html.Div(
    children=neutrino_scatter.content(app), style={"background-color": "white"}
)

if __name__ == "__main__":
    app.run_server(debug=False)