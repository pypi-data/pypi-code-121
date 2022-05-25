#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Tools for Lidar processing focused on Spanish PNOA datasets

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
@deffield    updated: 2022-05-19
'''

import sys

__version__ = '0.0a2'
__date__ = '2016-2022'
__updated__ = '2022-05-18'

# ==============================================================================
# Verbose provisional para la version alpha
if '-vvv' in sys.argv:
    __verbose__ = 3
elif '-vv' in sys.argv:
    __verbose__ = 2
elif '-v' in sys.argv or '--verbose' in sys.argv:
    __verbose__ = 1
else:
    __verbose__ = 0
if __verbose__ > 2:
    print(f'cartolidar.__init__-> __name__:     <{__name__}>')
    print(f'cartolidar.__init__-> __package__ : <{__package__ }>')
# ==============================================================================

# Paquetes, clases y modulos que se importan con: from cartolidar import *
# __all__ = [
#     'clidtools',
#     'clidax',
#     'DasoLidarSource',
# ]

# from cartolidar import clidtools
# from cartolidar import clidax
# from cartolidar.clidtools.clidtwins import DasoLidarSource
# from . import clidtools
# from . import clidax
# from clidtools.clidtwins import DasoLidarSource
