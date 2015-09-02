# Handlers of web requests

from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import SQLAlchemy
from app import app, db, lm
from .forms import LoginForm
from .models import User



@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    posts = [
        { 
            'author': {'nickname': 'John'}, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': {'nickname': 'Susan'}, 
            'body': 'The Avengers movie was so cool!' 
        }
    ]
    return render_template('index.html',
                           title='Home',
                           user=user,
                           posts=posts)
                           
# *************** Register Function *************************************

@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User(request.form['username'] , request.form['password'],request.form['email'])
    db.session.add(user)
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))

                           
# *************** Login Views and Functions *****************************                        

@app.before_request
def before_request():
    g.user = current_user
            
@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():  # Here the user is already logged in
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():  # Calling form.validate_on_submit() when the form is being presented to the user it will return False, so you know that you have to render the template. 
                                   # When validate_on_submit() is called as part of a form submission request, it will run all the validators attached to fields and check if the data is valid and can be processed.
        user = User.query.filter_by(username=form.username.data,password=form.password.data).first()
        if user is None:
            flash('Invalid login. Please try again.')
            return redirect(url_for('login'))
        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)
        login_user(user, remember = remember_me)
        
        flash('Logged in successfully.')
        return redirect(url_for('index'))
    return render_template('login.html', 
                           title='Sign In',
                           form=form,)
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    
    
# ************ User profile page *****************************

@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html',
                           user=user,
                           posts=posts)

