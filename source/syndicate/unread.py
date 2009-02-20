#!/usr/local/bin/python -u

import cStringIO
import cgi, sys, os
import MySQLdb
import re

def escape(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    s = s.replace("'", "&apos;")
    return s


def fetch_hash(cursor):
	row = cursor.fetchone()
	if row == None: return None
	
	hash = {}
	for i in range(len(row)):
		hash[cursor.description[i][0]] = row[i]
		
	return hash


def outputitem(title,url,body):
	print """<item>
	<title>%s</title>
	<link>%s</link>
	<description>%s</description>
</item>""" % (escape(title), escape(url), escape(body) )



def main():
	real_stdout = sys.stdout
	sys.stdout = cStringIO.StringIO()

	
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
	
	form = cgi.FieldStorage()
	outputtype = form.getvalue('type','')
	
	if outputtype == 'text':
		sys.stdout.write("Content-type: text/plain\n\n")
	else:
		sys.stdout.write("Content-type: text/xml\n\n")
	
	print """<?xml version="1.0" encoding="ISO-8859-1" ?>
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
	
	print "</channel></rss>"
	
	real_stdout.write( sys.stdout.getvalue() )
	

main()
