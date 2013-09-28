#!/usr/bin/env python

import app
import sys

app.db.session.add(app.Language(sys.argv[1], sys.argv[2]))
app.db.session.commit()
