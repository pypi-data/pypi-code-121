def getVersionNumber():
	import pkg_resources
	version = pkg_resources.require("traytable")[0].version
	return version

__version__ = getVersionNumber()

from .screens import screen, tray, clonetray, setrows, setcols
from .wells import well
from .csv import read_rockmaker