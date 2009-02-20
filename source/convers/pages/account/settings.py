#!/usr/bin/env python
#Pref manager. Yeah!

from StandardVars import *
from BasicPage import BasicPage
import ConvDB
import web
import themes

import words
from Consts import Consts

from WebForms import Template
from WebForms.Controls import *

form_controls = (
	RadioButton(name='gender', value='n', checked='checked'),
	RadioButton(name='gender', value='m'),
	RadioButton(name='gender', value='f'),
	RadioButton(name='gender', value='t'),
	
	Select(options=[('x', "(Whatever. I don\'t care.)")], name='theme'),
		
	CheckBox(name='themeoverride', value='y'),

	SubmitButton(name='update_button', value='Update'),
)

buttons = Consts(Update = "update_button")
	
actions = Consts()

page_script = """
<script>
function loaded(){
	Display.set("passwords", document.settings.chpass.checked)
}
</script>
"""

class SettingsPage(BasicPage):
	def __init__(self):
		if not user.IsRegistered(): 
			web.GoHome()
		
		BasicPage.__init__(self,
			name="Account Settings",
			post_buttons = buttons,
			actions = ['op', actions] 
			)
			
		self.buttonHandlers = {
			buttons.Update: self.UpdateSettings
			}
			
	def run(self):
		if self.postButton:
			self.dispatchButton()
			return
		#else:
		self.ShowSettings()
	
	def ShowSettings(self):
		"View your preferences. NOW."
		theme = themes.LoadTheme()
		
		theme.PrintHeader('The Conversatron - Your Settings', {
			"javascript": page_script,
			"onload": "loaded()"
			})
			
		if "message" in form:
			print "<div class='message'>%s</div>" % web.SanitizeHTML(form.getvalue('message',''))

		theme.PrintNavBanner('Settings')
		
		theme.StartUserBox('Settings for '+user.name)
		
		favs = ConvDB.GetUserFavorites(user)
		
		theuser = db.loadObject('select *, TO_DAYS(lastused)-TO_DAYS(created) as days from user where name="%s"' % (user.name))
	
		userDays = 0
		userYears = 0
		if theuser.days is not None:
			userDays = theuser.days % 365
			userYears = theuser.days / 365
	
		print 'Account Created: '+str(user.created) + ', '
		print str(userYears) + words.ChooseWord(userYears, ' year', ' years')
		if userDays:
			print ' ' + str(userDays) + words.ChooseWord(userDays, ' day', ' days')
		print ' ago.<br>'
		
		print '<br>'
		
		theform = """
<form method="post" action="settings.py" name="settings">
Gender:<br>
<x:control name="gender:n" />None of your business<br>
<x:control name="gender:m" />Male<br>
<x:control name="gender:f" />Female<br>
<br>
<x:control name="gender:t" />The Toilet<br>
<br><br>

Theme:<br>
Default: <x:control name="theme" /><br>
<x:control name="themeoverride:y" /> My theme choice overrides the theme on posts.<br>
<br>
<x:control name="update_button" />
</form>
"""
		t = Template.A(form_controls)
		theme_select = t.get_control('theme')

		theme_list = themes.themeNames()
		for item in theme_list:
			theme_select.add_option(Option(theme_select, value=item))

		t.template = theform
		t.parse()
		t.fill(FormDict(form))
		t.render()

		
		print '<form method="post" action="settings.py" name="settings">'
		
		genders = (('n', 'None of your business'), ('m', 'Male'), ('f', 'Female<br>'), ('t', 'Toilet Fixture<br>'))
		
		print 'Gender:<br>'
		for (abbr, desc) in genders:
			checked = ""
			if user.gender==abbr: checked="checked"
	
			print '<input name="gender" value="%s" type="radio" %s>%s<br>' % (abbr, checked, desc)
		
		
		print '<br>Default theme: <select name="theme"><option value="">(Whatever. I don\'t care.)'
		theme_list = themes.themeNames()
	
		for item in theme_list:
			selected = ""
			if item == user.theme: selected = "selected"
			
			print '<option value="%s" %s>%s' % (item, selected, item)
			
		print '</select><br>'
		
		checked = ""
		if theuser.themeoverride == "y": checked = " checked"
		
		print '<input type="checkbox" name="alwaysusemytheme" value="y" %s> My theme choice overrides the theme on posts.<br>' % (checked)
		print '<br>'
	
		
		if user.IsWriter():
			print """
<div style="border:1px black solid;padding:5px;">
Favorites menu preview:<br>
"""
			web.PrintFavoriteSelector(favs, 'favaskee')
			print """
<a href="prefs.py?op=favform">Edit Favorites</a>
</div>
<br><br>"""
		
		print """	
<div style="padding:5px;border:1px solid black;">
<input id='chpass' name="chpass" type="checkbox" onclick="Display.set('passwords', this.checked)"> <label for='chpass'>Change Password?</label>

<table id="passwords">
<tr>
	<td>Current Password:</td>
	<td><input type="password" name="oldpasswd" value="" size=12 maxlength=12></td>
</tr>
<tr>
	<td>New Password:</td>
	<td><input type="password" name="passwd" value="" size=12 maxlength=12></td>
</tr>
<tr>
	<td>And again:</td>
	<td><input type="password" name="passwd2" value="" size=12 maxlength=12></td>
</tr>
</table>
</div>"""

		print '<br><input type="submit" name="update_button" value="Update"></form>'
		print "<br><br><a href='/'>Nevermind...</a><br>"
		
		theme.EndUserBox()
		theme.PrintFooter()
		
	def UpdateSettings(self):
		"Change your prefs. NOW."
		theme = themes.LoadTheme()
		
		user.gender = form.getvalue("gender", None)
		user.theme = form.getvalue("theme", '')
	
		# Are we changing the user's password?
		if form.getvalue('chpass'):
			passwd  = form.getvalue('passwd', '')
			passwd2 = form.getvalue('passwd2', '')
			
			# Passwords must match
			if passwd != passwd2:
				theme.PrintHeader('The Conversatron - Your Settings')
				theme.StartErrorBox('Input error')
				print "Your passwords don't match. Back up and try again.<br>"
				theme.EndErrorBox()
				theme.PrintFooter()
				return
			
			# Password can't be blank.
			if passwd == "":
				theme.PrintHeader('The Conversatron - Your Settings')
				theme.StartErrorBox('Input error')
				print "You can't have an empty password. Back up and try again.<br>"
				theme.EndErrorBox()
				theme.PrintFooter()
				return
			
			# Only do something if it's a new password
			if passwd != user.passwd:
				user.passwd = passwd
				ConvUtil.CookieUser(user)
				
		if form.getvalue('alwaysusemytheme', None):
			user.themeoverride="y"
		else:
			user.themeoverride="n"
		
		user.Update(db)
		web.RedirectToSelf("message=Account+Updated")
	
			
