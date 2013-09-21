#!python

import app
import sys
from sqlalchemy.schema import CreateSequence, DropSequence, Sequence

if sys.version_info[0] == 2:
    input = raw_input

#username = input('Admin username: ')
#email = input('Admin email: ')
password = 'admin'

username = 'Kwpolska'
email = 'kwpolska@gmail.com'

print('Purging existing data...')

app.db.drop_all()

#try:
    #DropSequence(Sequence('admin_id_seq'), bind=app.db.session).execute()
#except:
    #app.db.session.rollback()
#try:
    #DropSequence(Sequence('page_id_seq'), bind=app.db.session).execute()
#except:
    #app.db.session.rollback()

print('Done.')

print('Creating tables...')

app.db.create_all()

print('Done.')

print('Creating sequences...')

try:
    CreateSequence(Sequence('admin_id_seq'), bind=app.db.session).execute()
except:
    app.db.session.rollback()

try:
    CreateSequence(Sequence('page_id_seq'), bind=app.db.session).execute()
except:
    app.db.session.rollback()

print('Done.')

print('Creating user: {0} with password {1} and email {2}...'.format(
      username, password, email))

admin = app.Admin(username, email, password)
app.db.session.add(admin)
app.db.session.commit()

print('Done.')
