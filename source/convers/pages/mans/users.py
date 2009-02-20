#!/usr/bin/python

#User manager. Yeah!

import urllib
import time
from Enum import Enum

import ConvDB

from StandardVars import *
import web
import themes

import words
from BasicPage import BasicPage

buttons = Enum(
	Search="search_button",
	Update="update_user",
	Delete="delete_user"
	)

level_names = {
	1:'Reader',
	2:'Writer',
	3:'Admin',
	4:'The Super'
	}

def ErrorUnknown(name):
	theme.ErrorPage(name, "User Unknown",
"""Whoops, that user doesn't seem to exist. Gah!<br><br>
<a href="users.py">Back to user manager</a>""")

def ErrorNoPriv(name):
	theme.ErrorPage(name, "Invalid Privileges",
"""You can't modify a user that has a greater or equal userlevel.<br><br>
<a href="users.py">Back to user manager</a>""")

class UserMan(BasicPage):
	def __init__(self):
		if not user.IsWriter():
			web.GoHome()

		BasicPage.__init__(self, name="User Manager", post_buttons=buttons)		

		if self.postButton in (buttons.Update,buttons.Delete):# UPDATE_BUTTON, DELETE_BUTTON):
			self.theUser = db.loadRow('user', form.getvalue('id'))
			
			if self.theUser is None:
				ErrorUnknown(self.name)

			if user.usertype <= self.theUser.usertype:
				ErrorNoPriv(self.name)

	def run(self):	
		if self.postButton == buttons.Search:
			HandleSearch()

		elif self.postButton == buttons.Update:
			self.HandleUpdate()
			web.RedirectToSelf('op=lookup&name=' + urllib.quote_plus(self.theUser.name))

		elif self.postButton == buttons.Delete:
			ConvDB.DeleteUser(self.theUser.id)
			web.RedirectToSelf('message='+urllib.quote("User '%s' deleted." % self.theUser.name))

		elif 'op' in form:
			self.HandleOp()
			
		else:
			MainView()

	def HandleUpdate(self):
		"Change a user's details."			
	
		# You need to be at least an admin to change user levels
		if user.IsAdmin():
			newtype = int(form.getvalue('usertype', self.theUser.usertype))
				
			# You can only change a level up to one minus your level
			newtype = min(newtype, user.usertype-1)
			
			# Shouldn't be able to change a user to guest level.
			newtype = max(1,newtype)
							
			self.theUser.usertype = newtype
	
		self.theUser.banned = "n"
		if "banned" in form:
			self.theUser.banned = "y"
	
		self.theUser.picture = form.getvalue("picture", "")		
		self.theUser.url = form.getvalue("url","")
		
		self.theUser._Update(db)


	def HandleOp(self):
		op = form.getvalue('op')
		cat = form.getvalue('type')
		
		if op == "lookup" or op == "change":
			if not user.IsWriter(): #user.usertype < 2:
				web.GoHome()
		else:
			if  not user.IsAdmin(): #user.usertype < 3:
				web.GoHome()
		
		if op == "search":
			self.HandleSearch()
			
		elif op == "list":
			HandleList(cat)
			
		elif op == "lookup":
			self.ShowUser()
			
		elif op == "change":
			self.HandleChange()
			
		elif op == "delete":
			self.HandleDelete()
			
		elif op == "zark":
			self.HandleZark()
			
		else:
			web.GoHome()

	def ShowUser(self):
		"Bring up a user's info."
		if 'name' not in form: web.RedirectToSelf()
		
		genders = {'n': 'None of your business', 'm': 'Male', 'f': 'Female', 't': 'Toilet Fixture'}
		usertypes = (('Reader',1), ('Writer',2), ('Administrator',3), ('The Super',4))
	
		theuser = db.loadObject('select *, TO_DAYS(now()) - TO_DAYS(created) as create_days, TO_DAYS(now()) - TO_DAYS(lastused) as lastused_days from user where name=%s', form.getvalue('name'))
		
		if theuser == None:
			theme.ErrorPage(self.name, "User Unknown",
	"""Whoops, that user doesn't seem to exist. Gah!<br><br>
	<a href="users.py">Back to user manager</a>""")
	
		theme.PrintHeader('The Conversatron - User manager')
		theme.PrintNavBanner('User Manager')
		
		if theuser.url == None: theuser.url = ''
		if theuser.lastip == None: theuser.lastip = ''
		
		if theuser.create_days is None: theuser.create_days = 0
		if theuser.lastused_days is None: theuser.lastused_days = 0
	
		createdDays = theuser.create_days % 365
		createdYears = theuser.create_days / 365
		
		lastusedDays = theuser.lastused_days % 365
		lastusedYears = theuser.lastused_days / 365
		
		IP = '<a href="resolve.py?addr='+urllib.quote_plus(theuser.lastip)+'" target="window">'+theuser.lastip+'</a>'
	
	
		print '<form method="post" action="users.py">'
		print '<input type="hidden" name="id" value="'+str(theuser.id)+'">'
		print '<br>'
		
		print '<table>'
		
		print '<tr><td></td><td><b>' + theuser.name + '</b></td></tr>'
	
		print '<tr><td align=right><b>Gender:</b></td><td>' + genders.get(theuser.gender, "??") + '</td></tr>'
	
		print '<tr><td align=right><b>User Type:</b></td><td>'
		web.HtmlSelect(usertypes, 'usertype', theuser.usertype)
		print "</td></tr>"
		
		checked = ''
		if theuser.banned == 'y':
			checked = 'checked'
		
		print '<tr><td align=right><b>Banned:</b></td><td><input name="banned" type="checkbox" %s></td></tr>' % (checked)
	
	
		# Picture
		print '<tr><td align=right><b>Picture:</b></td><td>'
		
		if theuser.picture == None or theuser.picture == "":
			print '<input name="picture" type="text" size=20>'
		else:
			print '<input name="picture" type="text" value="'+str(theuser.picture)+'" size=20></td></tr>'
			print '<tr><td></td><td><img src="/users/' + theuser.picture + '" width=80 height=100 >'
	
		print '</td></tr>'
		
		# URL
		print '<tr><td align=right><b>URL:</b></td><td><input name="url" type="text" value="' + theuser.url + '" size=40></td></tr>'
		
		# Change Button
		if user.usertype >= 3:
			print '<tr><td></td><td><input type="submit" name="update_user" value="Update User"></td></tr>'
	
		# Last IP
		print '<td><td>&nbsp;</td><td></td></tr>'
		print '<tr><td align=right><b>Last IP:</b></td><td>' + IP + '</td></tr>'
	
		# Creation Date
		print '<tr><td align=right><b>Created:</b></td><td>'+str(theuser.created)
	
		if createdYears+createdDays == 0:
			print ' (today)'
		else:		
			print ' (' + str(createdYears) + words.ChooseWord(createdYears, ' year', ' years') + ' ' + str(createdDays) + words.ChooseWord(createdDays, ' day', ' days') + ' ago)'
	
		print "</td></tr>"
	
		print '<tr><td align=right><b>Last Used:</b></td><td>'+str(theuser.lastused)
		
		if lastusedYears == 0 and lastusedDays == 0:
			print ' (today)'
		else:
			print ' (' + str(lastusedYears) + words.ChooseWord(lastusedYears, ' year', ' years') + ' ' + str(lastusedDays) + words.ChooseWord(lastusedDays, ' day', ' days') + ' ago)'
	
	
		print "</td></tr>"
	
			
		# Delete!
		if user.IsAdmin() and (theuser.usertype < user.usertype): #user.usertype >= 3:
	#		if theuser.usertype < user.usertype:
			print '<td><td>&nbsp;</td><td></td></tr>'
			print "<tr><td></td><td><input type='submit' name='delete_user' value='Delete the sucker' %s></td></tr>" % web.js_onclick_confirm("Really delete this sucker?")
		
		print '</table>'
		print '</form>'
	
		print "<br>"
	
		
		# Ratings
		ratings = ConvDB.GetSelfRatingHistory(theuser.id)
		if ratings != None:
			print '<b>Ratings on threads the user started:</b><br>'
			for thing in ratings: 
				print str(thing.rating) + ": " + thing.subject + ".<br>"
	
			print "<br>"
	
		ratings = ConvDB.GetRatingHistory(theuser.id)
		if ratings != None:
			print '<b>Ratings on other threads:</b><br>'
			for thing in ratings: 
				print str(thing.rating) + ": " + thing.subject + "<br>"
	
			print "<br>"
	
		print '<a href="users.py">Back to user manager</a>'
		
		theme.PrintFooter()


