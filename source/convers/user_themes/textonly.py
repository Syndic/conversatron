import time
import urllib
import ConfigParser

import Template
import stars
import web
	
from StandardVars import *


Weekdays = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

star_icons = {
	'gold_star': ' (Gold star)',
	'silver_star': ' (Silver star)',
	'bronze_star': ' (Bronze star)',
	}


# Factory method to create theme instances
def MakeThemeObject(name = None):
	return BasicTheme()

	
class BasicTheme:
	def __str__(self):
		return "A Conversatron theme (" + self.__class__.__name__ + ")"

	def __init__(self, settings_file = "themes/textonly.ini", theme_file = None):
		config = ConfigParser.ConfigParser()
		config.read([settings_file])
	
		self.settings = {}
		for key in  config.options('theme'):
			self.settings[key] = config.get('theme', key)
			
		self.settings['homepage'] = web.HomePage()
		self.settings['currentyear'] = time.localtime(time.time())[0]

		self.templates = Template.Manager()
		
		template_files = ['themes/textonly.xml']
		if theme_file != None: template_files.append(theme_file)
		
		self.templates.add_files(template_files)

	
	# -----
	# ----- Home Page
	# -----	
	def PrintIndex(self, page):
		data = {}
		
		data['title'] = self.settings['site_name']
		
		data['slogan'] = page.slogan
				
		data['page'] = page
		data['user'] = user
		data['theme'] = self

		data.update(self.settings)

		
		self.page = page
	
		print 'Content-type: text/html\n'
		self.templates.display('index', data, 0)
	
	
	# ----- Home Page Links
	def PrintLinks(self):
		if user.usertype >= 2:
			if self.page.pending:
				print '<a href="threadman.py">Inbox: '+str(self.page.pending)+'</a> . . . '
			if self.page.intrash:
				print '<a href="threadman.py?op=listdel">Trash: '+str(self.page.intrash)+'</a> . . . '
			print '<a href="/xyzzy/writerlinks.html">Writer Links</a><br>'

		print '<a href="/about.html">Introduction</a> . . . <a href="/faq.html">FAQ</a> . . . <a href="/archive/">Archives</a> . . . <a href="links.html">Links</a>'

		print ''' . . . Bars: <a href="/iebar.py?browser=ie" target="_search">IE</a> / <a href="#nowhere" onclick="window.sidebar.addPanel('ConversaBar', 'http://conversatron.com/iebar.py?browser=moz', '');">Moz</a>'''
		
		if user.usertype == 0:
			print ' . . . <a href="login.py">Sign in</a> . . . <a href="login.py?op=create">Create account</a><br>'
		else:
			print ' . . . <a href="prefs.py">Settings</a> . . . <a href="login.py?op=logout">Logout</a><br>'
		
		
		if user.usertype >= 2:
			print '<a href="askeeman2.py">Askees</a> '

		if user.usertype >= 3:
			print ' . . . <a href="askeeman2.py?op=addform">Add Askee</a> . . . <a href="userman.py">Users</a> . . . <a href="fileman.py">Files</a> . . . <a href="sloganman.py">Slogans</a>'

		if user.usertype >= 2:
			print '<br>'

	
	# ----- Home Page thread list
	def PrintThreads(self):
		odd = 1
		curday = None
		for row in self.page.threads:
			if curday != None and curday != int(row.yearday):
				data = {'day': Weekdays[int(row.weekday)]}
				data.update(self.settings)
				
				self.templates.display('index_date', data)
	
			curday = int(row.yearday)
			
			# If we get a non-empty string for star, then it's the name of a template to use for the image
			star = self.StarHtml(row)

			if odd:
				color = self.settings.get('home_oddcolor', '')
			else:
				color = self.settings.get('home_evencolor', '')

			odd = not odd
			
			data = {}
			data.update(self.settings)

			followup = ""
			archive = ""
			
			if user.usertype > 1:
				if row.followup == 'y':
					followup = self.settings.get('followupicon', '')
				if row.archive == 'y':
					archive = self.settings.get('archiveicon', '')
		
			data.update({'row': row, 'star': star, 'user': user, 'rowcolor': color, "archive": archive, "followup": followup})
			self.templates.display('index_thread', data)
		

	# -----
	# ----- Topic Page
	# -----
	def PrintThread(self, page, archindex=None):
		if archindex == None:
			print 'Pragma: no-cache'
			print 'Content-type: text/html\n'
		
		self.page = page
		
		data = {}
		data.update(self.settings)

		data['title'] = self.settings.get('site_name',"The Conversatron") + ' - ' + page.thread.subject
				
		data['user'] = user
		data['page'] = page
		data['theme'] = self
		
		data['archindex'] = archindex
		
		if archindex == None:
			data['minilogourl'] = web.HomePage()
		else:
			data['minilogourl'] = "/archive/archives"+str(archindex)+".html"

		
		self.templates.display('topic', data, 2);
		

	def PrintThreadEntries(self):
		listlen = len(self.page.entries)
		
		try:
			if self.page.anyErrors:
				print '<font color="red"><a href="#writers">There were errors in your post</a>. Please fix them and re-post.</font><br><br>'
		except: pass

		for num in range(listlen):
			item = self.page.entries[num]
			item._num = num
			self.PrintEntry(item)
	
			if (num == 0) and (listlen > 1):
				data = {}
				data.update(self.settings)
				
				self.templates.display('entry_responses', data)


	def PrintEntry(self, entry):
		data = {}
		data.update(self.settings)
		
		data['isfirst'] = entry._num == 0
		
		bgcolor = self.settings.get('entry_normal', '#ffffff')
		
		if entry.aname:
			if entry.emotion == 'h':
				image = entry.happypic
				bgcolor = self.settings.get('entry_happy', bgcolor)
				
			elif entry.emotion == 'a':
				image = entry.angrypic
				bgcolor = self.settings.get('entry_angry', bgcolor)
				
			elif entry.emotion == 's':
				image = entry.sadpic
				bgcolor = self.settings.get('entry_sad', bgcolor)
				
			else:
				image = entry.normpic
				
				
			data['image'] = "/askees/"+image
			data['name'] = entry.aname
			data['namecolor'] = self.settings.get('entry_askeecolor', '#ffffff')
			
		elif entry.uname:
			if entry.picture:
				image = "/users/"+entry.picture
			elif entry.gender == 'm':
				image = "/users/asker-m.gif"
			elif entry.gender == 'f':
				image = "/users/asker-f.gif"
			elif entry.gender == 't':
				image = "/users/green-toilet.gif"
			else:
				image = '/users/asker.gif'
	
			data['image'] = image
			data['name'] = entry.uname
			data['namecolor'] = self.settings.get('entry_askercolor', '#ffffff')
		else:
			data['image'] = '/users/asker.gif'
			data['name'] = "The Asker"
			data['namecolor'] = self.settings.get('entry_askercolor', '#ffffff')


		if entry.side == 'l':
			data['side'] = 'left'
		else:
			data['side'] = 'right'
				
		data['color'] = bgcolor
		data['text'] = entry.body	
			
		
		if entry.url:
			data['urlstart'] = '<a href="' + entry.url + '">'
			data['urlstop'] = '</a>'
		else:
			data['urlstart']=''
			data['urlstop']=''
	
		
		if user.usertype > 1:
			data['userIDStr'] = UserIDHTML(entry)
			data['buttonStr'] = EditEntryHTML(entry)		
		else:
			data['userIDStr'] = ""
			data['buttonStr'] = ""
					
		if entry.side == 'l':
			entrytempl = self.settings.get('entryleft', 'entry')
		else:
			entrytempl = self.settings.get('entryright', 'entry')

		# Override some stuff for follow-up posts			
		if entry.flag=="s":
			data['color'] = self.settings.get('entry_ghost',"#cccccc")
			data['textcolor'] = self.settings.get('entry_ghosttext', '#333333') 
	
		self.templates.display(entrytempl, data)


	def StartBox(self,title, color=None, width=None, intcolor="#FFFFFF", padding=4):
		"Start a colored group box"
		
		if color == None: color = self.settings.get('ucolor','')
		
		if width:
			print '<table width="'+str(width)+'" border=0 cellpadding='+str(padding)+' cellspacing=0>'
		else:
			print '<table border=0 cellpadding='+str(padding)+' cellspacing=0>'
		print '<tr><td align=center><font size="4">'+title+'</font></td></tr>'
		print '<tr><td>'
	
	
	def EndBox(self,):
		print '</td></tr></table>'



	def PrintHeader(self, title):
		"Standard header for all dynamic pages"
		
		print 'Pragma: no-cache'
		print 'Content-type: text/html\n'
		
		data = {'title': title}
		data.update(self.settings)
		
		self.templates.display('standard_head', data)


	def PrintFooter(self):
		print '</body></html>'

	def PrintNavBanner(self,title):
		"Print out a page header that lets you click back to the main page"
		
		print '<a href="' + web.HomePage() + '">'+self.settings['minilogo']+'</a><font size="+2">'+title+'</font><br clear="all">'


	def StartErrorBox(self, title, width="50%"):
		print '<table width="100%"><tr><td align="center">'
		self.StartBox(title, None, width)
		
	def EndErrorBox(self):
		self.EndBox()
		print '</td></tr></table>'
	
	def StartUserBox(self, title, width="60%"):
		self.StartBox(title, None, width)
		
	def EndUserBox(self):
		self.EndBox()


	def PrintArchiveHeader(self, title):
		"Standard header for all dynamic pages"
		
		print '<html><head><title>'+title+'</title>'
		print '</head><body bgcolor="' + self.settings['bgcolor'] + '">'
		
		
	def StarHtml(self, thread):
		return stars.GetStarHtml(thread)


