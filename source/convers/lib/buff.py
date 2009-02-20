import os
import sys
import re
import time
import cStringIO
import Cookie
import gzip
import md5, base64

# use email package to handle HTTP headers
from email.Message import Message
from email.Parser import HeaderParser

class Error(Exception):pass

entity_headers = [
	'allow', 
	'content-encoding', 
	'content-language', 
	'content-length',
	'content-location',
	'content-md5',
	'content-range',
	'content-type',
	'etag',
	'expires',
	'last-modified',
	]

theOutput = None

def ETags(value):
	tags = []
	for tag in value.split(","):
		tag = tag.strip()
		if tag.startswith("W/"): tag = tag[2:]
		tag.replace('\"',"")
		tags.append(tag)
		
	return tags
	
def Close():
	global theOutput
	if theOutput is not None:
		theOutput.close()
		theOutput = None

class Out(object):
	def get():
		global theOutput
		if theOutput is None:
			raise Error, "No output object has been installed."
		return theOutput
	get = staticmethod(get)

	def __init__(self):
		global theOutput
		if theOutput is not None:
			raise Error, "An output object has already been installed."
	
		# Hook standard output
		self.real_stdout = sys.stdout
		self.buffer = cStringIO.StringIO()
		sys.stdout = self.buffer
		
		# Default content type
		self.contenttype = "text/html"
		
		# No headers
		self.headers = Message()
		self.sendEntityHeaders = True
		self.redirecting = False
		
		self.cookies = Cookie.SimpleCookie()
		
		# Detect compression
		self.acceptsGzip = 0
		if os.environ.get("HTTP_ACCEPT_ENCODING", "").find("gzip") != -1:
			self.acceptsGzip = 1
			
		# Trap exiting a script to force output to close
		self.ran = False
		theOutput = self
		sys.exitfunc = Close
			
	def getResponseBody(self, body):
		if self.acceptsGzip:
			#gzip writes the time into its header
			#this kills cacheability, so we hack the time to be 0
			real_time = time.time
			time.time= lambda a=None:0
			zbuf = cStringIO.StringIO()
			zfile = gzip.GzipFile(mode = 'wb',  fileobj = zbuf)
			zfile.write(body)
			zfile.close()
			self.headers['Content-Encoding'] = "gzip"
			output = zbuf.getvalue()
			time.time = real_time
			return output
		else:
			return body

	def close(self):
		if self.ran: return
	
		# Restore stdout so we can pipe our data out
		sys.stdout = self.real_stdout
		
		body = self.buffer.getvalue()
		headers = ""
		self.buffer.close()
		
		# Look for any headers already written
		if re.search("location:", body, re.I):
			self.redirecting = True
			self.sendEntityHeaders = False
			msg = HeaderParser().parsestr(body, True)
			
			# Add written headers to our header list
			for name, value in msg.items():
				self.headers.add_header(name,value)
		
		elif  re.search("content-type:", body, re.I):
			try:
				endOfHeaders = body.index("\n\n");
				headers = body[:endOfHeaders]
				body = body[endOfHeaders+2:]
				
				msg = HeaderParser().parsestr(headers, True)
				
				# Add written headers to our header list
				for name, value in msg.items():
					self.headers.add_header(name,value)

			except ValueError:
				raise error, "Headers detected, sort of"

		# Get the response body, possibly compressed
		if self.sendEntityHeaders:
			body = self.getResponseBody(body)
		
		del self.headers['Content-Length']
		self.headers['Content-Length'] = str(len(body))

		if not self.redirecting and (not 'content-type' in self.headers):
			self.headers['Content-Type'] = self.contenttype

		etag = base64.encodestring(md5.new(body).digest())[:-1]
		self.headers['ETag'] = '"' + etag + '"'
		if 'HTTP_IF_NONE_MATCH' in os.environ:
			if etag in ETags(os.environ['HTTP_IF_NONE_MATCH']):
				print "Status: 304 Not Modified"
				self.sendEntityHeaders = False
		
		self._send_headers()

		if self.sendEntityHeaders:
			sys.stdout.write(body)
			
		self.ran = True
		
	def _send_headers(self):
		for header in self.headers.keys():
			if ((not self.sendEntityHeaders) and (header.lower() in entity_headers)):
				continue
			print header+": "+str(self.headers[header])
			
		if len(self.cookies) > 0: print self.cookies.output()
			
		print
	

def main():
	out = Out()
	cook = Cookie.SimpleCookie()
	
	cook['user'] = 'Adam Vandenberg'
	cook['level'] = 150

	print """<html>
<head>
<title>This is my title</title>
</head>

<body>
<p>This is a paragraph.</p>

<pre>""" + str(cook) + """</pre>
</body>
</html>"""
	
#	out.close()

if __name__ == '__main__':
	main()
