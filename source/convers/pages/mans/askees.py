import urllib
import re

import ConvDB

from StandardVars import *
from SuperHash import SuperHash

import web
import themes

page_script = """
<script>
var request = new Request();

function setup_tree(){	
	var cattable = $('category-table')
	var cats = cattable.getElementsByTagName('a')
	for(var i = 0; i < cats.length; i++){
		cats[i].onclick = expand2;
	}
}

function get_url(category){
	return "askees.py?op=node&node="+escape(category)
}

function add_node(category, results){
	if (results.readyState != ReadyState.Complete) return;
	if (results.status != HttpStatus.OK) return;
		
	var html = results.responseText;
	if (html)
	{
		o = $("cat-"+escape(category))
		o.innerHTML = html
		o.className = ""
		Display.show(o)
	}	
}

function expand2(){
	var cat = this.name
	cat_div = $("cat-"+escape(cat))
	if (cat_div){	
		if (cat_div.className == "_"){
			cat_div.style.display="block"
			cat_div.innerHTML = '<img src="/img/loading.gif" align="absmiddle">';
			request.Get(get_url(cat),
				function(results){add_node(cat, results)}
			)
		}
		else
			Display.toggle(cat_div);
	}
	
	return false;
}

</script>
"""

def HandleNode():
	category = form.getvalue("node")
	askees = ConvDB.GetAskeesForCategory(category)
	PrintStandardAskeeTable(askees)


def PrintNewestAskees():
	global mode
	global formtarget

	i = 0
	askees = ConvDB.GetNewestAskees(15)

	print "<br>"
	print "Newest Askees<br>"
	
	for askee in askees:
		if mode == "browse":
			print '<a href="?op=bview&formtarget=' + str(formtarget) + '&id=' + str(askee.id) + '" target="viewer"><img src="/askees/' + askee.normpic +'" width=80 height=100 title="' + askee.name + '" border=0></a>'

		else:
			print '<a href="?op=display&id=' + str(askee.id) + '"><img src="/askees/' + askee.normpic +'" width=80 height=100 title="' + askee.name + '" border=0></a>'

		i = i + 1
		if i % 5 == 0: print "<br>"


def PrintStandardAskeeTable(askees):
	global mode
	
	AskeeLinkFunc = AskeeLink
	if mode == "browse":
		AskeeLinkFunc = AskeeBrowseLink

	if len(askees) == 0:
		print "No askees in list.<br>"
		return

	print "<table>"
	HtmlTableRow( ("<b>Name</b>", "<b>Short Cut</b>", "<b>Retired</b>") )
	
	for askee in askees:
		# strip out HTML. Bluh
		askee.name = re.sub("<[^<]*>", '', askee.name)
	
		# keep the name reasonable
		if 40 < len(askee.name):
			askee.name = askee.name[:40] + "..."
		
		strRetired = ""
		if askee.retired == 'y': strRetired = "<font size=1>(ret.)</font>"

		HtmlTableRow( (AskeeLinkFunc(askee), askee.shortname, strRetired) )
	
	print "</table>"
	
	
def PrintSearchForm():
	global mode
	global formtarget

	search = form.getvalue('search', '')

	print """<form method="get"><input type="hidden" name="op" value="search">""" % locals()

	print """
<input type=hidden name="mode" value="%s">
<input type=hidden name="formtarget" value="%s">
""" % (mode, formtarget)

	print """Search for an Askee: <input type='text' name='search' value="%s"> <input type='submit' value='Go'>""" % (search)

	print "<br>"
	
	print "<font size=1>Does a substring search in names, shortcuts, and category names.</font><br></form>"



def HtmlTableRow(cells):
	print "<tr>"
	for cell in cells:
		print "<td>%s</td>" % cell
	print "</tr>"


def AskeeLink(askee):
	return '<a href="?op=display&id=%(id)s">%(name)s</a>' % {'id': askee.id, 'name': askee.name}


def AskeeBrowseLink(askee):
	return '<a href="?op=bview&id=%(id)s&formtarget=%(formtarget)s" target="viewer">%(name)s</a>' % {'id': askee.id, 'name': askee.name, 'formtarget': formtarget}


