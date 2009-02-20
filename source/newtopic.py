#!/usr/bin/env python

import string
import os

import ConvDB
import web

from StandardVars import *

import themes
theme = themes.LoadTheme()


theme.PrintHeader('The Conversatron - New Topic')
theme.PrintNavBanner('New topic posted!')

try:
	askeraddr = os.environ['REMOTE_ADDR']
except:
	askeraddr = "Unknown"

try:	
	askerclient = os.environ['HTTP_USER_AGENT']
except:
	askerclient = "Unknown"

subject = string.strip(form.getvalue('subject', ''))
if not subject:
	theme.StartErrorBox("There was a problem with your topic")
	print '<font size="+1">Um, yeah. You need a subject.<br>Why don\'t we back up and try that again?</font>'
	theme.EndErrorBox()
	theme.PrintFooter()
	web.quit()

text = string.strip(form.getvalue('body', ''))
if not text:
	theme.StartErrorBox("There was a problem with your topic")
	print '<font size="+1">You didn\'t enter any text. Or it was just all spaces.<br>Why don\'t we back up and try that again?</font>'
	theme.EndErrorBox()
	theme.PrintFooter()
	web.quit()


asaskee = form.getvalue('asaskee')

if user.usertype > 1:

	if asaskee:
		shortname = form.getvalue('shortname')
		if shortname:
			askeeid = ConvDB.AskeeShortcutToID(shortname)
		else:
			askeeid = form.getvalue('askee')
		
		
		if askeeid == None:
			theme.StartErrorBox('Askee Not Found')
			print "It would appear that you didn't choose a valid Askee - back up and try again."
			theme.EndErrorBox()
			theme.PrintFooter()
			web.quit()

		emotion = form.getvalue('emotion', 'n')

if user.banned == 'n':
	if user.usertype < 2:
		text = text[:2048]
		text = web.SanitizeHTML(text)

	subject = subject[:32]
	if user.usertype < 2:
		subject = web.SanitizeHTML(subject)

	subject = web.StripNewlines(subject)

	askerclient = web.SanitizeHTML(askerclient)
	
	text = web.NewlinestoBR(text)

	thread = ConvDB.SuperHash()
	thread.subject = subject
	thread.user = user.id
	thread.count = 1
	thread.whenis = ConvDB.DatetimeSQL()
	
	if user.usertype == 0:
		thread.theme = themes.GetCurrentThemeName()
	else:		
		if themes._overridepost and not (user.themeoverride=='y'):
			thread.theme = theme._name
		else:
			thread.theme = themes.GetCurrentThemeName()
	
	db.storeObject('thread', thread)
	cur = db.execute("select last_insert_id()")
	data = cur.fetchone()
	thread.id = data[0]

	entry = ConvDB.SuperHash()
	entry.thread = thread.id
	entry.asker = user.id
	if asaskee:
		entry.askee = askeeid
		entry.emotion = emotion
	else:
		entry.askee = 0
	entry.body = text
	entry.addr = askeraddr
	entry.Client = askerclient
	entry.whenis = ConvDB.DatetimeSQL()

	ConvDB.AddEntry(entry)

if user.usertype > 0:
	user.asked = user.asked + 1
	db.updateObject('user', user, 'id='+str(user.id))

#theme.StartUserBox('Yay!')
#print "Your topic has been posted. If we like it, it will appear on the topics list shortly.<br><br>"
#print "Please have some patience, and remember, not all responses will appear at once.<br><br>"
#print '<a href="' + web.HomePage() + '">Back to the main page</a>'
#theme.EndUserBox()

theme.StartUserBox('<blink>PROCESSING</blink>')
print """
<img src="/askees/wopr1.jpg" align=left hspace=5> <tt>launching new combinator interpreter instance...</tt>
"""
print '<br><a href="' + web.HomePage() + '">Back to the main page</a>'


theme.EndUserBox()

theme.PrintFooter()
