# Starts up the server with our application:
# The script imports the app variable from our app package and invokes its run method to start the server.

#!flask/bin/python

from app import app
app.run(debug=True)