def ExpandCategoryURL(category):
	global mode
	global formtarget
	
	modeStr=""
	if mode: modeStr = "&mode=%s" % mode
		
	formtargetStr = ""
	if formtarget:
		formtargetStr = "&formtarget=%s" % formtarget
	
	return "?expand=%(category)s%(modestr)s%(formtargetstr)s#%(category)s" % {'category': category.category, 'modestr': modeStr, 'formtargetstr': formtargetStr}


def HandleSearch():
	theme.PrintHeader('The Conversatron - Askee manager')
	theme.PrintNavBanner('Askee Manager - Search Results')
	
	PrintSearchForm()
	
	search = form.getvalue('search', '')
	
	askees = db.loadObjects("select id,name,shortname,askee.retired from askee where askee.name like '%%%(search)s%%' or askee.shortname like '%%%(search)s%%' order by name" % {'search': search})
	
	print "<b>Askees</b><br>"
	PrintStandardAskeeTable(askees)

		
	print "<br>"
	print "<b>Categories</b><br>"
	
	categories = db.loadObjects("select distinct category from askee where askee.category like '%%%(search)s%%' order by category" % {'search': search})

	if len(categories):
		for category in categories:
			print "<a href='%s'>%s</a><br>" % (ExpandCategoryURL(category), category.category)
	else:
		print "No categories found.<br>"
	
	theme.EndBox()
	theme.PrintFooter()


def HandleNormal():
	"Print the full askee list."
	
	global op

	theme.PrintHeader('The Conversatron - Askee manager', {'javascript': page_script, 'onload': 'setup_tree()'})
	theme.PrintNavBanner('Askee Manager')
	
	print "<br>"
	
	if user.usertype >= 3:
		print '[<a href="askeeman2.py?op=addform">Add New Askee</a>]<br>'

	PrintSearchForm()
	
	print "<div id='category-table'>"
	print "All Askees<br>"

	expandedCategory = form.getvalue('expand','').lower()
	expandAll = form.getvalue('expandall', 0)
	
	categories = ConvDB.GetAskeeCategories()
	
	for category in categories:
		# onclick="return expand('%(currcat)s');"
		print """[<a name="%(currcat)s" href="%(url)s">X</a>] <b>%(currcat)s</b><br><div style="margin-left:20px;" id="cat-%(quotecat)s" style="display:none" class="_">""" % {'url': ExpandCategoryURL(category), 'currcat': category.category, 'quotecat': urllib.quote(category.category), 'op': op}

		if expandAll or category.category.lower() == expandedCategory:
			askees = ConvDB.GetAskeesForCategory(category.category)			
			PrintStandardAskeeTable(askees)
			
		print "</div>"
			
	print "</div>"
	print "[<a href='askeeman2.py?expandall=1'>Expand All</a>]<br>"
	print "<font size=1>For the love of God, do <b>not</b> do this. Do a search instead, or browse by category.<br>While category browsing has been made much more efficient (DB-wise), showing everyone is now even <i>less</i> efficient.</font><br>"

	PrintNewestAskees()
		
	theme.PrintFooter()


