from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
import pyodbc
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

db = SQLAlchemy()
DB_NAME = "database.db"
sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
Session = sessionmaker(bind=sqlcon)
session = Session()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'aosdapodkpasodkpasdkopk asidjsaiodjasoid'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    db.init_app(app)

    from .views import views

    app.register_blueprint(views,url_prefix='/')

    from .models import User

    with app.app_context():
        db.create_all()


    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created database!')