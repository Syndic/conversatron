import re, sys, types

class StringWalker:
	"Iterates through a string. Useful for stepping linearly through a string in a recursive function."
	def __init__(self,str):
		self.str = str
		self.i = 0
		
	def nextchar(self):
		if self.i >= len(self.str):
			return None
			
		value = self.str[self.i]
		self.i = self.i + 1
		return value
		
	def getuntil(self, delim):
		dindex = self.str.index(delim, self.i)
		value = self.str[self.i:dindex]
		self.i = dindex
		
		return value
		
	def reset(self):
		self.i = 0


class Template:
### Part classes
	class TextPart:
		"A part of a template containg text to copy to the output."
		def __init__(self,s):
			self.s = s
			
		def evaluate(self,namespace=None,manager=None):
			return self.s
	
	
	class CodePart:
		"A part of a template containing an expression to evaluate and print."
		def __init__(self,s):
			self.s = s
	
		def evaluate(self,namespace={},manager=None):
			try:
				return eval(self.s,namespace)
			except Exception, e:
				if manager.debugMode:
					return "code error: " + self.s + "<br>" + str(e) + "<br>"
				else:
					return None;


	class ConditionalPart:
		"A part of a template containing an expression and some parts. If expression is true then show the parts."
		def __init__(self,condition,parts):
			# maybe should be a condition and a Template?
			self.condition = condition
			self.parts = parts
	
		def evaluate(self,namespace={},manager=None):
			try:
				result = eval(self.condition,namespace)
			except Exception, e:
				if manager.debugMode:
					return "error in conditional: " + self.condition + "<br>" + str(e) + "<br>"
				else:
					result = None
			
			if result:
				for part in self.parts:
					value = part.evaluate(namespace,manager)
					if value != None: sys.stdout.write(str(value))

	class TemplatePart:
		"A part of a template containing the name of another template to display."
		def __init__(self, templatename):
			self.templatename  = templatename
	
		def evaluate(self,namespace={},manager=None):
			if manager.debugMode: 
				sys.stdout.write("Include: "+self.templatename+"<br>")
			
			try:
				manager.display(self.templatename,namespace)
			except Exception, e:
				return "template error:" + str(self.templatename) + "<br>" + str(e) + "<br>"

### Template methods
	def __init__(self,template):
		self.list = self.__parse(StringWalker(template))
		
	def __parse(self,walker):
		"Returns a list of parts."
		thelist = []
		part = ""
		inBlock = 0
		escapeMode = 0
		haveConditional = 0
		
		while 1:
			char = walker.nextchar()
			if char is None: break

			# if the last character was a \ then let this character through as-is.			
			if escapeMode:
				part = part + char
				escapeMode = 0

			# a \ escapes the next character
			elif char == "\\":
				escapeMode = 1
				
			# If we are in a template block in } ends it. Otherwise, we return (and possibly pop up a level).
			elif char == "}":
				if inBlock:
					if part != "":
						thelist.append(Template.CodePart(part))							
						part = ""

					inBlock = 0
				else:
					break;

			# { Starts a template block.
			elif char == "{":
				if not inBlock:
					if part != "":
						thelist.append(Template.TextPart(part))
						part = ""
						
					inBlock = 1
					haveConditional = 0
				else:
					# error - this brace should have been caught in a recursive call which would have inBlock false.
					pass
			
			# An unescaped : in a template block marks a conditional block					
			elif (char == ":") and (inBlock):
				# we have the begining of a conditional.
				# "part" is the conditional, need to get the rest.
				thelist.append( Template.ConditionalPart(part,self.__parse(walker)) )
				inBlock = 0
				part = ""
				
			elif (char == "?") and (inBlock) and (not haveConditional):
				templatename = walker.getuntil("}")
				thelist.append( Template.TemplatePart(templatename) )
				inBlock = 0
				part = ""
				walker.nextchar()
								
			# otherwise just add this character to the current part.
			else:
				part = part + char
				
		# if there is some text left add it as a text part.
		if part != "":
			thelist.append(Template.TextPart(part))
			
		return thelist


	def display(self, namespace={},manager=None):
		for part in self.list:
			value = part.evaluate(namespace, manager)
			if value != None: sys.stdout.write(str(value))
			

class FileTemplate(Template):
	def __init__(self,filename):
		try:
			fTemplate = open(filename)
			template = fTemplate.read()
			fTemplate.close()
			self.list = self.__parse(StringWalker(template))
		except:
			print "error loading "+filename
		

class Manager:
	def __init__(self):
		self.templates = {}
		self.debugMode = False
		
	def display(self, template_name, namespace={}, debugMode = True):
#		try:
		if debugMode is not None:
			self.debugmode = debugMode

		template = self.templates[template_name]
		template.display(namespace, self)
#		except: pass

	def add_string(self,name,template):
		self.templates[name]=Template(template)
	
	def add_files(self,filenames):
		if type(filenames) == types.StringType:
			filenames = (filenames,)
		
		for filename in filenames:
			fTemplate = open(filename)
			template = fTemplate.read()
			fTemplate.close()

			# first check if the file contains multiple templates.			
			
			# 1: any attributes on the template, 2: template body.
			re_template = re.compile(r"<castle:template(.*?)>\s*(.*?)\s*</castle:template>",re.DOTALL)
			start = 0
			match = re_template.search(template,start)
			
			if match != None:
				while match:
					# get the template name
					name_match = re.search(r"name=\"(.*?)\"",match.group(1))
					tname = name_match.group(1)
					tbody = match.group(2)
					
					self.templates[tname]=Template(tbody)
					
					start = match.end()+1
					match = re_template.search(template,start)

			else:
			# otherwise, this is just a single template file.
				name = re.search(r"(.*)\.t$", filename)
				self.templates[name] = Template(template)
