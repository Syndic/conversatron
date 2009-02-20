#!/usr/bin/env python
#Edit a thread entry, quick before anyone sees!

from StandardVars import *
import ConvDB
import web
import themes

from BasicPage import BasicPage
from Consts import Consts

buttons = Consts(Fix="fix_button", Delete="delete_button")
actions = Consts(Swap="swap", Activate="activate")

class Entry(BasicPage):
	def __init__(self):
		if not user.IsWriter(): web.GoHome()
		self.getEntry()
	
		BasicPage.__init__(self, 
			name="Edit an entry", 
			post_buttons=buttons,
			actions=['op',actions])
		
		self.buttonHandlers = {
			buttons.Fix: self.HandleFix,
			buttons.Delete: self.HandleDelete
			}
	
	def getEntry(self):
		if 'id' not in form:
			web.GoHome()
			
		self.entry = db.loadRow('entry', form.getvalue("id"))
		if self.entry is None: web.GoHome()
	
	def run(self):
		if self.postButton:
			self.dispatchButton()
		elif self.action:
			self.HandleOp()
		else:
			self.EditEntry()
			
	def HandleFix(self):
		if form.getvalue('onright'):
			self.entry.side = 'r'
		else:
			self.entry.side = 'l'
		
		text = form.getvalue('body', '')
		text = web.NewlinestoBR(text)
		self.entry.body = text
	
		self.entry.emotion = form.getvalue('emotion', '')
	
		self.entry._Update(db)
		web.ReInFolder('convers.py', 'topic=%s' % self.entry.thread)
			
	def HandleDelete(self):
		self.entry._Delete(db)
		ConvDB.CacheThreadProps(self.entry.thread)
		web.ReInFolder('convers.py', 'topic=%s' % self.entry.thread)
			
	def HandleOp(self):		
		if self.action == actions.Swap:
			if 'sid' not in form: web.GoHome()
			
			sid = form.getvalue('sid')
			ConvDB.SwapEntries(self.entry.id, sid)
			web.ReInFolder('convers.py', 'topic=%s' % self.entry.thread)
		
		elif self.action == actions.Activate:
			self.entry.flag=" "
			self.entry._Update(db)
			ConvDB.CacheThreadProps(self.entry.thread)
			web.ReInFolder('convers.py', 'topic=%s' % self.entry.thread)
			
	def EditEntry(self):
		"Show the edit entry form."
		theme = themes.LoadTheme()
		
		theme.PrintHeader('The Conversatron - Edit entry')
		theme.PrintNavBanner('Edit entry')
		
		theme.StartUserBox('Edit entry:')
		
		print '<form method="post" action="entry.py">'
		print '<input type="hidden" name="id" value="%s">' % (self.entry.id)
		
		web.HtmlSelect(
			(('Normal','n'), ('Happy','h'), ('Angry','a'), ('Sad','s')),
			'emotion',
			self.entry.emotion)
			
		checked = ""
		if self.entry.side == 'r':
			checked = " checked"
	
		print 'On right: <input name="onright" type="checkbox"%s><br>' % checked
		
		text = self.entry.body.replace('</textarea>','').replace('<br>','\n')
		
		print '<textarea name="body" rows=10 cols=60 wrap="soft" onkeydown="CtrlEnterSubmit()">%s</textarea><br>' % (text)
		print '<input type="submit" name="fix_button" value="Fix it"> Please quickly proofread your reply. Thank you. <br><br><input type="submit" name="delete_button" value="Delete Entry"></form><hr>'
				
		theme.EndUserBox()
		theme.PrintFooter()
		
page = Entry()
page.run()
