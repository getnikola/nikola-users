#!/usr/bin/env python

import app
import sys

app.db.session.add(app.Language(sys.argv[0], sys.argv[1]))
app.db.session.commit()
