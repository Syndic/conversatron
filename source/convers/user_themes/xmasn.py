import ConvOutput
import time
import stars

#standard box colors
ecolor = '#FFAAAA'
ucolor = '#F763A3'
wcolor = '#99DD99'
acolor = '#AAFFAA'

bgcolor = '#CACACD'


boxtitlecolor = '#CEB75F'

mainlogo = '<img src="/img/xmn-logo.gif" width="440" height="80" alt="The Conversatron">'
minilogo = '<img src="/img/xmn-minilogo.gif" width="88" height="160" alt="Back to main page" border="0" hspace=5 align=left>'


Weekdays = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')


def PrintIndex(user, slogan, pending, intrash, threads, messages, favs, council):
	"The biggy. This mamma takes all the info needed for the frontpage and churnes it out."
	
	print 'Pragma: no-cache'
	print 'Content-type: text/html\n'
	print '<html><head><title>The Conversatron</title>'
	print '<meta name="description" content="Interact with undirected pop-culture, talk to imaginary characters, it\'s fun!">'
	print '<meta name="keywords" content="conversatron, forum, pop culture, debate, discuss, converse, humor, entertainment">'

	ConvOutput.PrintJavascript()
	
	print '<body bgcolor="#000000" text="#82C466" link="#40C0FF" vlink="#6666FF" alink="#FFCE36">'
	print '<table border=0 width="100%"><tr><td>'
	if user.usertype == 0:
		print '<a href="login.py">Sign in</a> or <a href="login.py?op=create">create an account</a> for the full Conversatron experience!'
	else:
		print '<font face="Trebuchet MS">Welcome, <font color="#FFFFFF"><b>'+user.name+'</b></font>.<br><font size="-2">If you\'re not '+user.name+', <a href="login.py?op=logout">click here</a>.</font></font>'
	
	print '</td><td align="center">'+mainlogo+'</td>'
	print '<td align="center" valign="top">'+time.strftime("%A, %B %d, %Y",time.localtime(time.time()))+'<br>'
	
	if user.usertype >= 2:
		if pending > 0:
			print '<a href="threadman.py"><img src="/img/BeMessages.gif" width="32" height="32" border="0" alt="'+str(pending)+' new threads" align="bottom">['+str(pending)+']</a>&nbsp;&nbsp;&nbsp;'
		if intrash > 0:
			print '<a href="threadman.py?op=listdel"><img src="/img/BeTrash.gif" width="32" height="32" border="0" alt="'+str(intrash)+' threads in trash" align="bottom">['+str(intrash)+']</a>'

	print '</td></tr><tr><td align="center" colspan="3"><font face="Trebuchet MS">'+slogan+'</font></td></tr>'
	print '<tr><td align="center" colspan="3"><img src="/img/twnklbar.gif" height=50 width=443></td></tr></table>'
	
	print '<table width="66%" border=0 cellspacing=0 cellpadding=2 align="left">'
	print '<tr><td align="center" bgcolor="#F763A3"><font size="-1" color="#000000" face="Verdana, Helvetica"><b>Current Topics</b></font></td></tr><tr><td bgcolor="#F763A3">'
	print '<table border=0 cellspacing=1 cellpadding=0 width="100%"><tr><td bgcolor="#F763A3">'

	print '<table cellspacing=0 cellpadding=2 border=0 width="100%">'
	
	odd = 0
	curday = None
	for row in threads:
		if curday != None and curday != int(row.yearday):
			print '<tr><td bgcolor="#F763A3" colspan=4 align=center><font size="3"><b>'+Weekdays[int(row.weekday)]+'</b></font></td></tr>'
		curday = int(row.yearday)
		
		if odd:
			color = '#000000'
		else:
			color = '#333333'
		odd = not odd
		
		star = stars.RateThread(row)
		
		followup = ''
		ratings = '&nbsp;'
		archive = ''
		
		if user.usertype >= 2:
			if row.followup == 'y':
				followup = '&nbsp;<img src="/img/farrow.gif" width="8" height="12" alt="" border="0">'
			if int(row.numvotes) > 0:
				ratings = '<font size=1>'+str(row.numvotes)+' / '+str(row.rating)+'</font>'
			if row.archive == 'y':
				archive='&nbsp;&nbsp;<img src="/img/archive.gif" width="16" height="16" alt="Message will be archived" border="0">'

			
		print '<tr bgcolor="'+color+'"><td><a href="convers.py?topic='+str(row.id)+'&count='+str(row.count)+'">'+row.subject+'</a>'+followup+'</td><td>'+str(row.count)+star+'</td><td><font size="-1">'+str(row.time)+'</font>'+archive+'</td><td align=right>'+ratings+'</td></tr>'
	
	print '<tr><td bgcolor="#F763A3" colspan=4 align=right><a href="/archive/"><font size="3" face="Georgia"><img src="/img/9arrow.gif" width="5" height="9" alt="" border="0"><b>Archives</b></font></a></td></tr>'
	print '</table>'
	EndBox()
	
	print '<table width="33%" cellpadding=5><tr><td>'
	
	StartBox('Whatnot', '#FFCE36', "100%", '#000000')
	ConvOutput.IncludeFile('info.ihtml')
	
	if user.usertype >= 1:
		print '<font size=2 face="Verdana">'
		print '<br><a href="prefs.py">Account Settings</a>'
		print '</font><br><br>'
	
	print 'Theme by <a href="http://www.virtue.nu/julieos/">Julie Ledgerwood</a>'
	EndBox()
	print '<br>'
	
	if user.usertype >= 2 or messages:
		StartBox('Messages', '#9999dd', "100%", '#000000')
		print '<font size=2 face="Verdana">'
		
		if user.usertype >= 2:
			print '<a href="messenger.py">Write a Message</a><br>'
		
		for item in messages:
			print "<hr noshade>"
			print '<a href="messenger.py?op=view&id='+str(item.id)+'">'+item.subject+'</a><br>'
			if item.askee:
				print 'From '+str(item.askee)+' ('+str(item.whenis)+')'
			else:
				print 'From '+str(item.fromuser)+' ('+str(item.whenis)+')'
			print ' <a href="messenger.py?op=del&id='+str(item.id)+'">[del]</a>'
		
		print '</font>'
		EndBox()
		print '<br>'
	
	if user.usertype >= 3:
		StartBox('Admin Stuff', '#9999dd', "100%", '#000000')
		if council:
			print council+'<br><br>'
		ConvOutput.IncludeFile('admin.ihtml')
		EndBox()
		print '<br>'
	
	if user.usertype >= 2:
		StartBox('Writer Stuff', '#9999dd', "100%", '#000000')
		ConvOutput.IncludeFile('writer.ihtml')
		EndBox()
		print '<br>'
	
	
	
	print '</td></tr></table><br clear="all"><br>'
	
	StartBox('Start a new topic', '#82C433', None, '#000000')
	
	print '<form method="post" action="newtopic.py">'
	print '<font face="Verdana" size=2><b>Subject:</b></font> <input name="subject" type="text" size=32 maxlength=32><br><br>'
	print '<font face="Verdana" size=2><b>Question:</b></font><br>'
	print '<textarea name="body" cols="72" rows="10" wrap="soft" class="ask"></textarea><br>'
	print '<input type=image src="/img/button_post.gif"  border=0>'
	
	if user.usertype >= 2:
		print '<br><br><table width="100%" border=1 bordercolor="#000000" cellpadding=4 cellspacing=0><tr><td>'
		print '<font size="-1"><input name="asaskee" type="checkbox">Make this question come from:'
		print '<input name="shortname" type="text" size=12 maxlength=12> '
		print '<a href="askeebrowse.html" target="window">Browse...</a> '
		ConvOutput.PrintFavoriteSelector(favs, 'askee')
		print '<select name="emotion"><option value="n">Normal<option value="h">Happy<option value="a">Angry<option value="s">Sad</select><br>'
		print '</font></td></tr></table>'
	
	print '</form>'
	
	EndBox()
	
	PrintFooter()

