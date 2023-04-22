import csv
import math
from dash import Dash, html, dcc, dash_table
import dash
# import dash_bootstrap_components as dbc
from dash.dependencies import State
from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform
from sqlalchemy import Table, create_engine, MetaData
from sqlalchemy.sql import select
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import warnings
import os
from flask_login import login_user, logout_user, current_user, LoginManager, UserMixin
import configparser
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
# import plotly.express as px
# import pandas as pd
import pandas as pd

username = 'anusha'
password = 'Password123'
database = 'sample3'
hostname = 'cloud-server.mysql.database.azure.com'
root_ca = '/Users/anusha/Desktop/Cloud_Computing/CS6065_Final_Public/DigiCertGlobalRootCA.crt.pem'

db_uri = f"mysql+pymysql://{username}:{password}@{hostname}/{database}"

engine = create_engine(
    f"mysql+pymysql://{username}:{password}@{hostname}/{database}",
    connect_args={
        "ssl": {
            "ssl_ca": root_ca
        }
    },
    echo=True
)

db = SQLAlchemy()
config = configparser.ConfigParser()
conn = engine.connect()

print(engine)

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50))
    password = Column(String(1000))
    email = Column(String(50))

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# # create a metadata object and load the table metadata
# metadata = MetaData()
# table = Table('users', metadata, autoload=True, autoload_with=engine)

# # select all rows from the table
# query = table.select()

# # execute the query and fetch the results
# result = conn.execute(query).fetchall()

# print(len(result))