def PrintUserSearchForm():
	search = form.getvalue('search', '')

	print '<form method="post" action="users.py">'
	print 'Search for a user: <input name="search" type="text" size=12 maxlength=12 value="%s">' % (web.SanitizeHTML(search))
	print '<input type="submit" name="search_button" value="Search"></form><br>'


def MainView():
	"Show main page."	
	theme.PrintHeader('The Conversatron - User manager')
	theme.PrintNavBanner('User Manager')
	
	if 'message' in form:
		print """<div style="width:auto;border: 1px thin black solid; background-color:#336699; padding:0px 30px; margin:10px">%s</div>""" % form.getvalue('message','')

	theme.StartUserBox("User Manager")
	
	
	PrintUserSearchForm()
	
	counts = ConvDB.GetUserTypes()
	print "View user by type:<br><div style='margin-left:25px'>"
	for count in counts:
		print '<a href="users.py?op=list&type=%s">%s</a> (%s)<br>' % (
			count.usertype, level_names[count.usertype], count.count)
			
	print '<br><a href="users.py?op=list&type=all">All</a><br>'
	print '<a href="users.py?op=list&type=banned">Banned</a><br>'
	print "</div>"

	theme.EndUserBox()
	theme.PrintFooter()


def MakeUserTable(list, cols=6):
	count = 0
	print '<table><tr>'
	
	for item in list:
		print '<td><a href="users.py?op=lookup&name=' + urllib.quote_plus(item.name) + '">'+item.name+'</a></td>'
		count = count+1
		if count == cols:
			count = 0
			print '</tr><tr>'
			
	print '</tr></table>'


