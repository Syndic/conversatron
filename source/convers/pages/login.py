#!/usr/bin/env python
"""User sign-in/sign-out
"""

import themes
import web

from StandardVars import *
from BasicPage import BasicPage
from Consts import Consts
import User


buttons = Consts(
	Create="create-button", 
	SignIn="sign-in-button", 
	SignOut="sign-out-button")

actions = Consts(
	Create="create", 
	SignOut="signout")
	
forms = Consts(SignIn="sign-in", Create="create")

which_form = {
	buttons.Create: forms.Create,
	actions.Create: forms.Create,
	buttons.SignIn: forms.SignIn
	}

class LoginScreen(BasicPage):
	def __init__(self):
		BasicPage.__init__(self, 
			post_buttons=buttons,
			actions=['op', actions])
			
		self.buttonHandlers = {
			buttons.Create: self.CreateUser,
			buttons.SignIn: self.SignIn
			}
			
		self.formErrors = []

	def run(self):
		if self.postButton:
			self.dispatchButton()
		elif self.action:
			self.HandleOp()
		else:
			self.SignInForm()
			
	def HandleOp(self):
		if self.action == actions.Create:
			self.CreateForm()
		elif self.action == actions.SignOut:
			User.SignOut()
			web.GoHome()
			
	def SignIn(self):
		name = form.getvalue('name', '')
		passwd = form.getvalue('passwd', '')
		
		if name=="" or passwd=="":
			PrintError("Name and password fields must not be left blank.")
		
		if User.HostileCharacters(name+passwd):
			PrintError("Please don't use any of the following characters: &lt; &gt; &amp; ; - %<br>")
		
		try:
			user = User.Get(db, name,passwd)
			user.SignIn()
			web.GoHome()
		except User.Error, e:
			PrintError(e)
		
		web.GoHome()
		
	def CreateUser(self):
		name = form.getvalue('name', '')
		passwd = form.getvalue('passwd', '')
		passwd2 = form.getvalue('passwd2', '')
		
		if name=='' or passwd=='' or passwd2=='':
			PrintError("Don't leave any fields blank.")
	
		if User.HostileCharacters(name+passwd):
			PrintError("Please don't use any of the following characters: &lt; &gt; &amp; ; - %<br>")
		
		user = db.loadObject('select * from user where name="%s"'%(name))
			
		if user != None:
			PrintError("Sorry, that user name is already taken. Please try a different one.")
		
		if passwd != passwd2:
			PrintError("Hey! Your passwords didn't match. We can't let you get away with that sort of sloppyness here!")
			
		user = User.Create(db, name, passwd, gender=form.getvalue('gender', 'n'))
		user.SignIn()
		web.GoHome()
		
	def SignInForm(self):
		"Print out the login user form."
		theme.PrintHeader('Login Manager')	
		theme.StartUserBox("Login to The Conversatron:", "40%")
		
		print """
<form method="post" action="login.py" id="sign-in">
<table>
<tr>
	<td align=right>Name: </td>
	<td><input type="text" name="name" size=12 maxlength=12></td>
</tr>
<tr>
	<td align=right>Password: </td>
	<td><input type="password" name="passwd" size=12 maxlength=12></td>
</tr>
<tr>
	<td></td>
	<td><input type="submit" name="sign-in-button" value="Login"></td>
</tr>
</table>
</form>"""
		theme.EndUserBox()
		theme.PrintFooter()
		
	def CreateForm(self):
		"Print out the create user form."
		theme.PrintHeader('Login Manager')
		theme.StartUserBox("Create a new account")
		
		print '<form method="post" action="login.py" id="create-user">'
		print '<table>'
		print '<tr><td>Desired username:</td><td><input type="text" name="name" size=12 maxlength=12></td></tr>'
		print '<tr><td colspan=2><hr noshade></td></tr>'
		print '<tr><td>Password :</td><td><input type="password" name="passwd" size=12 maxlength=12></td></tr>'
		print '<tr><td>And again:</td><td><input type="password" name="passwd2" size=12 maxlength=12></td></tr>'
		print '<tr><td colspan=2><hr noshade></td></tr>'
		print '<tr><td>Gender:</td><td>'
		print '<input name="gender" value="n" type="radio" checked>None of your business<br>'
		print '<input name="gender" value="m" type="radio">Male<br>'
		print '<input name="gender" value="f" type="radio">Female<br>'
		print '</td></tr>'
		print '<tr><td></td><td><input type="submit" name="create-button" value="Create"></td></tr>'
		print '</table></form>'
		
		print "Please don't use any of the following characters: &lt; &gt; &amp; ; - %<br>"
		theme.EndUserBox()
		theme.PrintFooter()
		

