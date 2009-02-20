"Defines a basic page handler for CGI based programs"

from StandardVars import form
import web

class Error(Exception): pass

class BasicPage(object):	
	"Basic services for CGI based programs"
	
	def __init__(self, **kw):
		self.postButton = None
		self.action = None
	
 		if 'post_buttons' in kw:
 			self.setPostButton(kw['post_buttons'])
 			
 		if 'actions' in kw:
 			self.setAction(kw['actions'])
 			
 		self.site = ""
 		if 'name' in kw:
 			self.name = kw['name']
		else:
			self.name = self.__class__.__name__
			
	def dispatchButton(self):
		if not self.buttonHandlers: return
		
		handler = self.buttonHandlers.get(self.postButton)
		if handler: handler()

	def isPost(self): return web.hasPostData()
	def isGet(self): os.environ.get("REQUEST_METHOD") == "GET"
	
	def setPostButton(self, buttons):
		"Determine which button was used to POST the form, if any"
		if not web.hasPostData(): 
			self.postButton = None
			return
		
		for button in buttons:
			if button in form: 
				self.postButton = button
				return
		
		raise Error, "Post data with unknown button."
		
	def setAction(self, actions):
		param, values = actions
		if param not in form:
			return
			
		action = form.getvalue(param)
		for value in values:
			if action == value:
				self.action = value
				return

	def __str__(self):
#		return "A Conversatron page class (" + self.__class__.__name__ + ")"
		return 'Page %s "%s"' % (self.site, self.name)
