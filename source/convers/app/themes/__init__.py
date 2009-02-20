# Dynamic theme code for The Conversatron
import time
import ConfigParser
from StandardVars import user

# Helper import function given in the Python docs.
# Correctly imports a dotted package name.
# Returns a reference to the right-most package. The default import
# returns a reference to the /left-most/ package.

def my_import(name):
	mod = __import__(name)
	components = name.split('.')
	for comp in components[1:]:
		mod = getattr(mod, comp)
	return mod


default_theme_name = "coolmint"

# A "*/" prefix will look for the file in the user_themes folder.
# No prefix means to look in the theme package folder.
registered_themes = {
	# Standard themes
	'classic'	: ('classic.ini', 'standard_boxes.xml'),
	'expert'	: ('expert.ini', 'standard_boxes.xml'),
	'night'		: ('night.ini', 'standard_boxes.xml'),

	# Boringest theme available
	'coolmint'	: ('*/coolmint.ini', '*/coolmint.xml'),

	'2000am' : ('*/2000d.ini', '*/2000.xml'),
	'2000pm' : ('*/2000n.ini', '*/2000.xml'),
	
	'beach' : ('*/beach.ini', '*/2000.xml'),

	# Text only theme
	'textonly'	: None,

	# Holidays
	'val'		: ('*/val.ini', 'standard_boxes.xml'),
	'valnight'	: ('*/valnight.ini', 'standard_boxes.xml'),
	
	'xmas'		: ('*/xmas.ini', 'standard_boxes.xml'),

	'solstice'		: ('*/solstice.ini', 'standard_boxes.xml'),

	'halloween'		: ('*/halloween.ini', 'standard_boxes.xml'),

	# And the rest	
	'aquaui'	: ('*/aquaui.ini', '*/aquaui.xml'),
	'lunaxp'	: (None, '*/lunaxp.xml'),

	'bmw'		: ('*/bmw.ini', 'standard_boxes.xml'),
		
	'space'		: ('*/space.ini', '*/space.xml'),
	
	"trendwhore": None,
	'sketch'	: None,
	'crayon'	: ('*/crayon.ini', 'standard_boxes.xml'),
	'elvis'		: ('*/elvis.ini', 'standard_boxes.xml'),
	}


def themeNames():
	theList = list(registered_themes.keys())
	theList.sort()
	
	return theList


def GetCurrentThemeName():
	hour = time.localtime(time.time())[3]
	minute = time.localtime(time.time())[4]
	
	now = hour * 100 + minute
	
	if _daystarts <= now < _nightstarts:
		return _daytheme
	else:
		return _nighttheme
	

def LoadTheme(theme_name = None):
	# Select the user's theme if they are overriding or no theme is specified
	if user.IsRegistered():
		if (user.themeoverride == 'y' or theme_name is None) and user.theme:
	 		theme_name = user.theme

	# Otherwise get the current theme
	if not theme_name:
		theme_name = GetCurrentThemeName()
	
	# Otherwise, try the hardwired default theme
	if not registered_themes.has_key(theme_name):
		theme_name = default_theme_name
	
	theme_files = registered_themes.get(theme_name, None)

	# If we got something, load a simple theme	
	if theme_files != None:
		theme_module = my_import('themes.default')
		theme_obj = theme_module.BasicTheme(*theme_files)
		theme_obj._name = theme_name
	
	# If the theme isn't a simple one, try importing it as a module
	else:
		theme_module = my_import('user_themes.' + theme_name)
		theme_obj = theme_module.MakeThemeObject(theme_name)
		theme_obj._name = theme_name	
	
	return theme_obj


def main():	
	config = ConfigParser.ConfigParser()
	config.read(['data/settings.ini'])

	global _daystarts, _nightstarts, _daytheme, _nighttheme
	global _overridehome, _overridepost
	
	try:
		_daystarts = config.getint('settings','daystarts')
	except:
		_daystarts = 600
		
	try:
		_nightstarts = config.getint('settings','nightstarts')
	except:
		_nightstarts = 1800

	try:	
		_daytheme = config.get('settings','daytheme')
	except:
		_daytheme = 'expert'
		
	try:
		_nighttheme = config.get('settings','nighttheme')
	except:
		_nighttheme = 'night'
	
#	_overridehome = config.getint('settings','overridehome')

	try:
		_overridepost = config.getint('settings','overridepost')
	except:
		_overridepost = 1

main()
