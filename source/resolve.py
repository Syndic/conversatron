#!/usr/bin/python

#IP resolver

import cgi
import sys
import socket

form = cgi.FieldStorage()

print 'Content-type: text/html\n'
print '<html><head><title>The Conversatron - Resolver</title></head><body bgcolor="#FFFFFF"><br>'


print '<font size="+2">'

print 'Attempting to resolve...<br>'


try:
	ip = form['addr'].value
except:
	print 'No IP to resolve.<br>'
	print '</font></body></html>'
	sys.exit()

print 'Resolving IP: ['+ip+'] ...<br>'

try:
	host = socket.gethostbyaddr(ip)
except:
	print 'IP is not named.<br>'
	print '</font></body></html>'
	sys.exit()

print 'Resolves to '+ host[0]

print '</font></body></html>'
