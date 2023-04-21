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

# app = dash.Dash(__name__)
app = DashProxy(__name__, external_stylesheets=external_stylesheets, transforms=[MultiplexerTransform()])
app.title = 'Cloud Computing Final Project'
app.layout = html.Div("Hello World")

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

######################
# Graphs
######################

graphs = {} # container to hold all figures
households_df = None
transactions_df = None
products_df = None
transactions_combined_household_df = None
all_three_combined_df = None

def serve_layout_demo():
    dashboard_layout = html.Div(children=[

        html.H1(children=['Cloud Computing Final Project']),
        html.P(['Athulya Ganesh', html.Br(),'Anusha Chitranshi']),
        html.Hr(),
        html.H4("Retail Dashboard")])
    return dashboard_layout


####################################
# USER LOGIN AND PAGE ROUTING
####################################

# create user layout
create = html.Div([ 
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.H1('Cloud Computing Final Project'),
        html.P('Use the form below to create a user account'),
        html.Br(),
        dcc.Location(id='create_user', refresh=True),
        dcc.Input(id="username"
            , type="text"
            , placeholder="Enter username"
            , maxLength =15),
        html.Br(),
        html.Br(),
        dcc.Input(id="password"
            , type="password"
            , placeholder="Enter password"),
        html.Br(),
        html.Br(),
        dcc.Input(id="email"
            , type="email"
            , placeholder="Enter email"
            , maxLength = 50),
        html.Br(), html.Br(),
        html.Button('Create User', id='submit-val', n_clicks=0, style={'backgroundColor':'white'}),
        html.Br(),html.Br(),html.Br(),html.Br(),
        html.Div(id='container-button-basic')
    ], style={'margin' : 'auto', 'width' : '50%', 'text-align' : 'center','backgroundColor':'#DAF7A6' })#end div

# login layout
login =  html.Div([dcc.Location(id='url_login', refresh=True)
            , html.H2('''Please log in to continue:''', id='h1')
            , dcc.Input(placeholder='Enter your username',
                    type='text',
                    id='uname-box'), html.Br()
            , dcc.Input(placeholder='Enter your password',
                    type='password',
                    id='pwd-box'), html.Br(), html.Br()
            , html.Button(children='Login',
                    n_clicks=0,
                    type='submit',
                    id='login-button')
            , html.Div(children='', id='output-state')
        ] , style={'margin' : 'auto', 'width' : '50%', 'text-align' : 'center'}) #end div

success = serve_layout_demo()

failed = html.Div([ dcc.Location(id='url_login_df', refresh=True)
            , html.Div([html.H2('Log in Failed. Please try again.')
                    , html.Button(id='back-button', children='Go back', n_clicks=0)
                ]) #end div
        ], style={'margin' : 'auto', 'width' : '50%', 'text-align' : 'center'}) #end div
logout = html.Div([dcc.Location(id='logout', refresh=True)
        , html.Br()
        , html.Div(html.H2('You have been logged out - Please login'))
        , html.Br()
        , html.Button(id='back-button', children='Go back', n_clicks=0)
    ], style={'margin' : 'auto', 'width' : '50%', 'text-align' : 'center'})#end div
    
app.layout= html.Div([
            html.Div(id='page-content', className='content')
            ,  dcc.Location(id='url', refresh=False)
        ])


app.layout= html.Div([
            html.Div(id='page-content', className='content')
            ,  dcc.Location(id='url', refresh=False)
        ])
# callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
@app.callback(
    Output('page-content', 'children')
    , [Input('url', 'pathname')])


def display_page(pathname):
    if pathname == '/':
        return create
    elif pathname == '/login':
        return login
    elif pathname == '/success':
        if current_user.is_authenticated:
            return success
        else:
            return failed
    elif pathname =='/data':
        if current_user.is_authenticated:
            return data
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            return logout
        else:
            return logout
    else:
        return '404'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='80', debug=True)