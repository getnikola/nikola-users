#!/usr/bin/env python

import os
import hashlib
import urlparse
import datetime
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
    publishemail = db.Column(db.Boolean)

    def __init__(self, title, url, author, description, email, publishemail, sourcelink = None, date = None, visible = False):
        self.title = title
        self.url = url
        self.author = author
        self.description = description
        self.sourcelink = sourcelink
        if date is None:
            self.date = datetime.datetime.now()
        else:
            self.date = date
        self.visible = visible
        self.email = email
        self.publishemail = publishemail

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
        return '<Admin %r>' % self.username

    @staticmethod
    def mkpwd(password):
        return hashlib.sha512(password.encode()).hexdigest()

@app.route('/')
def index():
    data = list(Page.query.filter_by(visible=True).order_by(Page.date))
    return render_template('index.html', data=data)

@app.route('/add/', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        f = request.form
        if 'tos' not in f:
            return render_template('add-error.html', error='tos')
        try:
            p = Page(f['title'], f['url'], f['author'], f['description'], f['email'], 'publishemail' in f, sourcelink = f['sourcelink'])
            db.session.add(p)
            db.session.commit()
        except:
            return render_template('add-error.html', error='general')
        return render_template('add-ack.html', p=p)
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
    data = list(Page.query.order_by(Page.visible == True, Page.date))
    return render_template('acp/index.html', data=data)

@app.route('/acp/<slug>/', methods=['POST'])
def admin_act(slug):
    page = Page.query.filter_by(id=int(slug)).first()
    if 'toggle' in request.form:
        page.visible = not page.visible
        db.session.add(page)
        db.session.commit()
        return redirect('/acp/', 302)
    elif 'edit' in request.form:
        if request.form['edit'] == '1':
            f = request.form
            page.title = f['title']
            page.url = f['url']
            page.author = f['author']
            page.description = f['description']
            page.email = f['email']
            page.sourcelink = f['sourcelink']
            page.publishemail = 'publishemail' in f
            page.visible = 'visible' in f
            db.session.add(page)
            db.session.commit()
            return redirect('/acp/', 302)
        else:
            return render_template('acp/edit.html', page=page)
    elif 'delete' in request.form:
        return render_template('acp/delete.html', page=page)
    elif 'del' in request.form:
        if request.form['del'] == '1':
            db.session.delete(page)
            db.session.commit()
        return redirect('/acp/', 302)

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

@app.route('/users/')
def admin_users():
    data = Admin.query.all()
    return render_template('acp/users.html', data=data)

@app.route('/users/<id>/', methods=['POST'])
def admin_user_edit(id):
    f = request.form
    if id == 'create':
        a = Admin(f['username'], f['email'], f['password'])
        db.session.add(a)
        db.session.commit()
    else:
        a = Admin.query.filter_by(id=int(id)).first()
        if 'del' in f:
            if f['del'] == '1':
                db.session.delete(a)
                db.session.commit()
        elif 'delete' in f:
            return render_template('acp/userdel.html', user=a)
        else:
            a.username = f['username']
            a.email = f['email']
            if f['password']:
                a.password = Admin.mkpwd(f['password'])

            db.session.add(a)
            db.session.commit()

    return redirect('/users/', 302)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=bool(os.environ["DEBUG"]))