def PrintError(error):
	"Print an error box with the specified text."
	
	theme.PrintHeader('Login Manager')
	theme.StartErrorBox('Input error')
	
	print error
	
	theme.EndErrorBox()
	theme.PrintFooter()

	web.quit()
	

def HandleLoginForm():
	"Print out the login user form."
	theme.PrintHeader('Login Manager')	
	theme.StartUserBox("Login to The Conversatron:", "40%")
	
	print '<form method="post" action="login.py"><input type="hidden" name="op" value="login">'
	print '<table><tr><td>Name :</td><td><input type="text" name="name" size=12 maxlength=12></td></tr>'
	print '<td>Password :</td><td><input type="password" name="passwd" size=12 maxlength=12></td></tr></table>'
	print '<input type="submit" value="Login"></form>'
	
	theme.EndUserBox()
	theme.PrintFooter()


def HandleLogin():
	"Handle a user attempting to log in an existing account."
	
	name = form.getvalue('name', '')
	passwd = form.getvalue('passwd', '')
	
	if name=="" or passwd=="":
		PrintError("Name and password fields must not be left blank.")
	
	if User.HostileCharacters(name+passwd):
		PrintError("Please don't use any of the following characters: &lt; &gt; &amp; ; - %<br>")
	
	try:
		user = User.Get(db, name,passwd)
		user.SignIn()
		web.GoHome()
	except User.Error, e:
		PrintError(e)
	
	web.GoHome()


def HandleLogout():
	"Log out and uncookie the user."
	User.SignOut()
	web.GoHome()


def HandleCreateForm():
	"Print out the create user form."
	theme.PrintHeader('Login Manager')
	theme.StartUserBox("Create a new account")
	
	print '<form><form method="post" action="login.py"><input type="hidden" name="op" value="fincreate">'
	print '<table>'
	print '<tr><td>Desired username:</td><td><input type="text" name="name" size=12 maxlength=12></td></tr>'
	print '<tr><td colspan=2><hr noshade></td></tr>'
	print '<tr><td>Password :</td><td><input type="password" name="passwd" size=12 maxlength=12></td></tr>'
	print '<tr><td>And again:</td><td><input type="password" name="passwd2" size=12 maxlength=12></td></tr>'
	print '<tr><td colspan=2><hr noshade></td></tr>'
	print '<tr><td>Gender:</td><td>'
	print '<input name="gender" value="n" type="radio" checked>None of your business<br>'
	print '<input name="gender" value="m" type="radio">Male<br>'
	print '<input name="gender" value="f" type="radio">Female<br>'
	print '</td></tr>'
	print '</table><br><input type="submit" value="Create"></form>'
	
	print "Please don't use any of the following characters: &lt; &gt; &amp; ; - %<br>"
	theme.EndUserBox()
	theme.PrintFooter()

	

def HandleCreate():
	"Create a new user!"
	
	name = form.getvalue('name', '')
	passwd = form.getvalue('passwd', '')
	passwd2 = form.getvalue('passwd2', '')
	
	if name=='' or passwd=='' or passwd2=='':
		PrintError("Don't leave any fields blank.")

	if User.HostileCharacters(name+passwd):
		PrintError("Please don't use any of the following characters: &lt; &gt; &amp; ; - %<br>")
	
	user = db.loadObject('select * from user where name="%s"'%(name))
		
	if user != None:
		PrintError("Sorry, that user name is already taken. Please try a different one.")
	
	if passwd != passwd2:
		PrintError("Hey! Your passwords didn't match. We can't let you get away with that sort of sloppyness here!")
		
	user = User.Create(db, name, passwd, gender=form.getvalue('gender', 'n'))
	user.SignIn()
	web.GoHome()


# ---- start here
theme = themes.LoadTheme()
# theme.debug = True
# op = form.getvalue('op', 'loginform')
# 
# if op == 'loginform':
# 	HandleLoginForm()
# elif op == 'login':
# 	HandleLogin()
# elif op == 'logout':
# 	HandleLogout()
# elif op == 'create':
# 	HandleCreateForm()
# elif op == 'fincreate':
# 	HandleCreate()

page = LoginScreen()
page.run()