def HandleDisplay():
	"Show an askee and bring up editing forms."

	theme.PrintHeader('The Conversatron - Askee manager')
	theme.PrintNavBanner('Askee Manager')
	
	categories = ConvDB.GetAskeeCategories()
		
	try:
		id = int(form["id"].value)
		askee = db.loadObject('select * from askee where id='+str(id))
		if askee == None:
			raise Exception
	except:
		print "Askee Unknown<br>"
		print '<a href="askeeman2.py">Back to Askee Manager</a>'
		theme.PrintFooter()
		web.quit()
	
	theme.StartBox('Info on '+askee.name, "#666699")
	
	if user.usertype >= 3:
		print '<form method="post" action="askeeman2.py" name="askee">'
		print '<input type="hidden" name="op" value="change">'
		print '<input type="hidden" name="id" value="'+str(askee.id)+'">'

	name = askee.name.replace('"', '&quot;') # string.replace(str(askee.name), '"', '&quot;')
	
	print '<table>'
	print '<tr><td>Name :</td><td><input name="name" type="text" maxlength=255 value="'+name+'"></td></tr>'

	print '<tr><td>Shortcut :</td><td><input name="shortname" type="text" maxlength=12 value="'+str(askee.shortname)+'"></td></tr>'

	print '<tr><td>Category :</td><td><input type="radio" name="radiocat" value="existing" checked> <select name="category" onchange="document.askee.radiocat[0].checked=true">'

	for category in categories:
		web.HtmlOption(category.category,category.category, askee.category==category.category )
	print '</select></td></tr>'

	print '<tr><td></td><td><input type="radio" name="radiocat" value="new"> <input name="newcategory" type="text" maxlength=32 value="'+str(askee.category)+'" onfocus="document.askee.radiocat[1].checked=true"></td></tr>'


	print '<tr><td></td><td>[<a href="'+ ExpandCategoryURL(askee) +'">view cateogry</a>]</td></tr>'

	print '</table><br>'
	
	print '*Do <b>NOT</b> leave with any broken images here!!<br>'
	print '<table border><tr><td> NormPic : <input name="normpic" type="text" maxlength=255 value="'+str(askee.normpic)+'"><br>'
	print '<img src="/askees/' + askee.normpic +'" width=80 height=100></td>'
	print '<td>HappyPic : <input name="happypic" type="text" maxlength=255 value="'+str(askee.happypic)+'"><br>'
	print '<img src="/askees/' + askee.happypic +'" width=80 height=100></td><tr>'
	print '<td>AngryPic : <input name="angrypic" type="text" maxlength=255 value="'+str(askee.angrypic)+'"><br>'
	print '<img src="/askees/' + askee.angrypic +'" width=80 height=100></td>'
	print '<td>SadPic : <input name="sadpic" type="text" maxlength=255 value="'+str(askee.sadpic)+'"><br>'
	print '<img src="/askees/' + askee.sadpic +'" width=80 height=100></td></tr></table>'
	
	if askee.url == None or askee.url == "":
		print '<br>URL : <input name="url" type="text" size=64 maxlength=255><br>'
	else:
		print '<br>URL : <input name="url" type="text" value="'+str(askee.url)+'" size=64 maxlength=255><br>'
	

	if user.usertype >= 3:
		print '<br><input type="submit" value="Change"></form><br>'
		
		print '<br><a href="askeeman2.py?op=retire&id='+str(askee.id)+'">'
		if askee.retired == 'n':
			print 'Retire this askee</a><br>'
		else:
			print 'Unretire this askee</a><br>'
			
		print '<br><a href="fileman.html" target="_blank">Open file browser</a><br>'
		
	
	print '<br><a href="askeeman2.py">Back to Askee Manager</a>'
	
	theme.EndBox()
	theme.PrintFooter()


def HandleChange():
	"Change the details of an askee based on the form."

	
	try:
		id = int(form["id"].value)
		askee = db.loadObject('select * from askee where id='+str(id))
		if askee == None:
			raise Exception
	except:
		theme.PrintHeader('The Conversatron - Askee manager')
		theme.StartErrorBox("Askee Unknown")
		print '<br><a href="askeeman.py">Back to Askee Manager</a>'
		theme.EndErrorBox()
		theme.PrintFooter()
		web.quit()

	oldcut = askee.shortname

	try:
		askee.name = form["name"].value
		askee.shortname = form["shortname"].value
		
		if form.getvalue('radiocat','') == 'existing':
			askee.category = form["category"].value
		else:
			askee.category = form["newcategory"].value
		
		askee.normpic = form["normpic"].value
		askee.happypic = form["happypic"].value
		askee.angrypic = form["angrypic"].value
		askee.sadpic = form["sadpic"].value
	except:
		theme.PrintHeader('The Conversatron - Askee manager')
		theme.StartErrorBox("Whoa there guy!")
		
		print "Don't leave any fields blank, chump!"
		
		theme.EndErrorBox()
		theme.PrintFooter()
		web.quit()
	
	askee.url = ''
	try:
		askee.url = form["url"].value
	except:
		pass
	
	if oldcut != askee.shortname:
		cid = ConvDB.AskeeShortcutToID(askee.shortname)
		if cid:
			theme.PrintHeader('The Conversatron - Askee manager')
			theme.StartErrorBox('Namespace error!')
			
			print "That shortcut is already taken. Choose another."
			
			theme.EndErrorBox()
			theme.PrintFooter()
			web.quit()
		
	db.updateObject('askee', askee, 'id='+str(askee.id))
	web.RedirectInFolder('/askeeman2.py?op=display&id='+str(id))


