"""
Package for the get_argument_to_typevar function.
"""
# Requires version-wrangling as typing changed between 3.6 and 3.7
from ...version import Python36Checker as __Python36Checker
if __Python36Checker().current_passes():
    from ._get_argument_to_typevar_3_6 import get_argument_to_typevar
else:
    from ._get_argument_to_typevar_3_7 import get_argument_to_typevar
