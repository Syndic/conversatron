#!/usr/bin/env python
"""User sign-in/sign-out
"""

import themes
import web

from StandardVars import *
from BasicPage import BasicPage
from Consts import Consts
import User

from WebForms import Template
from WebForms.Controls import *

_text = {'size':12, 'maxlength': 12}

form_controls = (
	TextInput(name='name', id='name', **_text),

	PasswordInput(name='passwd', **_text),
	PasswordInput(name='passwd2', **_text),

	TextArea(name="desc", rows=10, cols=60),

	RadioButton(name='gender', value='n', checked='checked'),
	RadioButton(name='gender', value='m'),
	RadioButton(name='gender', value='f'),
	
	SubmitButton(name='create-button', value='Create'),
	)

create_form = """
<form method="post" id="create_user">
<table>
<tr>
<td valign=top>Desired username:</td>
<td><x:control name="name" onchange="name_changed()" />

<button type="button" onclick="return check_name()" name="check-name-button" id="check-name-button" class="action" value="1">Check availability</button>

<img src="/img/loading.gif" align="absmiddle" style="display: none;" class="spinner" id="check-name-spinner"><br>
<div style="display:none;margin-top:2px;margin-left:5px;font: normal 11px Verdana,Arial,Helvetica,sans-serif;" id="name-status"></div>
</td>
</tr>

<tr><td colspan=2><hr noshade></td></tr>
<tr>
<td>Password :</td>
<td><x:control name="passwd" /></td>
</tr>

<tr>
<td>And again:</td>
<td><x:control name="passwd2" /></td>
</tr>

<tr><td colspan=2><hr noshade></td></tr>

<tr>
<td>Description:</td>
<td><x:control name="desc" /></td>
</tr>


<tr>
<td>Gender:</td>
<td>
<x:control name="gender:n" />None of your business<br>
<x:control name="gender:m" />Male<br>
<x:control name="gender:f" />Female<br>
</td>
</tr>

<tr><td></td>
<td><x:control name="create-button" /></td>
</tr>
</table>
</form>"""

page_script = """
<script>
var request = new Request();

function check_name_url(name){
	if (name == null) name = document.forms.create_user.name.value;
	return "check_name.py?name=" + escape(name)
}

function got_name(get){
	if (get.readyState != ReadyState.Complete) return;
	if (get.status != HttpStatus.OK) return;
	
	var js = get.responseText;
	if (js)
	{
		var result = eval(js.trim());
		show_name_status(result[1])		
	}
}

function show_name_status(message){	
	if (message) {
		Display.text('name-status', message)
		Display.show('name-status')
	} else { 
		Display.text('name-status', '')
		Display.hide('name-status')
	}
	
	Display.enable('check-name-button')
	Display.hide('check-name-spinner')	
}

function name_changed(){
	request.Cancel()
	if (!request.FromCache(check_name_url(), got_name))
		show_name_status()
}

function check_name(){
	if (!request.Use()) create_user.submit();

	Display.disable('check-name-button')	
	Display.show('check-name-spinner')
	Display.show('name-status')
	Display.text('name-status', "Checking...")
	
	request.CachedGet(check_name_url(), got_name)
	
	return false;
}
</script>
"""

buttons = Consts(
	Create="create-button",
	CheckName="check-name-button"
	)

class CreateAccountPage(BasicPage):
	def __init__(self):
		if not user.IsGuest(): web.GoHome()
	
		BasicPage.__init__(self, 
			name = "Create an Account",
			post_buttons=buttons)
			
		self.buttonHandlers = {buttons.Create: self.CreateUser}			
		self.Error = None

	def run(self):
		if self.postButton:
			self.dispatchButton()
		
		self.CreateForm()
						
	def CreateUser(self):
		name = form.getvalue('name', '')
		passwd = form.getvalue('passwd', '')
		passwd2 = form.getvalue('passwd2', '')
		
		if name=='' or passwd=='' or passwd2=='':
			self.Error = "Don't leave any fields blank."
			return
	
		if User.HostileCharacters(name+passwd):
			self.Error = "Please don't use any of the following characters: &lt; &gt; &amp; ; - %"
			return

		user = db.loadValue("select id from user where name=%s", name)		
		#user = db.loadObject('select * from user where name="%s"'%(name))
			
		if user != None:
			self.Error = "Sorry, that user name is already taken. Please try a different one."
			return
		
		if passwd != passwd2:
			self.Error = "Hey! Your passwords didn't match. We can't let you get away with that sort of sloppyness here!"
			return
			
		user = User.Create(db, name, passwd, gender=form.getvalue('gender', 'n'))
		user.SignIn()
		web.GoHome()
		
	def CreateForm(self):
		"Print out the create user form."
		theme.PrintHeader(self.name, {"javascript": page_script})
		theme.StartUserBox("Create a new account")
		
		if self.Error:
			print "<font color='red'>%s</font><br>" % (self.Error)
			
		t = Template.A(form_controls)
		t.template = create_form
		t.parse()
		t.fill(FormDict(form))
		t.render()
		p = """
<form method="post" id="create_user">
<table>
<tr>
<td valign=top>Desired username:</td>
<td><input type="text" id="name" name="name" size=12 maxlength=12 onchange="name_changed()"> <button type="submit" onclick="return check_name()" name="check-name-button" id="check-name-button" class="action" value="1">Check availability</button>
<img src="/img/loading.gif" align="absmiddle" style="display: none;" class="spinner" id="check-name-spinner"><br>
<div style="display:none;margin-top:2px;margin-left:5px;font: normal 11px Verdana,Arial,Helvetica,sans-serif;" id="name-status"></div>
</td>
</tr>

<tr><td colspan=2><hr noshade></td></tr>
<tr>
<td>Password :</td>
<td><input type="password" name="passwd" size=12 maxlength=12></td>
</tr>

<tr>
<td>And again:</td>
<td><input type="password" name="passwd2" size=12 maxlength=12></td>
</tr>

<tr><td colspan=2><hr noshade></td></tr>

<tr>
<td>Gender:</td>
<td>
<input name="gender" value="n" type="radio" checked>None of your business<br>
<input name="gender" value="m" type="radio">Male<br>
<input name="gender" value="f" type="radio">Female<br>
</td>
</tr>

<tr><td></td>
<td><input type="submit" name="create-button" value="Create"></td>
</tr>
</table>
</form>"""
		
		print "Please don't use any of the following characters: &lt; &gt; &amp; ; - %<br><br><a href='/'>Nevermind...</a>"
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
page = CreateAccountPage()
page.run()