def HandleAddForm():
	"Print the add askee form."
	
	theme.PrintHeader('The Conversatron - Askee manager')
	theme.PrintNavBanner('Askee Manager')
	
	theme.StartBox("Add New Askee", "#666699")
	
	categories = ConvDB.GetAskeeCategories()

	
	print '<form method="post" name="askee">'
	print """
<script>
function copy_normal()
{
	t = document.askee.normpic.value;
	document.askee.angrypic.value = t;
	document.askee.sadpic.value = t;
	document.askee.happypic.value = t;
}
</script>
"""
	print '<input type="hidden" name="op" value="add">'
	print '<table>'
	print '<tr><td>Name :</td><td><input name="name" type="text" maxlength=255></td></tr>'
	print '<tr><td>Shortcut :</td><td><input name="shortname" type="text" maxlength=12></td></tr>'

	print '<tr><td>Category :</td><td><input type="radio" name="radiocat" value="existing" checked> <select name="category" onchange="document.askee.radiocat[0].checked=true">'

	for category in categories:
		web.HtmlOption(category.category,category.category)
	print '</select></td></tr>'

	print '<tr><td></td><td><input type="radio" name="radiocat" value="new"> <input name="newcategory" type="text" maxlength=32 value="" onfocus="document.askee.radiocat[1].checked=true"></td></tr>'

	print '<tr><td colspan=2><hr noshade></td></tr>'
	print '<tr><td>NormPic :</td><td><input name="normpic" type="text" maxlength=255> <input type="button" name="dupe" value="Use for all" onclick="copy_normal()"></td></tr>'
	print '<tr><td>HappyPic :</td><td><input name="happypic" type="text" maxlength=255></td></tr>'
	print '<tr><td>AngryPic :</td><td><input name="angrypic" type="text" maxlength=255></td></tr>'
	print '<tr><td>SadPic :</td><td><input name="sadpic" type="text" maxlength=255></td></tr>'
	print '<tr><td>URL :</td><td><input name="url" type="text" size=64 maxlength=255></td></tr>'
	print '</table>'
	
	print '<input type="submit" value="Add"></form><br><br>'
	
	print '<a href="fileman.html" target="window">Open file browser</a><br>'
	print '<br><a href="askeeman2.py">Back to Askee Manager</a>'
	
	theme.EndBox()
	theme.PrintFooter()


def HandleAdd():
	"Add an askee from form data."
	
	askee = SuperHash()
	try:
		askee.name = form["name"].value
		askee.shortname = form["shortname"].value
		
		if form.getvalue('radiocat','') == 'existing':
			askee.category = form["category"].value
		else:
			askee.category = form["newcategory"].value

		askee.normpic = string.strip(form["normpic"].value)
		askee.happypic = string.strip(form["happypic"].value)
		askee.angrypic = string.strip(form["angrypic"].value)
		askee.sadpic = string.strip(form["sadpic"].value)
	except:
		theme.PrintHeader('The Conversatron - Askee manager')
		theme.StartErrorBox("Input Error")
		
		print "Don't leave any fields blank, chump!<br>"
		
		theme.EndBox()
		theme.PrintFooter()
		web.quit()
	
	try:
		askee.url = form["url"].value
	except:

		pass
	
	id = ConvDB.AskeeShortcutToID(askee.shortname)
	if id:
		theme.PrintHeader('The Conversatron - Askee manager')
		theme.StartErrorBox("Namespace error")
		
		print "That shortcut is already taken. Choose another."
		
		theme.EndErrorBox()
		theme.PrintFooter()
		web.quit()
	
	db.storeObject('askee', askee)
	num = ConvDB.AskeeShortcutToID(askee.shortname)
	web.RedirectInFolder('?op=display&id='+str(num))
	


