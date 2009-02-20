#!/usr/bin/python

#File manager. Yeah!

import string
import dircache

from StandardVars import *
import web
import themes

def HandleList(directory):
	"List all files in the given directory."

	global descriptions	
	
	theme.PrintHeader('The Conversatron - File Manager')
	theme.PrintNavBanner('File Manager')
	
	print "<b>Current Directory:</b> " + directory + "<br>"
	print descriptions[directory]
	print '<hr>'

	print '<form enctype="multipart/form-data" action="fileman.py" method="post">'
	print '<input type="hidden" name="op" value="submit">'
	print '<input type="hidden" name="dir" value="'+directory+'">'
	print 'Upload a file: <input name="thefile" type="file">'
	print '<input type="submit" value="Submit a hot hot GIF">'
	print '<br>'

	print "Change Directory: "
	
	i = 0
	for dir in dirlist:
		if 0 < i: print ' | '
	
		if dir == directory:
			print '<b>'+dir+'</b>'
		else:
			print '<a href="fileman.py?dir='+dir+'" title="' + descriptions[dir] + '">'+dir+'</a>'
			
		i = i +1
		
	print '</form>'
	print '<hr>'
	
	
	listit = form.getvalue('listit')
	if listit:
		filelist = dircache.listdir(directory)

		numfiles = len(filelist)
		colheight = numfiles/4
		currow = 0
		
		print '<font size="+2">File list:</font><br><br><table width="100%"><tr><td valign="top">'
		for item in filelist:
			if item[0] == '.':
				continue
			print item+' &nbsp; <a href="'+directory+'/'+item+'" target="viewer">[view]</a><br>'
			currow = currow + 1
			if currow > colheight:
				print '</td><td valign="top">'
				currow = 0
		print '</td></tr></table>'
	else:
		print '<a href="fileman.py?dir='+directory+'&listit=true">List files</a>'
				
	print '</body></html>'



def HandleSubmit(directory):
	"Accept a submitted file."
	try:
		thefile = form["thefile"].file
		filename = form["thefile"].filename
		pos = string.rfind(filename, '/')
		if pos >= 0:
			filename = filename[pos+1:]
		pos = string.rfind(filename, '\\')
		if pos >= 0:
			filename = filename[pos+1:]
		pos = string.rfind(filename, ':')
		if pos >= 0:
			filename = filename[pos+1:]
			
		dirname = directory+'/'+filename
		f = open(dirname, "w")
		f.write(thefile.read())
		f.close()
	except:
		pass
	
	web.RedirectInFolder('/fileman.py?dir=' + directory)


# ------- begin ----------
if user.usertype < 3:
	web.GoHome()

dirlist = ['askees', 'stuff', 'img', 'users']

descriptions = {
	"askees": "Put all 80x100 gifs of jpgs of askees here. Nothing else goes here.",
	"stuff": "Put <b>ALL</b> stuff here. Do not put stuff in img. If in doubt, it's stuff.",
	"img" : "Put only interface art here. Do NOT put one-time stuff here. That goes it stuff.",
	"users" : "Put 80x100 user pictures here.",
}


theme = themes.LoadTheme()

op = form.getvalue('op', 'list')
directory = form.getvalue('dir', 'askees')

# No access to a directory unless it's in the blessed list.
if directory not in dirlist:
	web.GoHome()

if op == "list":
	HandleList(directory)	
elif op == "submit":
	HandleSubmit(directory)
