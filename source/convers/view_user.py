def HandleShowUser():
	"Bring up a user's info."
	if 'name' not in form: web.RedirectToSelf()
	
	genders = {'n': 'None of your business', 'm': 'Male', 'f': 'Female', 't': 'Toilet Fixture'}
	usertypes = (('Reader',1), ('Writer',2), ('Administrator',3), ('The Super',4))

	theme.PrintHeader('The Conversatron - User manager')
	theme.PrintNavBanner('User Manager')
	
	theuser = db.loadObject('select *, TO_DAYS(now()) - TO_DAYS(created) as create_days, TO_DAYS(now()) - TO_DAYS(lastused) as lastused_days from user where name=%s', form.getvalue('name'))
	
	if theuser == None:
		theme.StartErrorBox("User Unknown")
		print "Whoops, that user doesn't seem to exist. Gah!<br><br>"
		print '<a href="users.py">Back to user manager</a>'
		theme.EndErrorBox()
		theme.PrintFooter()
		
		web.quit()

	if theuser.url == None: theuser.url = ''

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
	if user.IsAdmin(): #user.usertype >= 3:
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
		print "<tr><td></td><td><input type='submit' name='delete_user' value='Delete the sucker'></td></tr>"
	
	print '</table>'
	print '</form>'

	print "<br>"
