from typing import Tuple, Type, Optional

from .config import GROUP
from . import io
from enum import Enum, IntEnum, EnumMeta

def enum_txt(txts: dict ) -> None:
    """ define the enumerator text from a dictionary of IntEnumerator/txt pairs """
    for e, t in txts.items():
        setattr(e, 'txt', t)

def get_txt(e) -> str:
    """ get attribute txt if exists otherwhise attribute name 
    
    This is used for retrieving a custom text of enumerator 
    """
    return getattr(e, 'txt', e.name)

def get_group(e)-> int:
    """ get attribute .group if exists alse return GROUP.UNKNOWN """
    return getattr(e, 'group', GROUP.UNKNOWN)


def enum_group(groups: dict ) -> None:
    """ define the enumerator group from a dictionary of IntEnumerator/GROUP.member pairs """
    for e, g in groups.items():
        setattr(e, 'group', g)

def fjoin(*args) -> str:
    """ join fits elements """
    return " ".join(a.strip() for a in args if a)

def fsplit(key) -> Tuple[str,str]:
    s, _, p = key[::-1].partition(" ")
    return p[::-1], s[::-1]


_enum = -1 
def _inc(i: Optional[int] = None) -> int:
    """ number increment to use in frontend for easy implementation
    
    _inc(0) # reset increment to 0 and return 0 
    _inc()  # increment and return incremented number 
    """
    global _enum
    _enum = _enum+1 if i is None else i
    return _enum


