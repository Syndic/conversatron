#!/usr/bin/env python
"""Conversatr.com URL dispatcher script

This script handles all .py requests on http://conversatron.com/ 
after Apache has rewritten the URLS into the /convers/ folder.

The default behavior is to execfile the SCRIPT_URL.

Other URL rewrites (to .py files only for now) can happen through
this script rather than with mod_rewrite rules.

Todo: .py-less URLs.
"""
import sys
import cgi
import cgitb;cgitb.enable()
import os
import os.path

def dump_vars():
	"Dump all CGI variables to the browser"
	keys = os.environ.keys()
	keys.sort()
	print "<table>"
	for key in keys:
		print "<tr><td><b>%s:</b></td><td>%s</td></tr>" % (
			key, cgi.escape(os.environ[key]))
	print "</table>"

def report_error(error):
		print "Content-Type: text/html\n" 
		print "<html><head><title>Dispatching Error</title></head>"
		print "<body>"
		print "<h2>Conversatron.com dispatcher</h2>"
		print "<p><b>Error:</b> %s</p>" % error
	
		print "<hr><h3>CGI Vars</h3>"
		dump_vars()
		print "</body></html>"
		sys.exit(0)

def main():
	# Ensure that a path has been provided		
	filename = os.environ.get('SCRIPT_URL','')

	if filename.endswith("/"):
		filename += "index.py"

	filename = "pages" + filename

	if not os.path.exists(filename):
		base = os.path.abspath(".")
		report_error("No script '%s/%s'" % (base,filename))
	
	sys.path.append(os.path.abspath("lib"))
	sys.path.append(os.path.abspath("app"))
	# The script shouldn't get any vars from us!
	d = {}
	execfile(filename,d,d)

main()
