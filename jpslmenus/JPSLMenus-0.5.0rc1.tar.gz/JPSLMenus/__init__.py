######
# Install JS support when this is imported with from JPSLUtils import *
######
import os
from IPython.display import display, HTML

#Locate package directory
mydir=os.path.dirname(__file__) #absolute path to directory containing this file.

#load the supporting css
# tempcssfile = open(os.path.join(mydir,'css','input_table.css'))
# tempstyle = '<style type="text/css">'
# tempstyle += tempcssfile.read()+'</style>'
# tempcssfile.close()
# display(HTML(tempstyle))

#load the supporting javascript
tempJSfile=open(os.path.join(mydir,'js','menu.js'))
tempscript='<script type="text/javascript">'
tempscript+=tempJSfile.read()+'</script>'
tempJSfile.close()
display(HTML(tempscript))
del tempJSfile
del tempscript
del mydir
del display
del HTML
del os