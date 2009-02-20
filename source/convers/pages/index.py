#!/usr/bin/env python
# The Main Conversatron Page. OOOOohh baby!

from StandardVars import *
import ConvDB
from BasicPage import BasicPage
import web

import themes


class HomePage(BasicPage):
	def __init__(self):
		BasicPage.__init__(self)
	
		theme_name = form.getvalue('_theme', None)
		self.theme = themes.LoadTheme(theme_name)

	def ShowFromAskee(self):
		if not user.IsWriter(): return # .usertype>=2) : return
		
		print """<table border="1" cellpadding="4" cellspacing="0">
<tr><td>
<font size="-1">
<input name="asaskee" type="checkbox"> Make this question come from an askee:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input name="shortname" type="text" size="12" maxlength="12">
<a href="askeebrowse.html" target="_blank">Browse...</a>"""

		web.PrintFavoriteSelector(self.favs, 'askee')

		print """<select name="emotion">
<option value="n">Normal
<option value="h">Happy
<option value="a">Angry
<option value="s">Sad
</select><br>
Please do not overuse. -The Management
</font>
</td></tr>
</table>"""

	
	def run(self):
		slogan_bucket = self.theme.settings.get('slogan_bucket', 'expert')

		slogan = ConvDB.GetSlogan(slogan_bucket)
		if slogan:
			self.slogan = slogan
		else:
			self.slogan = ""

		self.threads = ConvDB.GetActiveThreadList()			
		
		if user.usertype >= 2:
			self.intrash = ConvDB.GetNumDeletedThreads()
			self.pending = ConvDB.GetNumNewThreads()
			self.favs = ConvDB.GetUserFavorites(user)
		else:
			self.intrash = 0
			self.pending = 0
			self.favs = None
			
		self.theme.PrintIndex(self)


page = HomePage()
page.run()
