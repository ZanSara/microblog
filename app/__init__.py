# init script for the app package

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


from app import views, models    
# Why the import statement is at the end and not at the beginning of the script? To avoid circular references, because the views module needs to import the app variable defined in this script. Putting the import at the end avoids the circular import error.
