#!/usr/bin/env python
"""User sign-in/sign-out
"""

import themes
import web

from StandardVars import *
from BasicPage import BasicPage
from Consts import Consts
import User

buttons = Consts(SignIn="sign-in-button")

class SignInPage(BasicPage):
	def __init__(self):
		BasicPage.__init__(self, 
			post_buttons=buttons)
			
		self.formErrors = []

	def run(self):
		if self.isPost:
			self.SignIn()

		self.SignInForm()
			
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
		
	def SignInForm(self):
		"Print out the login user form."
		theme.PrintHeader('Login Manager')	
		theme.StartUserBox("Login to The Conversatron:", "40%")
		
		print """
<form method="post" id="sign-in">
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

def PrintError(error):
	"Print an error box with the specified text."
	
	theme.PrintHeader('Login Manager')
	theme.StartErrorBox('Input error')
	
	print error
	
	theme.EndErrorBox()
	theme.PrintFooter()

	web.quit()

theme = themes.LoadTheme()
page = SignInPage()
page.run()
