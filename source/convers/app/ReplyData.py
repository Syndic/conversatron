from StandardVars import *
import ConvDB

class ReplyData: 
	def __init__(self, which=None):
		self.error = None
		self.isBlank = 0
		self.idToUse = None
		
		if which is not None: self.fillWithForm(str(which))
		
		
	def getFormData(self):
		which = str(self.replyNum)
		
		self.shortname = form.getvalue("shortname"+which, "")
		self.askeeid = int(form.getvalue("askee"+which, 0))
		self.text = form.getvalue("body"+which, "")
		
		if form.getvalue("onright"+which):
			self.side = 'r'
		else:
			self.side = 'l'
			
		self.emotion = form.getvalue("emotion"+which, 'n')
		
		self.replyIndex = which


	def resolveAskeeIDs(self):
		askeeid = None
		
		# Check for a blank entry
		if not (self.text or self.shortname or self.askeeid):
			self.isBlank = 1
			return
	
		if self.text and not (self.shortname or self.askeeid):
#			self.error = 'No askee specified for reply #%d' % self.replyNum
			self.error = 'No askee specified for this reply.'
			return
		
	
		if self.shortname:
			askeeid = ConvDB.AskeeShortcutToID(self.shortname)

			# error, unknown shortcut
			if askeeid is None:
				self.error = 'Unknown shortcut: %s' % self.shortname
				return

		elif self.askeeid:
			askeeid = self.askeeid

		# Check to see if this askee is retired or not
		askee = db.loadRow('askee', askeeid)
		if askee == None:
			self.error = "Unknown askee id. Weird."
			return
			
		if askee.retired == 'y' and not user.IsAdmin():
			self.error = "Askee has been retired. Sorry."
			return
			
		self.idToUse = askeeid		


	def fillWithForm(self, which):
		self.replyNum = which
	
		self.getFormData()
		self.resolveAskeeIDs()
