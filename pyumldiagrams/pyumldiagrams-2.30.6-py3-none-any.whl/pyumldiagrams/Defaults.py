"""
Sensible defaults for this library
"""
from pyumldiagrams.image.ImageFormat import ImageFormat

LEFT_MARGIN: int = 8
"""
The left margin added to the layout on the UML diagram.  For certain document types
this is in adjusted units
"""
TOP_MARGIN:  int = 8
"""
The top margin added to the layout on the UML diagram.  For certain document types
this is in adjusted units
"""

DEFAULT_HORIZONTAL_GAP: int = 60
"""
The horizontal gap between UML graphics added to the layout in addition to the gap imposed 
by the actual graphics positions
"""
DEFAULT_VERTICAL_GAP:   int = 60
"""
The vertical gap between UML graphics added to the layout in addition to the gap imposed 
by the actual graphics positions
"""

DEFAULT_IMAGE_WIDTH:  int = 1280
"""
The image width
"""
DEFAULT_IMAGE_HEIGHT: int = 1024
"""
The image height"
"""

DEFAULT_LINE_WIDTH: int = 1
"""
The line width
"""

DEFAULT_FILE_NAME: str = 'PyutExport'
"""
The file name
"""

DEFAULT_IMAGE_FORMAT: ImageFormat.PNG
"""
The Image format

Please don't presume what I am offended by.  Sticks and stones may broke my bones, but words will never hurt me
"""
