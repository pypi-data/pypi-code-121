""" We import almost everything by default, in the general
namespace because it is simpler for everyone 

Circular dependecies on modules, use forward references:
Forward references: https://www.python.org/dev/peps/pep-0484/#forward-references

"""

from .image import *
from .channel import *
from .imageCollection import *
from .timeSeries import *
from .DCCExceptions import *
from .channelInteger import *
from .channelFloat import *
from .pathPattern import *
from .cziFile import *
from .movieFile import *
from .lifFile import *
from .dataset import *
from .correlationMatrix import *
from .database import *
from .metadata import *
from .cafeine import *
from . import speckleAnalysis


__version__ = "1.0.9"
__author__ = "Daniel Cote <dccote@cervo.ulaval.ca>"
