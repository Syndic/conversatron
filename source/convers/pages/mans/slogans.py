#!/usr/bin/python

# Slogan Manager

import string
import urllib

import ConvDB

from StandardVars import *
import themes
import web


def HandleAddForm():
	"Print a new slogan form"
	
	theme.PrintHeader('The Conversatron - Slogan Manager')
	theme.PrintNavBanner('Slogan Manager')
	
	print '<form action="sloganman.py" method="post">'
	print '<input type="hidden" name="op" value="addit">'
	print '<table>'
	print '<tr><td align=right>Theme:</td><td><input name="theme" type="text" value="'+theme._name+'"></td></tr>'
	print '<tr><td align=right>Enter a new slogan, baby:</td><td><input name="slogan" type="text" size=70 maxlength=255></td></tr>'
	print '<tr><td></td><td><input type="submit" value="Add it"></td></tr>'
	print '</table>'
	print '</form>'
	
	ShowList()

	theme.PrintFooter()
	
def HandleAdd():	
	"Add a new slogan."
	
	try:
		newslogan = ConvDB.SuperHash()
		newslogan.slogan = form["slogan"].value
		newslogan.theme = form["theme"].value
		db.storeObject('slogan', newslogan)
	except:
		pass
		
	web.RedirectInFolder('/sloganman.py')
	
	
def ShowList():
	"Print a list of all slogans."
	
	viewlist = form.getvalue('list')
	
	if not viewlist:	
		print '<a href="sloganman.py?list=true">List all the suckers</a>'
	else:
		list = db.loadObjects('select * from slogan order by theme')
		
		currtheme = ""
		for item in list:
			if item.theme != currtheme:
				currtheme = item.theme
				print '<br><b>'+currtheme+'</b><br><br>'
			print item.slogan + ' <a href="sloganman.py?op=edit&id='+str(item.id)+'">[edit]</a><br>'



def HandleEditForm():
	"Bring up the edit slogan form"
	
	try:
		id = int(form["id"].value)
		slogan = db.loadObject('select * from slogan where id='+str(id))
	except:
		web.RedirectInFolder('/sloganman.py')
		web.quit()
		
	theme.PrintHeader('The Conversatron - Slogan Manager')
	theme.PrintNavBanner('Slogan Manager')
	
	slogtext = string.replace(str(slogan.slogan), '"', '&quot;')

	print '<form action="sloganman.py" method="post">'
	print '<input type="hidden" name="op" value="editit">'
	print '<input type="hidden" name="id" value="'+str(slogan.id)+'">'
	print 'Edit the sucker: <input name="slogan" type="text" size=70 maxlength=255 value="'+slogtext+'"> '
	print 'Theme: <input name="theme" type="text" value="'+slogan.theme+'">'
	print '<input type="submit" value="Edit it"><br>'

	theme.PrintFooter()


def HandleEdit():
	"Edit a slogan."
	
	try:
		slogan = ConvDB.SuperHash()
		slogan.slogan = form["slogan"].value
		slogan.theme = form["theme"].value
		
		db.updateObject('slogan', slogan, 'id='+str(form["id"].value))
	except:
		pass
		
	web.RedirectInFolder('/sloganman.py?op=list')

# ------- begin ----------
theme = themes.LoadTheme()

if user.usertype < 3:
	web.GoHome()

op = form.getvalue('op', 'add')


if op == "add":
	HandleAddForm()
elif op == "addit":
	HandleAdd()
elif op == "edit":
	HandleEditForm()
elif op == "editit":
	HandleEdit()
else:
	web.GoHome()
