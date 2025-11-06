import connexion
from flask import Flask
import jwt
from config import Config
import datetime


app = connexion.FlaskApp(__name__, specification_dir="./")
flask_app = app.app
flask_app.config.from_object(Config)

def encrypt_token(email):
     token = jwt.encode({
            'user': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
     
     return token


