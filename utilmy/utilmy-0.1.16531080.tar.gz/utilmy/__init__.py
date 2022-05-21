
from utilmy.tabular import *


from utilmy.dates import *


from utilmy.utilmy import *


#### Typing ######################################################################################
## https://www.pythonsheets.com/notes/python-typing.html
### from utilmy import (  )
from typing import List, Optional, Tuple, Union, Dict, Any
Dict_none = Union[dict, None]
List_none = Union[list, None]
Int_none  = Union[None,int]
Path_type = Union[str, bytes, os.PathLike]

try:
    import numpy.typing
    npArrayLike = numpy.typing.ArrayLike
except ImportError:
    npArrayLike = Any
