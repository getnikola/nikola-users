#!/usr/bin/env python

import os
import hashlib
import urlparse
from flask import Flask, render_template, request, flash, session, redirect
from flask.ext.sqlalchemy import SQLAlchemy

urlparse.uses_netloc.append("postgres")
dburl = urlparse.urlparse(os.environ["DATABASE_URL"])
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ''.join((
    'postgresql+psycopg2://',
    dburl.username, ':', dburl.password,
    '@', dburl.hostname, ':', str(dburl.port),
    '/', dburl.path[1:]))
app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]
db = SQLAlchemy(app)

class Page(db.Model):
    id = db.Column(db.Integer, db.Sequence('page_id_seq'), primary_key=True,
                   unique=True)
    title = db.Column(db.String(80))
    url = db.Column(db.String(512), unique=True)
    author = db.Column(db.String(80))
    description = db.Column(db.String(512))
    sourcelink = db.Column(db.String(512), nullable=True)
    date = db.Column(db.DateTime)
    visible = db.Column(db.Boolean)
    email = db.Column(db.String(512))

    def __init__(self, title, url, author, description, sourcelink, date, visible, email):
        self.title = title
        self.url = url
        self.author = author
        self.description = description
        self.sourcelink = sourcelink
        self.date = date
        self.visible = visible
        self.email = email

    def __repr__(self):
        return '<Page %r>' % self.title

class Admin(db.Model):
    id = db.Column(db.Integer, db.Sequence('admin_id_seq'), primary_key=True, unique=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(512), unique=True)
    password = db.Column(db.String(128))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = Admin.mkpwd(password)

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def mkpwd(password):
        return hashlib.sha512(password.encode()).hexdigest()

@app.route('/')
def index():
    data = (
        ('site name', 'http://google.com', 'author', 'desc', 'sourcelink'),
        ('another', 'http://example.com', 'authorette', 'ription', None),
        ('we', 'need', 'even', 'more', '!'),
        ('we', 'need', 'even', 'more', '!'),
        ('we', 'need', 'even', 'more', '!'),
        ('we', 'need', 'even', 'more', '!'),
    )
    return render_template('index.html', data=data)

@app.route('/add/', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # Temporary.
        return render_template('error.html')
    else:
        return render_template('add.html')

@app.route('/edit/')
def edit():
    return render_template('edit-remove.html', action='edit')

@app.route('/remove/')
def remove():
    return render_template('edit-remove.html', action='remove')

@app.route('/login/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['act'] == 'in':
            u = Admin.query.filter(Admin.username.ilike(
                request.form['username'])).first()
            if not u or Admin.mkpwd(request.form['password']) != u.password:
                flash('Login failed.', category='error')
                return render_template('login.html')
            else:
                session['username'] = u.username
                flash('Logged in!')
        else:
            session.pop('username')
            flash('Goodbye.')
        return redirect('/', 302)
    else:
        if 'username' in session:
            return redirect('/', 302)
        else:
            return render_template('login.html')

@app.route('/login/out/')
def admin_logout():
    session.pop('username')
    flash('Goodbye.')
    return redirect('/', 302)

@app.route('/acp/')
def admin_panel():
    return render_template('acp.html')

@app.route('/login/passwd/change/', methods=['GET', 'POST'])
def admin_change_passwd():
    if not session['username']:
        return render_template('accessdenied.html')

    if request.method == 'POST':
        if request.form['password'] == request.form['confirm']:
            u = Admin.query.filter(Admin.username.ilike(
                session['username'])).first()

            u.password = Admin.mkpwd(request.form['password'])
            db.session.add(u)
            db.session.commit()
            session.pop('username')
            flash('Your password has been changed.  For safety reasons, you need to log back in.')
            return redirect('/login/', 302)
        else:
            flash('The passwords do not match.', category='error')
            return render_template('changepasswd.html')

    else:
        return render_template('changepasswd.html')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=bool(os.environ["DEBUG"]))
