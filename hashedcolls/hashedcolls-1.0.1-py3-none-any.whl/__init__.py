"""Hashed dict/list collections"""

# This file is a part of hashedcolls package
# Licensed under Do-What-The-Fuck-You-Want license
# Initially made by @jedi2light (aka Stoian Minaiev)

from .hashedcolls import HashedDict, HashedList

__pkg_name__ = 'hashedcolls'
__pkg_desc__ = 'Hashed dict/list collections'
__project_license__ = 'WTFPL'
__author__ = '@jedi2light'
__author_email__ = 'stoyan.minaev@gmail.com'
__maintainer__ = __author__
__maintainer_email__ = __author_email__
__major_version__ = 1
__minor_version__ = 0
__patch_version__ = 1
__version_tuple__ = (__major_version__,
                     __minor_version__,
                     __patch_version__)
__version_string__ = '.'.join(list(map(str, __version_tuple__)))