def HandleList(kind = None):
	"Show a list of all users."
	
	theme.PrintHeader('The Conversatron - User manager')
	theme.PrintNavBanner('User Manager')
	
	if kind=='all':
		sql = "select id,name,usertype from user order by name"
		users = db.loadObjects(sql)
		boxtitle = "All Users"
		
	elif kind=="banned":
		sql = "select id,name,usertype from user where banned='y' order by name"
		users = db.loadObjects(sql)
		boxtitle = "Banned Users"
		
	else:
		sql = "select id,name,usertype from user where usertype=%s order by name"
		kind = int(kind)
		users = db.loadObjects(sql, kind)
		boxtitle = level_names.get(kind, "?")
	
	if users is None: users = ()
	
	print "<h2>" + boxtitle + "</h2>"

	MakeUserTable(users)
	
	print '<br><a href="users.py">Back to user manager</a>'
	
	theme.PrintFooter()


def HandleSearch():
	search = form.getvalue('search', '')
	
	if search=='':
		web.RedirectInFolder('/users.py')
		
	users = db.loadObjects("select name from user where user.name like '%" + search + "%' order by name")

	if len(users) == 1  and users[0].name.lower()==search.lower():
		web.RedirectInFolder('/mans/users.py?op=lookup&name=' + users[0].name)
		web.quit()

	theme.PrintHeader('The Conversatron - User manager')
	theme.PrintNavBanner('User Manager')
	PrintUserSearchForm()
	
	if len(users) > 0:
		MakeUserTable(users)
	else:
		print 'No users found with that string.'
		
	print '<br><a href="users.py">Back to user manager</a>'
	
	theme.PrintFooter()

def HandleZark():
	"Delete all user's crudlings"
	
	try:
		id = int(form["id"].value)
		theuser = db.loadRow('user', id)
#		theuser = db.loadObject('select * from user where id='+str(id))
		if theuser == None:
			raise Exception
			
		crudlings = db.loadObjects('select id from user where lastip="'+theuser.lastip+'" and id != '+str(id))
		for crud in crudlings:
			ConvDB.DeleteUser(crud.id)
		
		CacheAllThreadRatings()
	except:
		pass
		
	web.RedirectToSelf()

# ------- begin ----------

theme = themes.LoadTheme()

page = UserMan()
page.run()