# ----- HTML for the writer edit buttons on a thread entry
def EditEntryHTML(entry):
	buttonStr = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(' + entry.time + ')&nbsp;[<a href="entry.py?id='+str(entry.id)+'">edit</a>]&nbsp;'

	if entry.previd:
		buttonStr = buttonStr + ' [<a href="entry.py?op=swap&id='+str(entry.id)+'&sid='+str(entry.previd)+'">up</a>]&nbsp;'
		
	if entry.nextid:
		buttonStr = buttonStr + ' [<a href="entry.py?op=swap&id='+str(entry.id)+'&sid='+str(entry.nextid)+'">down</a>]&nbsp;'
	
	if entry.flag=="s":
		buttonStr = buttonStr + ' [<a href="entry.py?id='+str(entry.id)+'&op=activate">activate</a>]&nbsp;'
		buttonStr = buttonStr + ' [<a  href="entry.py?id='+str(entry.id)+'&op=delete">kill</a>]&nbsp;'

	return buttonStr
	

# ----- HTML for the user ID string that a writer sees	
def UserIDHTML(entry):
	if entry.uname:
		poster = '<a href="userman.py?op=lookup&name=' + urllib.quote_plus(entry.uname) + '">'+entry.uname+'</a>'
	else:
		poster = 'guest'
		
	IP = '<a href="resolve.py?addr='+urllib.quote_plus(entry.addr)+'" target="window">['+entry.addr+']</a>'

	browser = entry.client

	return '<font size="-1">Posted by ' + poster + ' at '+ IP + ' using ' + browser + '.</font>'

