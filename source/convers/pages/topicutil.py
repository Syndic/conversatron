#!/usr/bin/env python
#Display a thread, man!
import os
from StandardVars import *
import ConvDB
import stars

from BasicPage import BasicPage
import themes
import web

import Thread

class Thing(object):pass

buff.contenttype = "text/plain"

op = form.getvalue('op')
if op == "newposts":
	entry = int(form.getvalue('oid'))
	topic = int(form.getvalue('topic'))
	entries = ConvDB.GetThreadEntries(topic, False, True, newerThan=entry)
		
	if len(entries):
		o = Thing()
		o.thread = Thread.Thread(topic)
		o.thread.entries = entries
		o.theme = themes.LoadTheme(o.thread.theme)
		o.theme.page = o
		o.theme.PrintThreadEntries()
		
		buff.headers["X-Ajax-Props"] = "{\"entry\": " + str(entries[-1].oid) + "}"
