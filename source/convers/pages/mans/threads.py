#!/usr/bin/env python

#New thread manager

import sys; sys.path.insert(0,"..")
import os

import ConvDB
import web

from StandardVars import *

import themes

def topic_link(item):
	return '<a href="/convers.py?topic=%(id)s">%(subject)s</a>' % item

def HandleList():
	"In the normal case, just list all threads."
	
	theme.PrintHeader('The Conversatron - Thread manager')
	theme.PrintNavBanner('Thread Manager')
	
	theme.StartUserBox("Current Pending Threads", "")
	
	if op == "user":
		threads = ConvDB.GetNewThreadList('user')
		tablehead = '<table><tr><td><a href="threadman.py?op=subject">Subject</a></td><td><b>User</b></td><td><a href="threadman.py">Time</a></td><td>&nbsp;</td><td>&nbsp;</td></tr>'
	elif op == "subject":
		threads = ConvDB.GetNewThreadList('subject')
		tablehead = '<table><tr><td><b>Subject</b></td><td><a href="threadman.py?op=user">User</a></td><td><a href="threadman.py">Time</a></td><td>&nbsp;</td><td>&nbsp;</td></tr>'
	else:
		threads = ConvDB.GetNewThreadList()
		tablehead = '<table><tr><td><a href="threadman.py?op=subject">Subject</a></td><td><a href="threadman.py?op=user">User</a></td><td><b>Time</b></td><td>&nbsp;</td><td>&nbsp;</td></tr>'
		
	if threads != None:
		if len(threads):
		
			print tablehead
			for item in threads:
				print '<tr><td>%s</td>' % topic_link(item) #<a href="convers.py?topic=' + str(item.id) + '">'+str(item.subject)+'</a></td>'
				print '<td>'+str(item.name)+'</td><td>'+ str(item.whenis)+'</td>'
				print '<td><a href="threadman.py?op=delete&id='+str(item.id)+'&oldop='+op+'">[Delete]</a></td>'
				print '<td><a href="threadman.py?op=delfromhere&id='+str(item.id)+'">[Delete older]</a></td></tr>'
			print '</table>'
			
			print '<br><br><a href="threadman.py?op=deleteall">Delete ALL of them</a><br>'
			
			
		else:
			print '<font size="+2">Lucky you, no threads to contend with.</font>'
			
	theme.EndUserBox()
	theme.PrintFooter()


def HandleListDel():
	"List all deleted threads."
	
	theme.PrintHeader('The Conversatron - Thread manager')
	theme.PrintNavBanner('Thread Manager')
	
	theme.StartUserBox("Trashcan contents:", "80%")
	
	threads = ConvDB.GetDeletedThreadList()

	if threads != None:
		if len(threads):
		
			print '<table><tr><td>Subject</td><td>User</td><td><b>Time</b></td><td>&nbsp;</td></tr>'
			for item in threads:
				print '<tr><td><a href="convers.py?topic=' + str(item.id) + '">'+str(item.subject)+'</a></td>'
				print '<td>'+str(item.name)+'</td><td>'+ str(item.whenis)+'</td>'
				print '<td><a href="threadman.py?op=undelete&id='+str(item.id)+'&oldop='+op+'">[Undelete]</a></td></tr>'
			print '</table>'			
			
			print '<br><br><a href="threadman.py?op=empty">Empty Trash, FOREVER!</a> - <blink>*</blink>Warning, no confirmation!<br>'
			
		else:
			print '<font size="+2">Trashcan is empty.</font>'
			
	theme.EndUserBox()
	theme.PrintFooter()


def HandleDelete():
	"Delete the sucker!"
	try:
		id = int(form["id"].value)
		db.execute("update thread set deleted='y' where id=%i" % (id))
	except:
		pass
	
	try:
		oldop = form["oldop"].value
	except:
		oldop = 'chrono'
		
	web.RedirectToSelf('op='+oldop)


def HandleUndelete():
	"Delete the sucker!"
	try:
		id = int(form["id"].value)
		db.execute("update thread set deleted='n' where id=%i" % (id))
	except:
		pass
	
	try:
		oldop = form["oldop"].value
	except:
		oldop = 'chrono'
		
	web.RedirectInFolder('/threadman.py?op='+oldop)


def HandleDeleteAll():
	"Clear ALL unasnwered threads. Use with discression."
	
	cur = db.execute("select id from thread where active='n'")
	list = cur.fetchall()
	for item in list:
		db.execute("update thread set deleted='y' where id=%i" % (item[0]))
			
	web.GoHome()


def HandleDeleteOlder():
	"Delete all this id and all less than it."
	
	try:
		id = int(form["id"].value)
	except:
		web.RedirectInFolder('/threadman.py')
	
	cur = db.execute("select id from thread where active='n' and id<="+str(id))
	list = cur.fetchall()
	for item in list:
		db.execute("update thread set deleted='y' where id=%i" % (item[0]))
	
	web.RedirectInFolder('/threadman.py')


def HandleEmptyTrash():
	"Empty the trash. Permanently!"
	
	cur = db.execute("select id from thread where deleted='y'")
	list = cur.fetchall()
	for item in list:
		db.execute("delete from thread where id = %i" % (item[0]))
		db.execute("delete from entry where thread=%i" % (item[0]))
		db.execute("delete from rating where thread=%i" % (item[0]))
	
	web.GoHome()

# ------- begin ----------
if not user.IsWriter(): web.GoHome()

theme = themes.LoadTheme()

op = form.getvalue("op", "chrono")

if op == "chrono" or op == "user" or op == "subject":
	HandleList()
elif op == "delete":
	HandleDelete()
elif op == "delfromhere":
	HandleDeleteOlder()
elif op == "undelete":
	HandleUndelete()
elif op == "deleteall":
	HandleDeleteAll()
elif op == "listdel":
	HandleListDel()
elif op == "empty":
	HandleEmptyTrash()	