# def HandleView():
# 	"View your preferences. NOW."
# 	
# 	theme.PrintHeader('The Conversatron - Your Settings')
# 	theme.PrintNavBanner('Settings')
# 	
# 	theme.StartUserBox('Settings for '+user.name)
# 	
# 	favs = ConvDB.GetUserFavorites(user)
# 	
# 	theuser = db.loadObject('select *, TO_DAYS(lastused)-TO_DAYS(created) as days from user where name="%s"' % (user.name))
# 
# 	userDays = 0
# 	userYears = 0
# 	if theuser.days is not None:
# 		userDays = theuser.days % 365
# 		userYears = theuser.days / 365
# 
# 	#print 'Score: '+str(user.Score)+'<br>'
# 	print 'Account Created: '+str(user.created) + ', '
# 	print str(userYears) + words.ChooseWord(userYears, ' year', ' years')
# 	if userDays:
# 		print ' ' + str(userDays) + words.ChooseWord(userDays, ' day', ' days')
# 	print ' ago.<br>'
# 	
# 	print '<br>'
# 	
# 	print '<form method="post" action="prefs.py">'
# 	print '<input type="hidden" name="op" value="change">'
# 	
# 	
# 	genders = (('n', 'None of your business'), ('m', 'Male'), ('f', 'Female<br>'), ('t', 'Toilet Fixture<br>'))
# 	
# 	print 'Gender:<br>'
# 	for (abbr, desc) in genders:
# 		checked = ""
# 		if user.gender==abbr: checked="checked"
# 
# 		print '<input name="gender" value="%s" type="radio" %s>%s<br>' % (abbr, checked, desc)
# 	
# 	
# 	print '<br>Default theme:<select name="theme"><option value="">(Whatever. I don\'t care.)'
# 	theme_list = themes.themeNames()
# 
# 	for item in theme_list:
# 		selected = ""
# 		if item == user.theme: selected = "selected"
# 		
# 		print '<option value="%s" %s>%s' % (item, selected, item)
# 		
# 	print '</select><br>'
# 	
# 	checked = ""
# 	if theuser.themeoverride == "y": checked = " checked"
# 	
# 	print '<input type="checkbox" name="alwaysusemytheme" value="y" %s> My theme choice overrides the theme on posts.<br>' % (checked)
# 	print '<br>'
# 
# 	
# 	
# 	print '<table border><tr><td><input name="chpass" type="checkbox">Change Password</td>'
# 	if user.usertype > 1:
# 		print '<td>Current Favorites:</td>'
# 	print '</tr><tr><td>'
# 	print 'Password :<input type="password" name="passwd" value="" size=12 maxlength=12><br><br>'
# 	print 'And again:<input type="password" name="passwd2" value="" size=12 maxlength=12><br><br></td>'
# 	if user.usertype > 1:
# 		print '<td>Favorites menu preview:<br>'
# 		web.PrintFavoriteSelector(favs, 'favaskee')
# 		print '<br><a href="prefs.py?op=favform">Edit Favorites</a></td>'
# 	print '</tr></table><br><input type="submit" value="Update"></form>'
# 	
# 	theme.EndUserBox()
# 	theme.PrintFooter()
# 	
# 	
# def HandleChange():
# 	"Change your prefs. NOW."
# 	
# 	user.gender = form.getvalue("gender", None)
# 	user.theme = form.getvalue("theme", '')
# 
# 	# Are we changing the user's password?
# 	if form.getvalue('chpass'):
# 		passwd  = form.getvalue('passwd', '')
# 		passwd2 = form.getvalue('passwd2', '')
# 		
# 		# Passwords must match
# 		if passwd != passwd2:
# 			theme.PrintHeader('The Conversatron - Your Settings')
# 			theme.StartErrorBox('Input error')
# 			print "Your passwords don't match. Back up and try again.<br>"
# 			theme.EndErrorBox()
# 			theme.PrintFooter()
# 			return
# 		
# 		# Password can't be blank.
# 		if passwd == "":
# 			theme.PrintHeader('The Conversatron - Your Settings')
# 			theme.StartErrorBox('Input error')
# 			print "You can't have an empty password. Back up and try again.<br>"
# 			theme.EndErrorBox()
# 			theme.PrintFooter()
# 			return
# 		
# 		# Only do something if it's a new password
# 		if passwd != user.passwd:
# 			user.passwd = passwd
# 			ConvUtil.CookieUser(user)
# 			
# 	if form.getvalue('alwaysusemytheme', None):
# 		user.themeoverride="y"
# 	else:
# 		user.themeoverride="n"
# 	
# 	user.Update(db)
# 	web.GoHome()
# 
# 
# def IsFav(id, favs):
# 	"Is id in the favs list?"
# 	try:
# 		for item in favs:
# 			if id == item.id:
# 				return 1
# 	except:
# 		pass
# 	return 0
# 
# 
# def HandleFavForm():
# 	"Show ALL askees so the user can pick favorites."
# 	
# 	if user.usertype < 2:
# 		web.RedirectInFolder('/prefs.py')
# 	
# 	theme.PrintHeader('The Conversatron - Your Settings')
# 	
# 	print '<font size="+2">Favorites for '+user.name+'</font><hr>'
# 	
# 	print '<form method="post" action="prefs.py">'
# 	print '<input type="hidden" name="op" value="chfav">'
# 	
# 	try:
# 		list = ConvDB.GetAskeeList()
# 		favs = ConvDB.GetUserFavorites(user)
# 		
# 		if list==None:
# 			raise Exception
# 		numaskees = len(list)
# 		if numaskees == 0:
# 			raise Exception
# 			
# 		colheight = numaskees/3
# 		currow = 0
# 		currcat = ""
# 		
# 		print '<table bgcolor="#ccccFF"><tr><td>'
# 		for item in list:
# 			if str(item.category) != currcat:
# 				currcat = str(item.category)
# 				print '<br><b>'+currcat+'</b><br>'
# 			if IsFav(item.id, favs):
# 				print '<input name="'+str(item.id)+'" type="checkbox" checked> '
# 			else:
# 				print '<input name="'+str(item.id)+'" type="checkbox"> '
# 			print item.name+'<br>'
# 			currow = currow + 1
# 			if currow > colheight:
# 				print '</td><td>'
# 				currow = 0
# 		print '</td></tr></table>'
# 	except:
# 		pass
# 		
# 	print '<input type="submit" value="Update"></form>'
# 	
# 	theme.PrintFooter()
# 
# 
# def HandleChangeFavorites():
# 	"Change the favorite list."
# 	
# 	list = ConvDB.GetAskeeList()
# 	favs = ''
# 	first = 1
# 	
# 	for item in list:
# 		try:
# 			id = str(item.id)
# 			checked = form[id].value
# 			if checked:
# 				if first:
# 					favs = id
# 					first = 0
# 				else:
# 					favs = favs +','+id
# 		except:
# 			pass
# 	
# 	user.favorites = favs
# 	db.updateObject('user', user, 'id='+str(user.id))
# 	
# 	web.RedirectInFolder('/prefs.py?op=view')
# 	
# 
# # ----- Load up some shit
# theme = themes.LoadTheme()
# 
# op = form.getvalue('op', 'view')
# 
# if op == "view":
# 	HandleView()
# elif op == "change":
# 	HandleChange()
# elif op == "favform":
# 	HandleFavForm()
# elif op == "chfav":
# 	HandleChangeFavorites()

page = SettingsPage()
page.run()
