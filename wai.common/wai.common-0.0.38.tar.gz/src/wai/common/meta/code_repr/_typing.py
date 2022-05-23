"""
Types to do with code representations.
"""
from typing import Dict, Tuple, Callable, Any

# The types of a code-representation
ImportDict = Dict[str, str]
CodeRepresentation = Tuple[ImportDict, str]

# The type of the code_repr function
CodeReprFunction = Callable[[Any], CodeRepresentation]
