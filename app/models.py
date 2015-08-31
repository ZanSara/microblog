from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic') # For a one-to-many relationship a db.relationship field is normally defined on the "one" side. 
                                                                      # With this relationship we get a user.posts member that gets us the list of posts from the user. 
                                                                      # The backref argument defines a field that will be added to the objects of the "many" class that points back at the "one" object. 
                                                                      # In our case this means that we can use post.author to get the User instance that created a post.
    def __repr__(self):
        return '<User %r>' % (self.nickname)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)
