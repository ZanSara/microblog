from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin
from app import lm, db
from datetime import datetime
 
 
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)
    



class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    password = db.Column('password' , db.String(10))
    email = db.Column(db.String(64), nullable=True)
    registered_on = db.Column('registered_on' , db.DateTime)
    posts = db.relationship('Post', backref='author', lazy='dynamic') # For a one-to-many relationship a db.relationship field is normally defined on the "one" side. 
                                                                      # With this relationship we get a user.posts member that gets us the list of posts from the user. 
                                                                      # The backref argument defines a field that will be added to the objects of the "many" class that points back at the "one" object. 
                                                                      # In our case this means that we can use post.author to get the User instance that created a post.
    def __init__(self , username ,password , email):
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()
    
    def is_authenticated(self): # Check if the user CAN be authenticated
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return str(self.id)  # python 3
        except NameError:
            print('WARNING: running on Python2!!')
            return unicode(self.id)  # python 2    
    
    def __repr__(self):
        return '<User %r>' % (self.nickname)
    
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
    