def PrintThread(thread, entries, userlevel=0, archive=0, archindex=0):
	
	if archive:
		PrintArchiveHeader('The Conversatron - '+thread.subject)
	else:
		PrintHeader('The Conversatron - '+thread.subject)
	
	print '<table><tr><td>'
	
	print '<a href="/">'+minilogo+'</a><br>'
	print '<font color="#666666" size="3" face="Trebuchet MS"><b>The Topic:</b><br><font size=5>'
	print thread.subject
	print '</font></font></td></tr></table><br>'
	print '<font color="#666666" size="3" face="Trebuchet MS"><b>The Question:</b></font><br>'
	
	listlen = len(entries)
	for num in range(listlen):
		item = entries[num]
	
		if 1 < num:
			previd = entries[num-1].id
		else:
			previd = 0

		if 0 < num < listlen - 1:
			nextid = entries[num+1].id
		else:
			nextid = 0

		PrintEntry(item, userlevel, previd, nextid)

		if num == 0:
			print '<font color="#666666" size="3" face="Trebuchet MS"><b>Responses:</b></font><br>'
	
	if archive:
		print '<br>'
		print '<p align="center"><font face="Trebuchet MS" size=4><a href="/archive/archives'+str(archindex)+'.html">Back to Archive Index</a></font></p>'

	
