from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from flask_pymongo import PyMongo
from . forms import LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
from app import app


app.config['MONGO_URI']="mongodb://localhost:27017/stevenDB"

mongo = PyMongo(app)

key = b'\xd4\x87\\\x0eJ\x80\x9em=\r\x91d\x9b\xe3c'

@app.route('/')
def index():
    if not session.get('username'):
        flash('You are not authenticated')
        return redirect(url_for('login'))
    else:
        return render_template('index.html')


@app.route('/cabinet')
def cabinet():
    if session['username']:
        return render_template('cabinet.html')
    else:
        flash('You are not authenticated')
    return redirect(url_for('login'))


@app.route('/images/<path:filename>')
def imgFile(filename):
    if session['username']:
        return send_from_directory('/static/images', filename)
    else:
        flash('You are not authenticated')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if session['username']:
            return  redirect(url_for('index'))
    except Exception:
        pass
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = form.username.data
        password = form.password.data
        login_user = mongo.db.users.find_one({'username':user})
        if login_user is None or not check_password_hash(login_user['password'], password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        session['username'] = True
        return redirect(url_for('index'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = form.username.data
        password = generate_password_hash(form.password.data)
        mongo.db.users.insert({'username':user, 'password':password})
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    else:
        flash('Wrong')
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    session.clear()
    session['username'] = False
    return redirect(url_for('login'))
