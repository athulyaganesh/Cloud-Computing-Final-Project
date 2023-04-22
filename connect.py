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
app.layout = html.Div("Please work!")

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
login_manager.login_view = '/'

#User as base
# Create User class with UserMixin
class Users(UserMixin, Users):
    pass

def display_dashboard():
    dashboard_layout = html.Div(children=[

        html.H1(children=['Cloud Computing Final Project']),
        html.P(['Athulya Ganesh', html.Br(),'Anusha Chitranshi']),
        html.Hr(),
        html.H4("Retail Dashboard"),
        dcc.Link(html.Button("Login", style={'backgroundColor': 'white'}), href="/", refresh=True)])
    return dashboard_layout

####################################
# USER LOGIN AND PAGE ROUTING
####################################

# create user layout
create = html.Div([ 
        html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),
        html.H1('Cloud Computing Final Project'),html.Br(),
        html.H2('''Please sign up to continue:''', id='h1'),
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
        html.Br(),html.Br(),
        html.Div(id='container-button-basic'),
        dcc.Link(html.Button("Login", style={'backgroundColor':'white'}), href="/", refresh=True),
        html.Br(), html.Br() ,html.Br(),html.Br(),
    ], style={'margin' : 'auto', 'width' : '50%', 'text-align' : 'center','backgroundColor':'#DAF7A6' })#end div

# login layout
login =  html.Div([dcc.Location(id='url_login', refresh=True),
        html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),html.Br()
            , html.H1("Cloud Computing Final Project"),
            html.Br()
            , html.H2('''Please log in to continue:''', id='h1'), html.Br()
            , dcc.Input(placeholder='Enter your username',
                    type='text',
                    id='uname-box'), html.Br(),  html.Br()
            , dcc.Input(placeholder='Enter your password',
                    type='password',
                    id='pwd-box'), html.Br(), html.Br()
            , html.Button(children='Login',
                    n_clicks=0,
                    type='submit',
                    id='login-button', style={'backgroundColor':'white'}),  html.Br(),  html.Br()
            , html.Div(children='', id='output-state'),
            dcc.Link(html.Button("Create an Account", style={'backgroundColor':'white'}), href="/create", refresh=True),
            html.Br(), html.Br(), html.Br(), html.Br()
        ] , style={'margin' : 'auto', 'width' : '50%', 'text-align' : 'center', 'backgroundColor':'#F7B3A6'}, ) #end div

success = display_dashboard()

failed = html.Div([ dcc.Location(id='url_login_df', refresh=True)
            , html.Div([html.H2('Log in Failed. Please try again.')
                    ,dcc.Link(html.Button("Login", style={'backgroundColor':'white'}), href="/", refresh=True),
                ]) #end div
        ], style={'margin' : 'auto', 'width' : '50%', 'text-align' : 'center'}) #end div


logout = html.Div([dcc.Location(id='logout', refresh=True)
        , html.Br()
        , html.Div(html.H2('You have been logged out - Please login'))
        , html.Br()
        ,dcc.Link(html.Button("Login", style={'backgroundColor':'white'}), href="/", refresh=True),
    ], style={'margin' : 'auto', 'width' : '50%', 'text-align' : 'center'})#end div


questions = html.Div([
    html.Div([
    html.H1('Retail Questions'),html.Br(),
    html.Marquee(html.H2("WHAT DO WE WANT???")),html.Br(),
    ], style={'margin':'auto', 'text-align' : 'center', 'backgroundColor':'#C5DBFC'}),
    html.Div([
        html.P(html.B('1. How does customer engagement change over time? Do households spend less or more? What categories are growing or shrinking with changing customer engagement?'))
    ]),
    html.P(html.B('2. What demographic factors appear to affect customer engagement? How do they C.E. with certain categories? How might we re-engage customers within the store? Or within a certain category?')),
    html.P(html.B('3. What categories are growing or shrinking with changing customer engagement?')),
    html.P(html.B('4. Which demographic factors (e.g. household size, presence of children, income) appear to affect customer engagement?')),
    html.P(html.B('5. Provide a short write-up on which Data Science Predictive modeling techniques would be most suitable to reasonably answer the questions below.  Please see The Top 10 Machine Learning Algorithms for model section. (No more than 200 words) (2 points)')),

    html.Div([
    html.H1('Retail Answers'),html.Br(),
    html.Marquee(html.H2("MONEY!!!!!!")),html.Br(),
], style={'margin': 'auto', 'text-align': 'center', 'backgroundColor':'#C5DBFC'}),

    html.Div([
        html.P(html.I('1. TODO: ANSWER THIS '))
    ]),
    html.P(html.I('2. TODO: ANSWER THIS ')), #TODO
    html.P(html.I('3. TODO: ANSWER THIS ')), #TODO
    html.P(html.I('4. TODO: END MY LIFE')), #TODO
    html.P(html.I('5. TODO: GIVE ME AN A PLS')) #TODO
], style={'margin': 'auto', 'text-align': 'center', 'backgroundColor':'#C5DBFC'})


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
        return login
    elif pathname == '/create':
        return create
    elif pathname == '/success':
        if current_user.is_authenticated:
            return success
        else:
            return failed
    #elif pathname =='/data':
       # if current_user.is_authenticated:
           # return data
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            return logout
        else:
            return failed
    elif pathname == '/questions':
        return questions
    else:
        return 'Check your URL and try again.'

@app.callback(
    Output('url_login', 'pathname')
    , [Input('login-button', 'n_clicks')]
    , [State('uname-box', 'value'), State('pwd-box', 'value')])

def successful(n_clicks, input1, input2):
    user = Users.query.filter_by(username=input1).first()
    if user:
        if check_password_hash(user.password, input2):
            login_user(user)
            return '/success'
        else:
            pass
    else:
        pass

@app.callback(
    Output('output-state', 'children')
    , [Input('login-button', 'n_clicks')]
    , [State('uname-box', 'value'), State('pwd-box', 'value')])
def update_output(n_clicks, input1, input2):
    if n_clicks > 0:
        user = Users.query.filter_by(username=input1).first()
        if user:
            if check_password_hash(user.password, input2):
                return ''
            else:
                return 'Incorrect username or password'
        else:
            return 'Incorrect username or password'
    else:
        return ''
@app.callback(
    Output('url_login_success', 'pathname')
    , [Input('back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/'
@app.callback(
    Output('url_login_df', 'pathname')
    , [Input('back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/'
# Create callbacks
@app.callback(
    Output('url_logout', 'pathname')
    , [Input('back-button', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='80', debug=True)