def PrintEntry(entry, userlevel=0, previd=None, nextid=None):
	"Print one thread entry."
	
	color = "#303030"
	
	if entry.aname:
		if entry.emotion == 'h':
			image = entry.happypic
			color = "#003500"
		elif entry.emotion == 'a':
			image = entry.angrypic
			color = "#350000"
		elif entry.emotion == 's':
			image = entry.sadpic
			color = "#000040"
		else:
			image = entry.normpic
			color = "#303030"
			
		image = "/askees/"+image
		name = entry.aname
	elif entry.uname:
		if entry.picture:
			image = "/users/"+entry.picture
		elif entry.gender == 'm':
			image = "/users/asker-m.gif"
		elif entry.gender == 'f':
			image = "/users/asker-f.gif"
		else:
			image = '/users/asker.gif'
		name = entry.uname
	else:
		image = '/users/asker.gif'
		name = 'The Asker'
	
	side = entry.side
	when = entry.time
	text = entry.body
	
	buttonStr = '&nbsp;&nbsp;&nbsp;('+when+')&nbsp;[<a href="entry.py?id='+str(entry.id)+'">edit</a>]&nbsp;'

	if previd:
		buttonStr = buttonStr + ' [<a href="entry.py?op=swap&id='+str(entry.id)+'&sid='+str(previd)+'">up</a>]&nbsp;'
		
	if nextid:
		buttonStr = buttonStr + ' [<a href="entry.py?op=swap&id='+str(entry.id)+'&sid='+str(nextid)+'">down</a>]&nbsp;'
	
	if entry.flag=="s":
		buttonStr = buttonStr + ' <a name="followup"></a>[<a href="entry.py?id='+str(entry.id)+'&op=activate">activate</a>]&nbsp;'
		buttonStr = buttonStr + ' <a name="followup"></a>[<a href="entry.py?id='+str(entry.id)+'&op=delete">kill</a>]&nbsp;'
		color = "#cccccc"
		text = "<font color='#666666'>" + text + "</font>"
	
	if entry.url:
		urlstart = '<a href="' + entry.url + '">'
		urlstop = '</a>'
	else:
		urlstart = ''
		urlstop = ''
		
	if side == 'r':
		print '<table cellpadding=0 cellspacing=0 border=0><tr><td bgcolor="#0000DD"><b>'+name+'</b>'
		if userlevel > 1: print buttonStr
		print '</td><td bgcolor="#0000DD">&nbsp;</td></tr>'
		print '<tr><td valign="top" bgcolor="'+color+'"><table cellpadding=4><tr><td valign="top"><img src="/img/_.gif" width=100 height=1 alt=""><br>'+text+'</td></tr></table></td>'
		print '<td valign="top">'+urlstart+'<img src="'+image+'" width=80 height=100 border=0 alt="">'+urlstop+'</td></tr></table>'
	else:
		print '<table cellpadding=0 cellspacing=0 border=0><tr><td bgcolor="#0000DD">&nbsp;</td><td bgcolor="#0000DD"><b>'+name+'</b>'
		if userlevel > 1: print buttonStr
 		print '</td></tr>'
		print '<tr><td valign="top">'+urlstart+'<img src="'+image+'" width=80 height=100 border=0 alt="">'+urlstop+'</td>'
		print '<td valign="top" bgcolor="'+color+'"><table cellpadding=4><tr><td valign="top"><img src="/img/_.gif" width=100 height=1 alt=""><br>'+text+'</td></tr></table></td></tr></table>'

	
	if userlevel > 1:
		import urllib
	
		print '<font size="-1" color="#FFFFFF">Posted by '
		if entry.uname:
			print '<a href="userman.py?op=lookup&name=' + urllib.quote_plus(entry.uname) + '">'+entry.uname+'</a>'
		else:
			print 'guest'
		print ' at <a href="resolve.py?addr='+urllib.quote_plus(entry.addr)+'" target="window">['+entry.addr+']</a>'
		print ' using '+entry.client+'</font><br>'
	
	print "<br>"
	
