from xml.sax.saxutils import quoteattr, escape

class FormDict(object):
	def __init__(self, form):
		self._form = form
		
	def __getitem__(self,name):
		if name not in self._form:
			raise KeyError, name

		return self.get(name)
		
	def get(self,name, default=None):
		return self._form.getfirst(name,default)
		
	def __contains__(self,name):
		return name in self._form


def _render_tag(control, tagname, contents=None):
	if contents is None: contents = ""

	return "<%(tagname)s%(attrs)s>%(contents)s</%(tagname)s>" % {
		'tagname': tagname,
		'attrs': control._attr_list(),
		'contents': contents
		}
	

class ControlBase(object):
	def __init__(self, **kw):
		self.attrs = {}
		for name in kw:
			self.attrs[name.rstrip('_')] = kw[name]

		self.value = ""
		self.multivalue = False
		
	def update_attrs(self, more_attrs):
		self.attrs.update(more_attrs)
		
	def get_value(self):
		return self.attrs.get('value', self.value)
		
	def get_name(self):
		return self.attrs.get('name')
		
	def map_name(self):
		"""Name a template can use to bind to this control"""
		if self.multivalue:
			return "%s:%s" % (self.get_name(), self.get_value())
		else: return self.get_name()
			
	def _attr_list(self, **kw):
		"""Format a list of HTML attributes"""
		attrs = self.attrs.copy()
		attrs.update(kw)
		
		if len(attrs) == 0: return ""
		
		pairs = [""] #leading space
		for key in attrs:
			value = attrs[key]
			if value is not None:
				if value == "": value=key
				pairs.append( '%s=%s' % (key, quoteattr(str(value)) ) )
			
		return " ".join(pairs)
	
	def fill(self, form): pass		
	def render(self): raise NotImplementedError, "Must override render"


class InputRenderer(object):
	"""Render an <input> subclass"""
	def render(self):
		return "<input%s />" % self._attr_list()

class ValueBinder(object):
	"""Fill by setting 'value' attr if name present in form"""
	def fill(self, form):
		if self.get_name() in form:
			self.attrs['value']=form.get(self.get_name())

class CheckedBinder(object):
	"""Fill by setting 'checked' attr if name=value present in form"""
	def fill(self, form):
		if self.get_name() in form:
			if form[self.get_name()]==self.get_value():
				self.attrs['checked'] = 'checked'
			else: 
				try: del self.attrs['checked']
				except KeyError: pass
	
class InputBase(InputRenderer, ControlBase):
	def __init__(self, **kw):
		ControlBase.__init__(self,**kw)
 
class TextInput(ValueBinder, InputBase):
	def __init__(self, **kw):
		InputBase.__init__(self, type='text',**kw)
		
class PasswordInput(ValueBinder, InputBase):
	def __init__(self, **kw):
		InputBase.__init__(self, type='password',**kw)
		
class TextArea(ControlBase):
	def __init__(self, **kw):
		ControlBase.__init__(self, **kw)

	def fill(self, form):
		self.value = form.get(self.get_name(), self.value)
# 		if self.self.get_name() in form:
# 			self.value = form[self.self.get_name()]
	
	def render(self):
		return _render_tag(self, 'textarea', escape(self.value))

class CheckBox(CheckedBinder, InputBase):
	def __init__(self,**kw):
		InputBase.__init__(self, type='checkbox',**kw)
		self.multivalue = True

class RadioButton(CheckedBinder, InputBase):
	def __init__(self,**kw):
		InputBase.__init__(self, type='radio',**kw)
		self.multivalue = True

class SubmitButton(InputBase):
	def __init__(self, **kw):
		InputBase.__init__(self, type='submit',**kw)

class ResetButton(InputBase):
	def __init__(self, **kw):
		InputBase.__init__(self, type='reset',**kw)

class HiddenInput(InputBase):
	def __init__(self, **kw):
		InputBase.__init__(self, type='hidden', **kw)

class ButtonInput(InputBase):
	def __init__(self, **kw):
		InputBase.__init__(self, type='button', **kw)

class Button(ControlBase):
	def __init__(self, **kw):
		ControlBase.__init__(self, **kw)

	def renderer(self):
		return _render_tag(self, 'button', self.value)

class Option(ControlBase):
	def __init__(self, select, contents=None, **kw):
		ControlBase.__init__(self,**kw)
		self.select = select
		
		if contents is None: contents = self.attrs.get('value', '')
		self.contents = contents
		
	def fill(self, form):
		if self.select is None: return
		
		name = self.select.get_name()

		if (name in form) and (form[name]==self.attrs.get('value')): 
			self.attrs['selected'] = 'selected'
 		else: del self.attrs['selected']
		
	def render(self):
		return _render_tag(self, 'option', self.contents)

class Select(ControlBase):
	def __init__(self, options=None, **kw):
		ControlBase.__init__(self, **kw)
		self.options = []
		
		if options is not None:
			for value,description in options:
				self.options.append(Option(self, description, value=value))
				
	def add_option(self, option):
		self.options.append(option)
		
	def fill(self,form):
		if self.get_name() not in form: return
		value = form[self.get_name()]
		
		for option in self.options: option.fill(form)
		
	def _option_list(self):
		vals = []
		for option in self.options:
			vals.append(option.render())
		return "\n".join(vals)
		
	def render(self):
		return _render_tag(self, 'select', self._option_list())
