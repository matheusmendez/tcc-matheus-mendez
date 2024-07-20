from app import app
from flask import render_template, request, redirect, session, flash, url_for

from helpers import FormUser
from flask_bcrypt import check_password_hash
from datetime import datetime


@app.route('/login')
def login():
    next = request.args.get('next')
    form = FormUser()
    return render_template('login.html', next=next, form=form, title='')


@app.route(
    '/authenticate',
    methods=[
        'POST',
    ],
)
def authenticate():
    form = FormUser(request.form)
    user = form.userid.data
    password = form.password.data

    if user == 'admin' and password == 'admin':
        session['user_logged'] = user
        flash(user + ' logado com sucesso!')
        next_page = request.form['next']
        return redirect(next_page)
    else:
        flash('Usuário não logado.')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session['user_logged'] = None
    flash('Logout successful!')
    return redirect(url_for('devices'))
