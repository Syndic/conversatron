import WebForms.Controls
import re
from HTMLParser import HTMLParser

_single_tags = ('img', 'input', 'br', 'hr', 'link', 'meta')

class Text(object):
	def __init__(self, content=None):
		self.content = content
		
	def render(self): return self.content

class Element(object):
	def __init__(self, tag, attrs):
		self.tag = tag
		self.attrs = attrs

def _codify_tag(tag):
	return re.sub('[-:.]', '_', tag)

class A(HTMLParser):
	def __init__(self, control_defs = None):
		HTMLParser.__init__(self)
		
		self.runs = []
		self.controls = {}
		self.ids = {}
		
		if control_defs:
			for control in control_defs:
				self.controls[control.map_name()] = control
				
	def get_control(self, map_name):
		return self.controls.get(map_name)
				
	def do_x_control(self, tag, attrs):
		if 'name' not in attrs: return #Error
		
		name = attrs.get('name')
		del attrs['name']
		
		control = self.get_control(name) #self.controls.get(name)
		if control is not None:
			control.update_attrs(attrs)
			self.runs.append(control)

	def generic_starttag(self, tag, attrs):
		if 'id' in attrs:
			self.ids[attrs['id']] = tag
		self.runs.append(Text(self.get_starttag_text()))

	def handle_starttag(self, tag, attrs):
		# Turn [(n,v)...] into a dict
		attrs = dict(attrs)
	
		m = getattr(self,'start_' + _codify_tag(tag), self.generic_starttag)
		m(tag,attrs)

	def handle_startendtag(self, tag, attrs):
		m = getattr(self,'do_' + _codify_tag(tag), None)
		if m: m(tag,dict(attrs))
		else:
			HTMLParser.handle_startendtag(self, tag)
	
	def handle_endtag(self, tag):
		if not tag in _single_tags:
			self.runs.append(Text("</%s>" % tag));

	def handle_comment(self, data): pass #eat comments. ARUM

	def handle_data(self, data): self.runs.append(Text(data))
	
	def handle_entityref(self, data): 
		self.handle_data("&%s;" % data)
	def handle_charref(self, data): 
		self.handle_charref("&#%s;" % data)
		
	def handle_pi(self, data):
		data = data.strip()
		command = None
		space = data.find(' ')
		if -1 < space:
			command = data[:space]

		#print command
	
	def render(self): print ''.join([run.render() for run in self.runs])
	
	def fill(self, form):
		for control in self.controls.itervalues(): 
			control.fill(form)
	
	def parse(self):
		self.feed(self.template)
		self.close()

		# collate neighboring Text()
		new_parts = []
		for part in self.runs:
			if  (0 < len(new_parts)) and (isinstance(part, Text)):
				last_part = new_parts[-1];
				if isinstance(last_part, Text):
					last_part.content += part.content
				else:
					new_parts.append(part)
			else:
				new_parts.append(part)

		self.runs = new_parts
	

def main():
	input = WebForms.Controls.TextInput(name='foo', size=12)
	a = A([input])
	a.template = """
<?include foo="bar" ?>
<html>
<head>
<title>Adam Vandenberg's Personal Site</title>
<link rel="stylesheet" type="text/css" href="/all.css">
</head>

<body>&amp;
<x:control name="foo" />
<div id="nav">
<img style="margin: 5px;" src="/img/avcom.gif" align=middle>
<img style="margin-top: 5px;" src="/img/squiggle.gif" align=middle>
<img style="margin-top: 7px;" src="/img/avtitle.gif" align=middle>
</div>
<br>
<div class="wrapper">
<div id="main">
<h1>Adamv.com</h1>

<p>
I'm a computer programmer living in Chapel Hill, NC.<br>
I provide software consulting under the name <a href="http://flangy.com/">Flangy Software</a>.
</p>

<p>
My resume is <a href="/resume/">available online</a>.
</p>

<h2>Fonts</h2>

<p>Some <a href="/fonts/">TrueType fonts</a> I created.</p>

<h2>Code Projects</h2>
<p>My <a href="/dev/">programming related projects</a>.</p>

<h2>Other Places of Interest</h2>

<ul>

<li> My weblog, <strike><a href="http://theflangynews.editthispage.com/" style="color:#999;text-decoration:none">The Flangy News</a></strike> <a href="http://www.livejournal.com/users/piehead/">The Piehead News</a>.</li>
</ul>
</p>

<hr size="1">

<h2>Contact Information</h2>

<ul>
<li> Email: <img src="/img/qqq.gif" align=absmiddle></li>
</ul>
</div>
</div>
</body>
</html>
"""

	a.parse()
	a.fill({'foo': 'blart'})
	
	a.render()
	print a.ids
	print len(a.runs)
	print [type(part).__name__ for part in a.runs]

if __name__ == "__main__":
	main()
