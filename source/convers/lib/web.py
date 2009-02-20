import sys
import os
import os.path
import re
import cgi
"""
Helper functions for doing web apps.

Combines a bunch of HTTP and HTML crap.
"""

# ----- The standard HTTP header
def header(contenttype = None):
	if not contenttype: contenttype = "text/html"
	print "Content-type: " + contenttype + "\n"
	
	
def js_onclick_confirm(message):
	js = """onclick="return(confirm('%s'));\""""
	return js % cgi.escape(message)


# ----- Redirect browser to a new URL
# If no server name is given, redirect to URL on current server
def Redirect(url):
	if url[:4] != 'http':
		servername = os.environ.get('HTTP_HOST', "http://conversatron.com")
		
		if url[0] == '/':
			slash = ""
		else:
			slash = "/"
		
		url = 'http://' + servername + slash + url
		
	print 'Location: ' + url + '\n'
	
	
def ReInFolder(page, querystring=None, **kw):
	new_url = os.path.dirname(os.environ['SCRIPT_URL']) + '/' + page
	
	if querystring is not None:
		new_url = new_url + "?" + querystring
		
	Redirect(new_url)
	pass
	
def RedirectToSelf(querystring=None):
#SCRIPT_URL:	/foo/nuts.py
#REQUEST_URI:	/foo/nuts.py?string=cheese

	new_url = os.environ['SCRIPT_URL']
	if querystring is not None:
		new_url = new_url + "?" + querystring
	Redirect(new_url)
	pass

# ----- Redirect browser to a new page in the current folder
# It only gets the current folder one slash-level deep
def RedirectInFolder(pagename):
	base = HomeFolder(pagename)
		
	print 'Location: ' + base + '\n'
	

# ----- Redirect the browser to the homepage and stop processing
def GoHome():
	print 'Location: ' + HomeFolder('/index.py') + '\n'
	quit()


def RedirectToThread(thread):
	RedirectInFolder('/convers.py?topic='+str(thread.id)+'&count='+str(thread.count))
	quit()

# ----- Construct a full URL to the given filename in the 'current' folder
def HomePage(): return HomeFolder("/index.py")

def HomeFolder(filename = ""):
	try:
		base = os.environ['REQUEST_URI']
		slash = '/'.find(base,1) # string.find(base, "/", 1)
		if slash >= 0:
			base = base[0:slash]
		else:
			base = ""
	except:
		base = ""
		
	servername = os.environ.get('HTTP_HOST', "conversatron.com")
	
	if filename[0] == '/':
		strslash = ""
	else:
		strslash = "/"
		
	return 'http://' + servername + base + strslash + filename



# ----- Dump the contents of the given filename to the browser
def IncludeFile(filename):
	"Load a text file and print it out"

	f = open(filename, 'r')
	buffer = f.read()
	f.close()

	print buffer



# ------ Quit the script
def quit():
	sys.exit()


# ------ String Manipulation
def StripTags(text):
	text = re.sub(r"(<[^>]*>)", '', text)
	return text


def StripNewlines(text):
	"Remove all newline characters from a blob of text."
	
	text = text.replace('\015','').replace('\012','')
	return text
	

def NewlinestoBR(text):
	"Turn newlines into <br>"

	# Newlines from HTML forms SHOULD always be \015\012, but you never know	
	text = text.replace('\015\012','<br>')
	text = text.replace('\012','<br>')
	text = text.replace('\015','<br>')	
	return text


def SanitizeHTML(text, quote=0):
	"Escape any HTML elements."
	return cgi.escape(text,quote)	
	

# ----- Show a favorites dropdown list
def HtmlOption(name, value, isSelected=0):
	if isSelected:
		selected = " selected "
	else:
		selected = ""

	print '<option value="%s"%s>%s' % (value, selected, name)
	

def HtmlSelect(list, name, selection=''):
	selection = str(selection)
	print '<select name="'+name+'">'
	if list:
		for item in list:
			HtmlOption(item[0], item[1], selection == str(item[1]))
	print '</select>'
	

def PrintFavoriteSelector(list, name, selection=None):
	print '<select name="'+name+'"><option value="0">Select an Askee...'
	if list:
		for guy in list:
			HtmlOption(guy.name, guy.id, selection == str(guy.id))
	print '</select>'


# ----- Form handling stuff
def hasPostData():
	return os.environ["REQUEST_METHOD"] == "POST" and 0 < int(os.environ.get("CONTENT_LENGTH",0))
