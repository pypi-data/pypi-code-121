# noinspection PyUnresolvedReferences
from ..EasyCommandInterface import *


def _init():
    import sys
    import EasyCommandInterface

    sys.modules['ECI'] = EasyCommandInterface


_init()
