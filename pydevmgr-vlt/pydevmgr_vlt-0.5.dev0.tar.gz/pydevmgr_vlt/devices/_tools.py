from typing import Optional
from pydevmgr_core import NodeAlias1

_enum = -1 
def _inc(i: Optional[int] = None) -> int:
    """ number increment to use in frontend 
    
    _inc(0) # reset increment to 0 and return 0 
    _inc()  # increment and return incremented number 
    """
    global _enum
    _enum = _enum+1 if i is None else i
    return _enum

