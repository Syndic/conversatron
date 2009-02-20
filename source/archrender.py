#!/usr/bin/python

#Archive page renderer

import sys

import ConvDB
import themes


class boring:
	def ShowWriterStuff(self): pass


if len(sys.argv) == 1:
	sys.exit()

id = int(sys.argv[1])
currindex = int(sys.argv[2])

db = ConvDB.Init()

try:
	thread = db.loadObject("select * from thread where id="+str(id))
	if thread == None:
		raise Exception
except:
	print "Error: Couldn't load thread"
	sys.exit()
	
theme = themes.LoadTheme(thread.theme)


entries = ConvDB.GetThreadEntries(thread.id)

# Fake up a 'page' to hold the data
data = boring()
data.entries = entries
data.thread = thread

theme.PrintThread(data, currindex)
