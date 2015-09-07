# Handlers of web requests

from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import gettext
from app import app, db, lm
from .forms import LoginForm, EditProfileForm, PostForm
from .models import User, Post
from config import POSTS_PER_PAGE, LANGUAGES
from .emails import follower_notification
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(post)
        db.session.commit()
        flash(gettext('Your post is now live!'))
        return redirect(url_for('index'))  # Without the redirect, the last request is the POST request that submitted the form, so a refresh action will resubmit the form,
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html',
                           title='Home',
                           form=form,
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
    username = User.make_valid_username(username)
    if username != request.form['username']:
        flash('Username non valido: impossibile inserire i caratteri che non siano lettere, numeri, punti e underscore (_).'.format(username))
        return redirect(url_for('register'))
    if not User.unique_email(request.form['email']):
        flash("Esiste già un account collegato all'indirizzo {0}.".format(request.form['email']))
        return redirect(url_for('register'))
    user = User(username, request.form['password'], request.form['email'])
    db.session.add(user)
    db.session.add(user.follow(user)) # Makes every user followers of himself
    db.session.commit()
    flash('Registrazione completata con successo')
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
@app.route('/user/<username>/<int:page>')
@login_required
def user(username, page=1):
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('User %s not found.' % username)
        return redirect(url_for('index'))
    posts = user.sorted_posts().paginate(page, POSTS_PER_PAGE, False)
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
    follower_notification(user, g.user)
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
    

# Internationalization and Localization
#@babel.localeselector
#def get_locale():
#    return request.accept_languages.best_match(LANGUAGES.keys())  
    
    
    
# ********** Error Handlers *****************************
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback() # Just in case this 500 was triggered by a database exception
    return render_template('500.html'), 500

