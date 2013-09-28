#!/usr/bin/env python

import app
import sys

print('[{0}] {1}'.format(sys.argv[2], sys.argv[1]))
app.db.session.add(app.Language(sys.argv[1], sys.argv[2]))
try:
    app.db.session.commit()
except:
    raise
else:
    print('OK')