def HandleBrowseView():
	"Show just the picture for the browse thing."
	
	if not form.getvalue('id'):
		print 'Content-type: text/html\n'
		print "<html><body>Select an askee to view images.</body></html>"
	
		web.quit()
	
	try:
		id = int(form["id"].value)
		askee = db.loadRow('askee', id)#db.loadObject('select * from askee where id='+str(id))
		if askee == None:
			raise Exception
	except:
		web.quit()
		
	global formtarget
	formid = formtarget
	shortname = askee.shortname

	print 'Content-type: text/html\n'

	print """	
<html>
<head>
<title>Askee Browser</title>

<script>
function SelectAskee(emotion)
{
	theform = top.opener.document.reply
	
	theform.shortname%(formid)s.value='%(shortname)s'
	theform.askee%(formid)s.selectedIndex=0
	theform.emotion%(formid)s.selectedIndex=emotion
	
	top.window.close()
}
</script>
</head>

<body>
""" % locals()
	
	print '<table><tr><td>Normal</td><td>Happy</td><td>Angry</td><td>Sad</td></tr><tr>'

	print '''<td><a href="#" onclick="SelectAskee(0);return void(0)"><img src="/askees/''' + askee.normpic +'''" width=80 height=100></a></td>'''

	print '''<td><a href="#" onclick="SelectAskee(1);return void(0)"><img src="/askees/''' + askee.happypic +'''" width=80 height=100></a></td>'''

	print '''<td><a href="#" onclick="SelectAskee(2);return void(0)"><img src="/askees/''' + askee.angrypic +'''" width=80 height=100></a></td>'''

	print '''<td><a href="#" onclick="SelectAskee(3);return void(0)"><img src="/askees/''' + askee.sadpic +'''" width=80 height=100></a></td>'''

	print '</tr></table>'		
	print '</body></html>'


def HandleRetire():
	"Toggle retired status of an askee."
	
	try:
		id = int(form["id"].value)
		askee = db.loadObject('select * from askee where id='+str(id))
		if askee == None:
			raise Exception
	except:
		theme.PrintHeader('The Conversatron - Retired Askees')
		theme.StartErrorBox("Askee Unknown")
		print '<br><a href="">Back to Askee Manager</a>'
		theme.EndErrorBox()
		theme.PrintFooter()
		web.quit()
	
	if askee.retired == 'n':
		askee.retired = 'y'
	else:
		askee.retired = 'n'
	
	db.updateObject('askee', askee, 'id='+str(askee.id))
	web.RedirectInFolder('?op=display&id='+str(id))


def HandleFrameset():
	global mode
	global formtarget

	print "Content-type: text/html\n"
	print """<html>
<head>
<title>The Conversatron - Askee Browser</title>
</head>
<frameset rows="*,140">
<frame name="main" src="askeeman2.py?op=main&mode=%(mode)s&formtarget=%(formtarget)s">
<frame name="viewer" src="askeeman2.py?op=bview" noresize>
</frameset>

</html>""" % globals()


# ------- begin ----------
theme = themes.LoadTheme()

op = form.getvalue('op', 'main')
mode = form.getvalue('mode', None)
formtarget = form.getvalue('formtarget', None)

adminOps = ["change", "addform", "add", "retire"]

if op in adminOps:
	if user.usertype < 3:
		web.GoHome()
else:
	if user.usertype < 2:
		web.GoHome()

optable = {
	"main": HandleNormal,

	"frameset": HandleFrameset,
	"bview": HandleBrowseView,

	"display": HandleDisplay,

	"change": HandleChange,

	"addform": HandleAddForm,
	"add": HandleAdd,

	"retire": HandleRetire,
	"search": HandleSearch,
	
	"node": HandleNode,
	}

func = optable.get(op, None)
if func:
	func()
else:
	print "Content-type: text/html\n"
	print "Unknown operation '" + op + "'."
