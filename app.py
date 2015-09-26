#!/usr/bin/env python
# -*- coding: utf-8 -*-


import newrelic.agent
newrelic.agent.initialize('/srv/nikola-users/newrelic.ini')

import os
import json
import urlparse
import datetime
import random
import mandrill
import requests
from flask import Flask, render_template, request, abort, session, url_for, redirect, escape
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import exc as sqlexc
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

ADMIN_LIST = ['kwpolska@gmail.com',
              'ralsina@kde.org',
              'ralsina@netmanagers.com.ar',
              'info@oquanta.info',
              'daniel@daniel.priv.no']

db = SQLAlchemy(app)


@app.template_filter('nl')
def nlfilter(s):
    return '<p>' + unicode(escape(s)).replace('\n\n', '</p><p>') + '</p>'

def addslash(u):
    return u if u.endswith('/') else u + '/'

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
        self.sourcelink = sourcelink if sourcelink else None
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

    return render_template('index.html', data=data, icons=LF.icons, len=len, header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())


@app.route('/tos/')
def tos():
    return render_template('tos.html', header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())

# Copied from:
# http://flask.pocoo.org/docs/patterns/streaming/#streaming-from-templates
def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(2) # would break our thing if we had more here
    return rv

@app.route('/check/', methods=['GET', 'POST'])
def checksite():
    if request.method == 'POST':
        def checkgenerator(f):
            homeurl = f['url']
            yield '<p>Checking site: <strong>{0}</strong>.</p>'.format(homeurl)
            burl = homeurl.split('index.html')[0]
            if not burl.endswith('/'):
                burl += '/'
            if homeurl != burl:
                yield '<p>Base determined as <strong>{0}</strong>.</p>'.format(
                    burl)
            rssurl = burl + 'rss.xml'
            success = """
            <p class="text-success">
            <i class="fa fa-check" style="font-size: 2em;"></i>
            This is a Nikola site.</p>"""

            failed = """
            <p class="text-danger">
            <i class="fa fa-times" style="font-size: 2em;"></i>
            This is not a Nikola site.</p>"""

            unknown = """
            <p class="text-warning">
            <i class="fa fa-warning" style="font-size: 2em;"></i>
            The check has failed.  {0}</p>"""
            try:
                r = requests.get(rssurl)
                nsite = False
                patterns = ['<generator>https://getnikola.com/</generator>',         # v7.6.1
                            '<generator>http://getnikola.com/</generator>',          # v7.0.0
                            '<generator>Nikola <http://getnikola.com/></generator>', # v6.3.0
                            '<generator>nikola</generator>']                         # v6.2.1
                for i in patterns:
                    if i in r.content:
                        nsite = True

                if nsite:
                    yield success
                elif r.status_code not in [200, 404]:
                    yield unknown.format('HTTP {0} received.'.format(
                        r.status_code))  # formatception!
                else:
                    yield failed
            except Exception as e:
                yield unknown.format('An unhandled exception occurred: ' + str(e))

        return render_template('checkresult.html', data=checkgenerator(request.form))

        #return Response(stream_template('checkresult.html',
                                        #data=list(checkgenerator(request.form)))
    else:
        return render_template('checksite.html')

