"""
Standard Tags, Sets and Maps.

This module contains implementation of standard AIML tags and sets & maps.

For the information about sets and maps, refer to
https://sites.google.com/a/techmaru.com/techmaruhome/technology/aiml-2-1
"""
from ._pattern import PATTERNS, EXACT_MATCH_SCORE
from ._template import TEMPLATE_EVAL, TEMPLATE_PARSER
from .sets import IS_NUMBER
from .maps import SUCCESSOR, PREDECESSOR, SINGULAR, PLURAL
from typing import Dict, Mapping, Set


STD_SETS: Dict[str, Set[str]] = {
    "number": IS_NUMBER
}
"""AIML sets defined by the standard:

* number: set of natural numbers
"""


STD_MAPS: Dict[str, Mapping[str, str]] = {
    "successor": SUCCESSOR,      #
    "predecessor": PREDECESSOR,  #
    "singular": SINGULAR,        #
    "plural": PLURAL             #
}
"""Maps defined by AIML standard:

* successor: The function f(x) = x + 1.  (or "unknown")
* predecessor: The function f(x) = x - 1.  (or "unknown")
* singular: Mapping plural -> singular  (english only)
* plural: Mapping singular -> plural (english only)
"""

__all__ = [
    "PATTERNS", "EXACT_MATCH_SCORE",
    "TEMPLATE_EVAL", "TEMPLATE_PARSER",
    "STD_SETS",
    "STD_MAPS",
]
