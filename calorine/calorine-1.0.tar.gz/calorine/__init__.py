# -*- coding: utf-8 -*-
"""
Main module of the calorine package.
"""

from .io import (read_kappa,
                 read_thermo,
                 read_settings,
                 read_xyz,
                 write_xyz)
from .ase_calculator import GPUMD_NEP

__project__ = 'calorine'
__description__ = 'Some like it hot'
__copyright__ = '2022'
__license__ = 'Mozilla Public License 2.0 (MPL 2.0)'
__version__ = '1.0'
__maintainer__ = 'The calorine developers team'
__status__ = 'Stable'
__url__ = 'http://calorine.materialsmodeling.org/'

__all__ = ['GPUMD_NEP',
           'read_thermo',
           'read_kappa',
           'read_settings',
           'read_xyz',
           'write_xyz']
