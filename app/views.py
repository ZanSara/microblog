# Handlers of web requests

from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import SQLAlchemy
from app import app, db, lm
from .forms import LoginForm, EditProfileForm
from .models import User
from datetime import datetime



@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    posts = [
        { 
            'author': {'username': 'John'}, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': {'username': 'Susan'}, 
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
    username = User.unique_username(request.form['username'])
    if username != request.form['username']:
        flash('Esiste già un utente con questo nome! Puoi provare {0}'.format(username))
        return redirect(url_for('register'))
    if not User.unique_email(request.form['email']):
        flash("Esiste già un account collegato all'indirizzo {0}.".format(request.form['email']))
        return redirect(url_for('register'))
    user = User(username, request.form['password'], request.form['email'])
    db.session.add(user)
    db.session.add(user.follow(user)) # Makes every user followers of himself
    db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))

                           
# *************** Login Views and Functions *****************************                        

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
            
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

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html',
                           user=user,
                           posts=posts)
                           
@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditProfileForm(g.user.username)
    if form.validate_on_submit():
        g.user.username = form.username.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.username.data = g.user.username
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)
    
    
# ********** Followers Functions ************************

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Utente %s non trovato.' % username)
        return redirect(url_for('index'))
    if user == g.user:
        flash('Ogni utente segue sé stesso di default.')
        return redirect(url_for('user', username=username))
    u = g.user.follow(user)
    if u is None:
        flash('Non puoi seguire ' + username + '. Forse lo segui già?')
        return redirect(url_for('user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('Ora segui ' + username + '!')
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Utente %s non trovato.' % username)
        return redirect(url_for('index'))
    if user == g.user:
        flash('Impossibile smettere di seguire sé stessi.')
        return redirect(url_for('user', username=username))
    u = g.user.unfollow(user)
    if u is None:
        flash('Non puoi smettere di seguire ' + username + '. Riprova più tardi.')
        return redirect(url_for('user', username=username))
    db.session.add(u)
    db.session.commit()
    flash('Hai smesso di seguire ' + username + '.')
    return redirect(url_for('user', username=username))
    
    
    
    
    
    
    
    
    
# ********** Error Handlers *****************************
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback() # Just in case this 500 was triggered by a database exception
    return render_template('500.html'), 500

