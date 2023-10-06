from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os


load_dotenv()
secret_key = os.getenv('SECRET_KEY')
database_uri = os.getenv('DATABASE_URI')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SECRET_KEY'] = secret_key
db = SQLAlchemy(app)


from app import views
from app import admin_views