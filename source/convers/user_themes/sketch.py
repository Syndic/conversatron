from themes.default import BasicTheme
from StandardVars import *


# Factory method to create theme instances
def MakeThemeObject(name = None):
	return TrendwhoreTheme()		

		
class TrendwhoreTheme(BasicTheme):
	def __init__(self,  settings_file = "themes/sketch.ini", theme_file = "themes/sketch.xml"):
		BasicTheme.__init__(self, settings_file, theme_file)
		

	def StartBox(self,title, color="#000000", width=None, intcolor="#FFFFFF", padding=4):
		data = {'color': color, 'boxtitle': title}
		self.templates.display('box_start', data)

                
	def EndBox(self):
		self.templates.display('box_end', {})
