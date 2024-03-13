from flask import Flask, render_template, redirect 
from .models import *

from flask import current_app as app

from flask import session, request, flash, url_for

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    if request.method=='POST':
        new_username = request.form['username']
        user = User.query.filter_by(username=new_username).first()
        if user and user.check_password(request.form['password']):
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    if request.method=='POST':
        new_username = request.form['username']
        user = User.query.filter_by(username=new_username).first() # user or none
        if user:
            flash('Username taken !! Please signup with some other username.')
            return redirect(url_for('signup'))
        
        new_user = User(username=new_username, password='')
        new_user.set_password(request.form['password'])
        db.session.add(new_user)
        db.session.commit()

        session['username'] = new_user.username
        return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None) # None here is the value that gets returned when the key 'username' does not exist in the session dictionary
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username = session['username'])

# flash, logout left