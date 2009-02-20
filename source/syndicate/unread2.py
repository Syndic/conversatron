#!/usr/bin/python

import sys
import os
import re

import cgi
import cgitb; cgitb.enable()

import gzip

import cStringIO
import MySQLdb

def compressBuf(buf):
	zbuf = cStringIO.StringIO()
	zfile = gzip.GzipFile(mode = 'wb',  fileobj = zbuf, compresslevel = 6)
	zfile.write(buf)
	zfile.close()
	return zbuf.getvalue()


def fetch_hash(cursor):
	row = cursor.fetchone()
	if row == None: return None
	
	hash = {}
	for i in range(len(row)):
		hash[cursor.description[i][0]] = row[i]
		
	return hash


def outputitem(title,url,body):
	title = string.replace(title,'"',"&quot;")
	title = string.replace(title,"'","&apos;")
	
	print >> buff, """<item>
	<title>%s</title>
	<link>%s</link>
	<description>%s</description>
</item>""" % (title, url, cgi.escape(body) )


def do_page():
	DB = MySQLdb.connect(host="localhost", user="convers", db="conversatron")
	cur = DB.cursor()
	SQL = """
select
	thread.id, thread.subject, thread.whenis, user.name, entry.body
from
	entry,
	thread left join user on thread.user = user.id
where
	thread.active='n' and 
	thread.deleted='n' and 
	thread.id = entry.thread
order by thread.id desc
"""
	cur.execute(SQL)
	
	print >> buff, """<?xml version="1.0"?>
	<!--
	<!DOCTYPE rss PUBLIC "-//Netscape Communications//DTD RSS 0.91//EN"
				"http://my.netscape.com/publish/formats/rss-0.91.dtd">
	-->
	<rss version="0.91">
	
	
	<channel>
		<title>Con: Pending</title>
		<link>http://conversatron.com</link>
		<description>Unposted Con submissions</description>
		<language>en-us</language>
	
	"""
	i = 0
	while i < 30:
		row = fetch_hash(cur)
		if row == None: break;
		
		name = str(row["name"])
		
		subject = re.sub(r"(<[^>]*>)", '', row["subject"])
		body = row["whenis"] + "<br><br>" + row["body"]
	#	body = re.sub(r"(<[^>]*>)", '', row["body"])
	
		outputitem(name + ": " + subject, "http://conversatron.com/convers.py?topic=" + str(row["id"]), body)
		
		i = i + 1
	
	print >> buff, "</channel></rss>"


def main():
	try:
		do_page()
	except:
		print >> buff, "Whoops."

	if outputtype == 'text':
		content_type = "text/plain"
	else:
		content_type = "text/xml"
		
	content = buff.getvalue() 
	zbuf = compressBuf(content)
	
#	print "Content-type: %s" % content_type
	sys.stdout.write("Content-type: text/html\r\n")
	sys.stdout.write("Content-Encoding: gzip\r\n")
	sys.stdout.write("Content-Length: %d\r\n" % (len(zbuf)))
	
	sys.stdout.write("\r\n")
	
	sys.stdout.write(zbuf)

#	sys.stdout.write(content)
	

###

buff = cStringIO.StringIO()
form = cgi.FieldStorage()
outputtype = form.getvalue('type','')
	
main()
