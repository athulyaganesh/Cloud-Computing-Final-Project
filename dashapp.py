from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import State
from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform
from sqlalchemy import Table, create_engine
from sqlalchemy.connectors import pyodbc
from pyodbc import connect, Cursor
from sqlalchemy.sql import select
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import warnings
import os
from flask_login import login_user, logout_user, current_user, LoginManager, UserMixin
import configparser
import plotly.express as px
import pandas as pd
import base64
import io
warnings.filterwarnings("ignore")
import dash
import dash_html_components as html

external_stylesheets = [
    dbc.themes.FLATLY,
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]

# app = dash.Dash(__name__)
app = DashProxy(__name__, external_stylesheets=external_stylesheets, transforms=[MultiplexerTransform()])
app.title = 'Cloud Computing Final Project'
app.layout = html.Div("Hello World")

if __name__ == '__main__':
    app.run_server(debug=True)