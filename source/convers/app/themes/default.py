import time
import urllib
import ConfigParser

import Template
import stars
import web
	
from StandardVars import *

import re
import os.path

Weekdays = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

star_icons = {
	'gold_star': '<img src="/img/gs.gif" width=12 height=12 alt="Gold">',
	'silver_star': '<img src="/img/ss.gif" width=12 height=12 alt="Silver">',
	'bronze_star': '<img src="/img/bs.gif" width=12 height=12 alt="Bronze">',
	}


# Factory method to create theme instances
def MakeThemeObject(name = None):
	if name == "val":
		return BasicTheme("val.ini")
	else:
		return BasicTheme()

	
class BasicTheme:
	def __str__(self):
		return "A Conversatron theme (" + self.__class__.__name__ + ")"

	def __init__(self, settings_file = None, theme_file = None):
		if settings_file is None:
			settings_file = "default.ini"
			
		if settings_file.startswith("*"):
			settings_file = 'user_themes' + settings_file[1:]
		else:
			settings_file = os.path.dirname(__file__) + '/' + settings_file
	
		config = ConfigParser.ConfigParser()
		config.read([settings_file])
	
		self.settings = {}
		for key in  config.options('theme'):
			self.settings[key] = config.get('theme', key)
			
		self.settings['homepage'] = web.HomePage()
		self.settings['currentyear'] = time.localtime(time.time())[0]

		self.templates = Template.Manager()
		
		template_files = [os.path.dirname(__file__) +'/default.xml']
		
		if theme_file != None: 
			if theme_file.startswith("*"):
				theme_file = 'user_themes' + theme_file[1:]
			else:
				theme_file = os.path.dirname(__file__) + '/' + theme_file
				
			template_files.append(theme_file)
		
		self.templates.add_files(template_files)		
		self.debug=True

	
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
	
		self.templates.display('index', data, self.debug)

	# ----- <head> links
	def PrintHeadLinks(self):
		print "<!-- Page specific links -->"
		# Try to print page specific links, but don't cry
		# if the page doesn't define that method.
		try:
			self.page.PrintHeadLinks()
		except NameError, e:
			pass
	
	# ----- Home Page Links
	def PrintLinks(self):
		if user.IsWriter():
			if self.page.pending:
				print '<a href="/mans/threads.py">Inbox: '+str(self.page.pending)+'</a> . . . '
			if self.page.intrash:
				print '<a href="/mans/threads.py?op=listdel">Trash: '+str(self.page.intrash)+'</a> . . . '
			print '<a href="/xyzzy/writerlinks.html">Writer Links</a><br>'
			
			print '<a href="/mans/askees.py">Askees</a> '
			if user.IsAdmin():
				print ' . . . <a href="/mans/askees.py?op=addform">Add Askee</a> . . . <a href="/mans/users.py">Users</a> . . . <a href="/mans/files.py">Files</a> . . . <a href="/mans/slogans.py">Slogans</a>'

			print '<br>'

		if user.IsGuest():
			print '<div id="login_links"><a href="/account/signin.py" onclick="return showSignIn()">Sign in</a> or <a href="/account/create.py">Create an account</a></div>'
			
			self.templates.display('inline-sign-in', {}, self.debug)

		print '<a href="/htmldocs/about.html">Introduction</a> &amp; <a href="/htmldocs/faq.html">FAQ</a> . . . <a href="/archive/">Archives</a> . . . <a href="/htmldocs/links.html">Flotsam</a> . . . <a href="source/">The Source</a>'
		
		if user.IsRegistered():
			if user.IsWriter():
				print ' . . . '
			else:
				print '<br>'
			print '%s: <a href="/account/settings.py">Settings</a> . . . <a href="/account/signout.py">Sign out</a>' % (user.name,)
			
		print '<br>'

	
	# ----- Home Page thread list
	def PrintThreads(self):
		odd = 1
		curday = None
		for row in self.page.threads:
			if curday != None and curday != int(row.yearday):
				data = {'day': Weekdays[int(row.weekday)]}
				data.update(self.settings)
				
				self.templates.display('index_date', data, self.debug)
	
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
			self.templates.display('index_thread', data, self.debug)
		

	# -----
	# ----- Topic Page
	# -----
	def PrintThread(self, page, archindex=None):		
		self.page = page
		
		thread_subject = page.thread.subject
		thread_subject = re.sub(r"(<[^>]*>)", '', thread_subject)
		
		data = {}
		data.update(self.settings)

		try:
			data['javascript'] = self.page.javascript
		except: pass

		data['title'] = self.settings.get('site_name',"The Conversatron") + ' - ' + thread_subject
				
		data['user'] = user
		data['page'] = page
		data['theme'] = self
		
		data['archindex'] = archindex
		
		if archindex == None:
			data['minilogourl'] = '/'
		else:
			data['minilogourl'] = "/archive/archives"+str(archindex)+".html"

		
		self.templates.display('topic', data, self.debug);

	def EntryRefresh(self): 
		last_oid = self.page.thread.entries[-1].oid
		print """<script>"""
		print """last_oid=%s;""" % last_oid
		print """function url(){
		return "http://conversatron.dev/topicutil.py?op=newposts&topic=%s&oid=" + last_oid;
}""" % (self.page.thread.id)
		print """
function get_done(get){
	if (get.readyState != ReadyState.Complete) return;	
	if (get.status != HttpStatus.OK) return;
	
	var props = getResponseProps(get)
	var js = get.responseText;
	if (js)
	{
		last_oid = props.entry;
		var html = "<a name='" + last_oid.toString() + "'></a><div id='" + last_oid.toString() + "'>" + js + "</div>";
		DOM.before('new-posts', html);

		new Effect.Appear(last_oid.toString()).fade();
		
	}
	else
	{
		Display.text('new-posts', "<span id='message'>No new posts.</span>");
		(new Effect.Appear("new-posts")).fade();
	}
		
	Display.enable('refresh-entries')
}

function get_new_posts(button){
	Display.disable(button)
	Display.hide('new-posts')
	var request = new Request()
	request.GetNoCache(url(), get_done)
	return false;
}
</script>
<div id="new-posts"></div>
<form style="display:inline">
<input type="button" class="action"  id="refresh-entries" name="refresh-entries" value="Check for new posts" onclick="return get_new_posts(this)"/>
</form>
"""
		
	def PrintThreadEntries(self):
		listlen = len(self.page.thread.entries)
		try:
			if self.page.anyErrors:
				print '<font color="red"><a href="#writers">There were errors in your post</a>. Please fix them and re-post.</font><br><br>'
		except: pass

		for num in range(listlen):
			item = self.page.thread.entries[num]
			item._num = num
			item._count = listlen
			self.PrintEntry(item)
	
			if (num == 0) and (listlen > 1):
				data = {}
				data.update(self.settings)
				
				self.templates.display('entry_responses', data, self.debug)


	def PrintEntry(self, entry):
		data = {}
		data.update(self.settings)
		
		data['isfirst'] = (entry._num == 0)
		data['islast'] = (entry._num == entry._count - 1)
		
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
#				image = '/users/asker.gif'
				image = '/users/user2.jpg'
			
			data['image'] = image
			data['name'] = entry.uname
			data['namecolor'] = self.settings.get('entry_askercolor', '#ffffff')
		else:
			data['image'] = '/users/user2.jpg'
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
	
		self.templates.display(entrytempl, data, self.debug)


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
		

	def PrintHeader(self, title, more_data=None):
		"Standard header for all dynamic pages"
		
		print 'Pragma: no-cache'
		print 'Content-type: text/html\n'
		
		data = {'title': title}
		data.update(self.settings)
		
		if more_data is not None: data.update(more_data)
		
		self.templates.display('standard_head', data, self.debug)


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
		
	
	def ErrorPage(self, pagename, title, errortext):
		self.PrintHeader('The Conversatron - %s' % pagename)
		self.StartErrorBox(title)
		print errortext
		self.EndBox()
		self.PrintFooter()				
		web.quit()


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
