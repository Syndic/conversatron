#!/usr/local/bin/python

import cgi, sys, os
import MySQLdb
import string

def fetch_hash(cursor):
	row = cursor.fetchone()
	if row == None: return None
	
	hash = {}
	for i in range(len(row)):
		hash[cursor.description[i][0]] = row[i]
		
	return hash


def outputitem(title,url):
	title = string.replace(title,'&',"&amp;")
	title = string.replace(title,'"',"&quot;")
	title = string.replace(title,"'","&apos;")
	
	print """<item>
	<title>%s</title>
	<link>%s</link>
</item>""" % (title,url)



### MAIN ###
DB = MySQLdb.connect(host="localhost", user="convers", db="conversatron")
cur = DB.cursor()
SQL = "select id,subject from thread where active='y' and deleted='n' order by whenis desc"
cur.execute(SQL)

sys.stdout.write("Content-type: text/xml\n\n")

print """<?xml version="1.0"?>
<!DOCTYPE rss PUBLIC "-//Netscape Communications//DTD RSS 0.91//EN" "http://my.netscape.com/publish/formats/rss-0.91.dtd">
<rss version="0.91">


<channel>
	<title>The Conversatron</title>
    <link>http://conversatron.com</link>
	<description>An Experiment in Distributed Pop Culture</description>
	<language>en-us</language>

	<image>
		<url>http://conversatron.com/syndicate/conlogo.jpg</url>
		<title>The Conversatron</title>
		<link>http://conversatron.com</link>
	</image>

"""
i = 0
while i < 15:
	row = fetch_hash(cur)
	if row == None: break;

	outputitem(row["subject"],"http://conversatron.com/convers.py?topic="+str(row["id"]))
	
	i = i + 1

print "</channel></rss>"