@app.route('/add/', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        f = request.form
        langs = [LF.ids[i] for i in f.getlist('languages')]
        if 'tos' not in f:
            return render_template('add-error.html', error='tos', header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())
        elif not f['title'] or not f['author'] or not f['email'] or not f['url'] or not langs:
            return render_template('add-error.html', error='empty', header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())
        try:
            if 'visible' in f and 'username' in session:
                visible = True
            else:
                visible = False

            p = Page(f['title'], addslash(f['url']), f['author'], f['description'],
                     f['email'], 'publishemail' in f, langs,
                     sourcelink = f['sourcelink'], visible = visible)
            db.session.add(p)
            db.session.commit()
        except:
            return render_template('add-error.html', error='general', header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())
        if not session.get('is_admin'):
            mail_admin(p)
        return render_template('add-ack.html', p=p, header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())
    else:
        return render_template('add-edit.html', data=None, langs=LF.names, header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())

@app.route('/edit/')
def edit():
    return render_template('edit-remove.html', action='edit', header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())

@app.route('/remove/')
def remove():
    return render_template('edit-remove.html', action='remove', header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())

@app.route('/login/', methods=['GET', 'POST'])
def login():
    # remove leftover stuff
    if 'username' in session:
        session.pop('username')

    if request.method == 'POST':
        if 'assertion' not in request.form:
            abort(400)

        assertion_info = {'assertion': request.form['assertion'],
                          'audience': 'users.getnikola.com'} # window.location.host
        resp = requests.post('https://verifier.login.persona.org/verify',
                            data=assertion_info, verify=True)

        if not resp.ok:
            print(resp)
            print(resp.content)
            abort(500)

        data = resp.json()

        if data['status'] == 'okay':
            session.update({'email': data['email']})
            data['is_admin'] = data['email'] in ADMIN_LIST
            session['is_admin'] = data['is_admin']
            # TODO -- we should allow non-admins and let them do some things.
            if not session['is_admin']:
                session.pop('email')
                session.pop('is_admin')
                data['status'] = 'failure'
                data['reason'] = 'Not an admin.'
            return json.dumps(data)
    else:
        if 'email' in session:
            return redirect('/', 302)
        else:
            return render_template('login.html', header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())

@app.route('/logout/', methods=["POST"])
def logout():
    try:
        session.pop('email')
    except KeyError:
        pass
    try:
        session.pop('is_admin')
    except KeyError:
        pass
    return redirect('/', 302)

@app.route('/acp/')
def admin_panel():
    if not session.get('is_admin'):
        return render_template('accessdenied.html', header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())
    data = list(Page.query.order_by(Page.visible == True, Page.date))
    return render_template('acp/index.html', data=data, icons=LF.icons, header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())

@app.route('/acp/<slug>/', methods=['POST'])
def admin_act(slug):
    if not session.get('is_admin'):
        return render_template('accessdenied.html', header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())
    page = Page.query.filter_by(id=int(slug)).first()
    if 'toggle' in request.form:
        page.visible = not page.visible
        db.session.add(page)
        db.session.commit()
        return redirect('/acp/', 302)
    elif 'edit' in request.form:
        if request.form['edit'] == '1':
            try:
                f = request.form
                langs = [LF.ids[i] for i in f.getlist('languages')]
                page.title = f['title']
                page.url = addslash(f['url'])
                page.author = f['author']
                page.description = f['description']
                page.email = f['email']
                page.sourcelink = f['sourcelink'] if f['sourcelink'] else None
                page.languages = langs
                page.publishemail = 'publishemail' in f
                page.visible = 'visible' in f
                db.session.add(page)
                db.session.commit()
            except sqlexc.IntegrityError:
                return render_template('add-error.html', error='general', langs=LF.names, langids=LF.ids, header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())
            return redirect('/acp/', 302)
        else:
            return render_template('add-edit.html', data=page, langs=LF.names, langids=LF.ids, header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())
    elif 'delete' in request.form:
        return render_template('acp/delete.html', page=page, header=newrelic.agent.get_browser_timing_header(), footer=newrelic.agent.get_browser_timing_footer())
    elif 'del' in request.form:
        if request.form['del'] == '1':
            db.session.delete(page)
            db.session.commit()
        return redirect('/acp/', 302)


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

    message = {'text': msg, 'from_email': 'request@getnikola.com', 'from_name':
               'Some Sites Using Nikola ({0})'.format(page.author), 'to':
               [{'email': 'users@getnikola.com', 'name': 'Nikola'}],
               'auto_html': False, 'subject':
               '[Some Sites Using Nikola] Addition Request'}
    return MANDRILL.messages.send(message=message, async=False, ip_pool='Main Pool')

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=bool(os.environ["DEBUG"]))
