from themes.default import BasicTheme
from StandardVars import *


# Factory method to create theme instances
def MakeThemeObject(name = None):
	return TrendwhoreTheme()		

		
class TrendwhoreTheme(BasicTheme):
	def __init__(self,  settings_file = "themes/trendwhore.ini", theme_file = "themes/trendwhore.xml"):
		BasicTheme.__init__(self, settings_file, theme_file)


	
	# ----- Home Page Links
	def PrintLinks(self):
		if user.usertype == 0:
			print """
<a href="login.py?op=create"><img src="/img/trendwhore/createaccount.gif" border="0" alt="Create Account"></a>
<img src="/img/trendwhore/command_spacer.gif" width="22" height="30" alt=" .:. ">
<a href="login.py"><img src="/img/trendwhore/signin.gif" border="0" alt="Sign in"></a><br>"""

		print """
<a href="about.html"><img src="/img/trendwhore/introduction.gif" border="0" alt="Introduction"></a>
<img src="/img/trendwhore/command_spacer.gif" width="22" height="30" alt=" .:. ">
<a href="faq.html"><img src="/img/trendwhore/faq.gif" border="0" alt="FAQ"></a>
<img src="/img/trendwhore/command_spacer.gif" width="22" height="30" alt=" .:. ">
<a href="archive/"><img src="/img/trendwhore/archives.gif" border="0" alt="Archives"></a>
<img src="/img/trendwhore/command_spacer.gif" width="22" height="30" alt=" .:. ">
<a href="links.html"><img src="/img/trendwhore/links.gif" border="0" alt="Links"></a>"""

		if user.usertype != 0:
			print """
<img src="/img/trendwhore/command_spacer.gif" width="22" height="30" alt=" .:. ">
<a href="prefs.py"><img src="/img/trendwhore/settings.gif" border="0" alt="Settings"></a>
<img src="/img/trendwhore/command_spacer.gif" width="22" height="30" alt=" .:. ">
<a href="login.py?op=logout"><img src="/img/trendwhore/logout.gif" border="0" alt="Logout"></a><br>"""		

		if user.usertype >= 2:
			if self.page.pending:
				print '<a href="threadman.py">Inbox: '+str(self.page.pending)+'</a> . . . '
			if self.page.intrash:
				print '<a href="threadman.py?op=listdel">Trash: '+str(self.page.intrash)+'</a> . . . '
			print '<a href="/xyzzy/handbook.html">Writer\'s Handbook</a> . . . <a href="/xyzzy/steve.html">Steve\'s Rants</a> . . . <a href="/xyzzy/jeremy.html">Jeremy\'s Rants</a><br>'
		
		if user.usertype >= 3:
			print '<a href="askeeman.py?op=addform">Add askee</a> . . . <a href="askeeman.py">Askees</a> . . . <a href="userman.py">Users</a> . . . <a href="fileman.py">Files</a> . . . <a href="sloganman.py">Slogans</a><br>'

		if user.usertype >= 2:
			print 'Askee Manager II: <a href="askeeman2.py">Electric Boogaloo</a> (beta)<br><br>'


	def StartBox(self,title, color=None, width=None, intcolor="#FFFFFF", padding=4):
		print """<table width="80%" align="center" border="0" bgcolor="#26354F" cellspacing="0" cellpadding="3"><tr><td>
          <table width="100%" cellspacing="0" cellpadding="4">
            <tr><td class="header">""" + title + """</td></tr>
            <tr class="even">
              <td>
                <div align="center">"""
                
	def EndBox(self):
		print """</div>
              </td>
            </tr>
          </table>
        </td></tr></table>"""