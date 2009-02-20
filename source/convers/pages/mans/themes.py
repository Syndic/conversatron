#!/usr/bin/env python
#New thread manager

import ConvDB
import web

from StandardVars import *

import themes

def ShowThemeOptions(list, chosen):
	for item in list:
		if item == chosen:
			selected = " selected='selected'"
		else:
			selected = ""
			
		print """<option value='%s'%s>%s</option>""" % (item, selected, item)


def main():
	themeList = themes.themeNames()

	theme.PrintHeader('The Conversatron - Theme Manager')
	theme.PrintNavBanner('Theme Manager')
	
	print "<form method='post'>"
	print "<input type='hidden' name='op' value='change'>"
	
	print "<table>"
	
	print "<tr><td align='right'>Day Theme:</td><td><select name='daytheme'>"
	ShowThemeOptions(themeList, themes._daytheme)
	print "</select></td></tr>"
	
	print "<tr><td align='right'>Night Theme:</td><td><select name='nighttheme'>"
	ShowThemeOptions(themeList, themes._nighttheme)
	print "</select></td></tr>"
	
	print "<tr><td align='right'>Day Starts:</td><td>&nbsp;<input name='daystarts' value='%s' size=5></td></tr>" % (themes._daystarts)
	print "<tr><td align='right'>Night Starts:</td><td>&nbsp;<input name='nightstarts' value='%s' size=5></td></tr>" % (themes._nightstarts)

#	print "<tr><td align='right'>Override Home:</td><td>&nbsp;<input name='overridehome' value='%s' size=5></td></tr>" % (themes._overridehome)

	print "<tr><td align='right'>Use user's theme for posts:</td><td>&nbsp;<input name='overridepost' value='%s' size=5> (1=yes, 0=no)</td></tr>" % (themes._overridepost)

	print "<tr><td></td><td><input type='submit' value='Change'></td></tr>"
			
	print "</table>"
	print "</form>"
	
	theme.PrintFooter()
	

def change():
	# Template for the settings.ini file
	
	setting_names = ("daytheme","nighttheme","daystarts","nightstarts","overridepost")
	
	settings = "[settings]\n"	
	for name in setting_names:
		value = form.getvalue(name)
		settings += "%s: %s\n" % (name, value)
		

	fini = open('data/settings.ini', 'w+')
	fini.write(settings)
	fini.close()
	
	web.RedirectInFolder('/mans/themes.py')


# ------- begin ----------
if not user.IsAdmin():
	web.GoHome()


theme = themes.LoadTheme()

op = form.getvalue("op", "showvalues")

if op=="showvalues":
	main()
elif op=="change":
	change()
else:
	theme.PrintHeader('The Conversatron - Theme Manager')
	theme.PrintNavBanner('Theme Manager')
	print "invalid operation"
	theme.PrintFooter()
