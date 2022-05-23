"""
ecalic
======

provides:
1. a efficient wayt handle CMS Ecal IC-type variables, i.e. a collection of
numbers associated to a single Ecal crystal.
2. helper classes to transform Ecal database xml_file (from conddb) to ecalic format.

Available submodules:
==================
- ic: handling of CMS-Ecal ICs (format and operations) (main class icCMS)
- iov: convert xml_file conddb format to icCMS format
- cmsStyle: improving style (can be a source of crash), not mandatory

Documentation
=============
Best to get documentation is to load the package with ipython, which provides
tab completion.
>>> import ecalic as ecal
>>> help(ecal.ic)
>>> help(ecal.iov)

Note:
- matplotlib.pyplot is available as ecalic.plt
"""

from . import ic
from . import iov
#from . import cmsStyle as cms
from .ic import icCMS
from .ic import geom
from .ic import join_eb_ee
from .ic import icCovCor
from .iov import xml
