#!/usr/bin/env python

import sys

if len(sys.argv) != 3:
    print('USAGE: add-language.py English en')
    exit(-1)

import app

print('[{0}] {1}'.format(sys.argv[2], sys.argv[1]))
app.db.session.add(app.Language(sys.argv[1], sys.argv[2]))
try:
    app.db.session.commit()
except:
    raise
else:
    print('OK')
    print('Make sure to add the flag!')
    print('(If you already added one, run: `heroku ps:restart`)')
