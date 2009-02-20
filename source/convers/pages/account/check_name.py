#!/usr/bin/env python

from StandardVars import *
import web

# class NameResult(object);
# 	__slots__ = ['status','message']
# 
# 	def __init__(self, status,message):
# 		self.status=status
# 		self.message=message

name = form.getvalue("name")
if not name: 
	print "[-1, 'Illegal name']";
	web.quit()
	
exists = db.loadValue("select name from user where name=%s", name)
if exists:
	print "[0, 'Name in use']";
else:
	print "[1, 'Name available']";
