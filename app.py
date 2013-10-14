#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import hashlib
import urlparse
import datetime
import random
import mandrill
from flask import Flask, render_template, request, flash, session, url_for, redirect, escape
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY

urlparse.uses_netloc.append("postgres")
dburl = urlparse.urlparse(os.environ["DATABASE_URL"])
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'public'),
            static_url_path='/public')
app.config['SQLALCHEMY_DATABASE_URI'] = ''.join((
    'postgresql+psycopg2://',
    dburl.username, ':', dburl.password,
    '@', dburl.hostname, ':', str(dburl.port),
    '/', dburl.path[1:]))
CSRF_ENABLED = True
app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]
try:
    MANDRILL = mandrill.Mandrill(os.environ['MANDRILL_APIKEY'])
except KeyError:
    print('Mandrill unavailable')
db = SQLAlchemy(app)


@app.template_filter('nl')
def nlfilter(s):
    return '<p>' + unicode(escape(s)).replace('\n\n', '</p><p>') + '</p>'

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
    languages = db.Column(ARRAY(db.Integer))

    def __init__(self, title, url, author, description, email, publishemail, languages, sourcelink = None, date = None, visible = False):
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
        self.languages = languages

    def __repr__(self):
        return '<Page %r>' % self.title

    def languages_names(self):
        q = self.languages
        if q is None:
            return []
        names = []
        for i in q:
            _ = Language.query.filter(Language.id == i)
            names += [i.name for i in _]
        return names

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

class Language(db.Model):
    id = db.Column(db.Integer, db.Sequence('language_id_seq'), primary_key=True, unique=True)
    name = db.Column(db.String(512), unique=True)
    icon = db.Column(db.String(8))

    def __init__(self, name, icon):
        self.name = name
        self.icon = icon

    def __repr__(self):
        return '<Language %r (%r)>' % (self.name, self.icon)


class LanguageFetcher(object):
    """A language fetcher."""

    def __init__(self):
        self.llist = Language.query.all()
        _ = [i.name for i in self.llist]
        self.names = ['English'] + sorted(_[1:])
        self.ids = {i.name: i.id for i in self.llist}
        self.icons = {i.id: i.icon for i in self.llist}

LF = LanguageFetcher()

@app.route('/')
def index():
    data = Page.query.filter_by(visible=True).all()
    random.shuffle(data)

    return render_template('index.html', data=data, icons=LF.icons, len=len)


@app.route('/tos/')
def tos():
    return render_template('tos.html')

@app.route('/add/', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        f = request.form
        langs = [LF.ids[i] for i in f.getlist('languages')]
        if 'tos' not in f:
            return render_template('add-error.html', error='tos')
        elif not f['title'] or not f['author'] or not f['email'] or not f['url'] or not langs:
            return render_template('add-error.html', error='empty')
        try:
            if 'visible' in f and 'username' in session:
                visible = True
            else:
                visible = False

            p = Page(f['title'], f['url'], f['author'], f['description'],
                     f['email'], 'publishemail' in f, langs,
                     sourcelink = f['sourcelink'], visible = visible)
            db.session.add(p)
            db.session.commit()
        except:
            return render_template('add-error.html', error='general')
        if 'username' not in session:
            mail_admin(p)
        return render_template('add-ack.html', p=p)
    else:
        return render_template('add-edit.html', data=None, langs=LF.names)

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
    if 'username' not in session:
        return render_template('accessdenied.html')
    data = list(Page.query.order_by(Page.visible == True, Page.date))
    return render_template('acp/index.html', data=data, icons=LF.icons)

@app.route('/acp/<slug>/', methods=['POST'])
def admin_act(slug):
    if 'username' not in session:
        return render_template('accessdenied.html')
    page = Page.query.filter_by(id=int(slug)).first()
    if 'toggle' in request.form:
        page.visible = not page.visible
        db.session.add(page)
        db.session.commit()
        return redirect('/acp/', 302)
    elif 'edit' in request.form:
        if request.form['edit'] == '1':
            f = request.form
            langs = [LF.ids[i] for i in f.getlist('languages')]
            page.title = f['title']
            page.url = f['url']
            page.author = f['author']
            page.description = f['description']
            page.email = f['email']
            page.sourcelink = f['sourcelink'] if f['sourcelink'] else None
            page.languages = langs
            page.publishemail = 'publishemail' in f
            page.visible = 'visible' in f
            db.session.add(page)
            db.session.commit()
            return redirect('/acp/', 302)
        else:
            return render_template('add-edit.html', data=page, langs=LF.names, langids=LF.ids)
    elif 'delete' in request.form:
        return render_template('acp/delete.html', page=page)
    elif 'del' in request.form:
        if request.form['del'] == '1':
            db.session.delete(page)
            db.session.commit()
        return redirect('/acp/', 302)

@app.route('/login/passwd/change/', methods=['GET', 'POST'])
def admin_change_passwd():
    if 'username' not in session:
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
    if 'username' not in session:
        return render_template('accessdenied.html')
    data = Admin.query.all()
    return render_template('acp/users.html', data=data)

@app.route('/users/<id>/', methods=['POST'])
def admin_user_edit(id):
    if 'username' not in session:
        return render_template('accessdenied.html')
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


def mail_admin(page):
    msg = """Hello there,
a request was sent to add a page to the Some Sites Using Nikola listing.

Title: {title}
URL: {url}
Author: {author} <{email}>

You can accept or deny this request at the Management page:
    <{mgmt}>

{sig}
Some Sites Using Nikola at {ssun}
""".format(title=page.title, url=page.url, author=page.author,
           email=page.email, mgmt=url_for('admin_panel', _external=True),
           sig='-- ', ssun=url_for('index', _external=True))

    message = {'text': msg, 'from_email': 'users@getnikola.com', 'from_name':
               'Some Sites Using Nikola ({0})'.format(page.author), 'to':
               [{'email': 'info@getnikola.com', 'name': 'Nikola'}],
               'auto_html': False, 'subject':
               '[Some Sites Using Nikola] Addition Request'}
    return MANDRILL.messages.send(message=message, async=False, ip_pool='Main Pool')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=bool(os.environ["DEBUG"]))
