from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length
from app.models import User

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)
    
class EditProfileForm(Form):
    username = StringField('username', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])
    
    def __init__(self, original_username, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_username = original_username
    
    def validate(self):
        if not Form.validate(self):
            return False
        if self.username.data == self.original_username:
            return True
        if self.username.data != User.make_valid_username(self.username.data):
            self.username.errors.append(gettext("Username non valido. Impossibile utilizzare caratteri che non siano lettere, numeri, il punto e l'underscore (_)"))
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user != None:
            self.username.errors.append("{0} è un username già in uso, scegline un'altro.".format(self.username.data))
            return False
        return True
        
class PostForm(Form):
    post = StringField('post', validators=[DataRequired()])
