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

####################################
# DATABASE Setup
# ####################################

username = 'anusha'
password = 'Password123'
database = 'cloud_db'
hostname = 'cloud-server.mysql.database.azure.com'
root_ca = '/Users/anusha/Desktop/Cloud_Computing/CS6065_Final_Public/DigiCertGlobalRootCA.crt.pem'

db_uri = f"mysql+pymysql://{username}:{password}@{hostname}/{database}"

engine = create_engine(
   f"mysql+pymysql://{username}:{password}@{hostname}/{database}",
   connect_args = {
    "ssl": {
            "ssl_ca": root_ca
        }
   }
)

db = SQLAlchemy()
config = configparser.ConfigParser()

print ("\n\n {0} \n\n".format(engine))

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable = False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
Users_tbl = Table('users', Users.metadata)

####################################
# Application Setup
####################################

external_stylesheets = [
    dbc.themes.FLATLY,
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]

app = DashProxy(__name__, external_stylesheets=external_stylesheets, transforms=[MultiplexerTransform()])
app.title = 'Cloud Computing Final Project'

server = app.server
app.config.suppress_callback_exceptions = True
# config
server.config.update(
    SECRET_KEY=os.urandom(12),
    SQLALCHEMY_DATABASE_URI=db_uri,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MYSQL_SSL_CA = root_ca
)
db.init_app(server)
# Setup the LoginManager for the server
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'
#User as base
# Create User class with UserMixin
class Users(UserMixin, Users):
    pass

