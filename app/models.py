from flask import current_app, url_for, request, redirect, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin
from app import lm, db
from datetime import datetime
from hashlib import md5 

class Post(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)


# ******** Followers Table **********
# No need for a Model here, it's just an association table 

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)



class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(10), nullable=False)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    posts = db.relationship('Post', backref='author', lazy='dynamic') # For a one-to-many relationship a db.relationship field is normally defined on the "one" side. 
                                                                      # With this relationship we get a user.posts member that gets us the list of posts from the user. 
                                                                      # The backref argument defines a field that will be added to the objects of the "many" class that points back at the "one" object. 
                                                                      # In our case this means that we can use post.author to get the User instance that created a post.
    # Many-to-many self-referential relationship
    followed = db.relationship('User',                                      # 'User' is the right side entity that is in this relationship (the left side entity is the parent class).
                               secondary=followers,                         # secondary indicates the association table that is used for this relationship.
                               primaryjoin=(followers.c.follower_id == id), # secondaryjoin indicates the condition that links the right side entity (the followed user) with the association table.
                               secondaryjoin=(followers.c.followed_id == id), #backref defines how this relationship will be accessed from the right side entity.
                               backref=db.backref('followers', lazy='dynamic'), # lazy is similar to the parameter of the same name in the backref, but this one applies to the regular query instead of the back reference.
                               lazy='dynamic')
                               
    def __init__(self , username ,password , email):
        self.username = username
        self.password = password
        self.email = email
    
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
    
    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)
        # d=mm: If one have no Gravatar, return a "mystery man" (mm) image
        # s=%d: return scaled to size.
    
    @staticmethod
    def unique_username(username):
        if User.query.filter_by(username=username).first() is None:
            return username
        version = 1
        while True:
            new_username = username + str(version)
            if User.query.filter_by(username=new_username).first() is None:
                break
            version += 1
        return new_username
        
    @staticmethod
    def unique_email(email):
        if User.query.filter_by(email=email).first() is None:
            return True
        return False
        
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    # http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-viii-followers-contacts-and-friends 
    def followed_posts(self):
        return Post.query.join(followers, 
                                (followers.c.followed_id == Post.user_id)
                              ).filter(followers.c.follower_id == self.id
                              ).order_by(Post.timestamp.desc()
                              )
    def sorted_posts(self):
        return self.posts.order_by(Post.timestamp.desc())
    
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))
    


    

