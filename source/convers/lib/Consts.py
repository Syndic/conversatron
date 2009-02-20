#!/usr/bin/env python

"A collection of named constants"
class Consts(object):
	def __init__(self,**kw):
		self.__dict__['_values'] = {}
		self._values.update(kw)

	def names(self):
		return self._values.keys()
		
	def __iter__(self):
		return self._values.itervalues()
		
	def __getattr__(self,name):
		return self._values[name]
		
	def __setattr__(self,name,value):
		if (name not in self._values):
			object.__setattr__(self,name,value)
		else:
			raise TypeError, "Cannot assign to %s" % name
			
	def __repr__(self):
		"""A Consts object can be eval'd if all values are eval'able."""
		r = "Consts("
		values=[]
		for k,v in self._values.iteritems():
			values.append("%s=%r" % (k,v))
		r += ", ".join(values) + ")"
		return r

if __name__=='__main__':
	consts = Consts(foo='bar', eggs='sauce', chuck='rock')

	print consts
	print 'consts.foo: ',consts.foo
	
	print 'Values: ',
	for k in consts: print k,
	print
	print 'Names: ', consts.names()
	
	try:
		print "Setting 'consts.foo':",
		consts.foo = "some_other_value"
		print "set"
	except Exception, e:
		print "%s: %s" % (e.__class__.__name__, e)