def PrintNavigation(id):
	print '<br><table align=center><tr><td align="left"><a href="convers.py?prev='+str(id)+'"><img src="/img/xmn-prev.gif" border=0 width=120 height=20></a></td>'
	print '<td align="center">&nbsp;&nbsp;&nbsp;<a href="/">'+minilogo+'</a>&nbsp;&nbsp;&nbsp;</td>'
	print '<td align="right"><a href="convers.py?next='+str(id)+'"><img src="/img/xmn-next.gif" border=0 width=100 height=20></a></td></tr></table><br>'


def PrintHeader(title):
	"Standard header for all dynamic pages"
	
	print 'Pragma: no-cache'
	print 'Content-type: text/html\n'
	print '<html><head><title>'+title+'</title>'

	ConvOutput.PrintJavascript()
	
	print '</head><body bgcolor="#000000" text="#FFFFFF" link="#40C0FF" vlink="#6666FF" alink="#FFCE36">'

def PrintArchiveHeader(title):
	"Standard header for all dynamic pages"
	
	print '<html><head><title>'+title+'</title></head>'
	print '<body bgcolor="#000000" text="#FFFFFF" link="#40C0FF" vlink="#6666FF" alink="#FFCE36">'


def PrintNavBanner(title):
	"Print out a page header that lets you click back to the main page"
	
	print '<table><tr><td>'
	print '<a href="/">'+minilogo+'</a></td>'
	print '<td><font color="#666666" size="+1" face="Trebuchet MS">'+title+'</font></td>'
	print '</tr></table><br>'

def PrintFooter():
	print '<p align=right><font color="#000000" size="-2">Images &copy; their respective owners. Text &copy; 1999-'+str(time.localtime(time.time())[0])+' The Conversatron. For entertainment purposes only.</font></p></body></html>'

def StartBox(title, color, width=None, intcolor="#000000", padding=3):
	"Start a colored group box"
	
	if width:
		print '<table width="'+width+'" border=0 cellspacing=0 cellpadding=2>'
	else:
		print '<table border=0 cellspacing=0 cellpadding=2>'
	print '<tr><td align="center" bgcolor="'+color+'"><font size="-1" color="#000000" face="Verdana, Helvetica"><b>'+title+'</b></font></td></tr><tr><td bgcolor="'+color+'">'
	print '<table border=0 cellspacing=1 cellpadding='+str(padding)+' width="100%"><tr><td bgcolor="'+intcolor+'">'

def EndBox():
	print '</td></tr></table></td></tr></table>'


