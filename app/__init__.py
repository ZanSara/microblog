# init script for the app package

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import basedir
import os

app = Flask(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = 'Login completato con successo'


from app import views, models    
# Why the import statement is at the end and not at the beginning of the script? To avoid circular references, because the views module needs to import the app variable defined in this script. Putting the import at the end avoids the circular import error.

