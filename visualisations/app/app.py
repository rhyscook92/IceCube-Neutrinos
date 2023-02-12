import flask
import dash
import dash_bootstrap_components as dbc


server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.COSMO])
