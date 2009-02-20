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


def outputitem(title,url, body):
	title = string.replace(title,'"',"&quot;")
	title = string.replace(title,"'","&apos;")
	
	body = cgi.escape(body)
	
	print """<item>
	<title>%s</title>
	<link>%s</link>
	<description>%s</description>
</item>""" % (title,url,body)



### MAIN ###
DB = MySQLdb.connect(host="localhost", user="convers", db="conversatron")
cur = DB.cursor()
SQL = "select t.id,t.subject,e.body from thread as t, entry as e where t.active='y' and t.deleted='n' and t.id=e.thread order by t.whenis desc limit 15"
cur.execute(SQL)

sys.stdout.write("Content-type: text/xml\n\n")

print """<?xml version="1.0"?>

<!DOCTYPE rss PUBLIC "-//Netscape Communications//DTD RSS 0.91//EN"
            "http://my.netscape.com/publish/formats/rss-0.91.dtd">

<rss version="0.91">


<channel>
	<title>The Conversatron</title>
    <link>http://conversatron.com</link>
	<description>An Experiment in Distributed Pop Culture</description>
	<language>en-us</language>

"""
i = 0
while i < 15:
	row = fetch_hash(cur)
	if row == None: break;

	outputitem(row["subject"],"http://conversatron.com/convers.py?topic="+str(row["id"]), row["body"])
	
	i = i + 1

print "</channel></rss>"

