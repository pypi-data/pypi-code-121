#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Utilities included in cartolidar project 
cartolidar: tools for Lidar processing focused on Spanish PNOA datasets

clidtools incldes ancillary tools that work on raster outputs of cartolidar
Most of those raster represent dasometric Lidar variables (DLVs).
DLVs (Daso Lidar Vars): vars that characterize forest or land cover structure.

@author:     Jose Bengoa
@copyright:  2022 @clid
@license:    GNU General Public License v3 (GPLv3)
@contact:    cartolidar@gmail.com
@deffield    updated: 2022-05-19
'''

import sys

__version__ = '0.0a2'
__updated__ = '2022-05-18'
# No se importa nada con: from qlidtwins import *
__all__ = []

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
    print(f'clidtools.__init__-> __name__:     <{__name__}>')
    print(f'clidtools.__init__-> __package__ : <{__package__ }>')
# ==============================================================================

# from cartolidar.clidtools.clidtwins_config import GLO # GLO es una variable publica del modulo clidtwins_config
# from cartolidar.clidtools.clidtwins import DasoLidarSource # DasoLidarSource es la clase principal del modulo clidtwins
# from cartolidar.clidtools.clidtwins import mostrarListaDrivers # mostrarListaDrivers es una funcion del modulo clidtwins

from .clidtwins_config import GLO # GLO es una variable publica del modulo clidtwins_config
from .clidtwins import DasoLidarSource # DasoLidarSource es la clase principal del modulo clidtwins
from .clidtwins import mostrarListaDrivers # mostrarListaDrivers es una funcion del modulo clidtwins

# Variables, clases y funciones que se importan con: from clidtwins import *
__all__ = [
    'GLO',
    'DasoLidarSource',
    'mostrarListaDrivers'
]

# from . import clidtwins # Inlcuye DasoLidarSource, mostrarListaDrivers, etc.
# from . import clidtwins_config # Incluye GLO, que es una variable publica del modulo clidtwins_config
# __all__ = [
#     'clidtwins',
#     'clidtwins_config',
# ]

