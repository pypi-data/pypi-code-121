"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import pyparsing as ppa

# * Local Imports --------------------------------------------------------------------------------------->
from antistasi_sqf_tools.code_parsing.grammar.general_parts import COMMA, BRACKETS_OPEN, BRACKETS_CLOSE
from antistasi_sqf_tools.code_parsing.grammar.base_data_parts import FLOAT, STRING, INTEGER, VARIABLE

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


_ARRAY_ITEM = ppa.Forward()
_ARRAY_CONTENT = ppa.delimited_list(_ARRAY_ITEM, delim=COMMA)

ARRAY = BRACKETS_OPEN + ppa.ZeroOrMore(_ARRAY_CONTENT) + BRACKETS_CLOSE

_ARRAY_ITEM <<= STRING ^ INTEGER ^ ppa.Group(ARRAY) ^ FLOAT ^ VARIABLE


# region[Main_Exec]

if __name__ == '__main__':
    x = '["rhs_weap_hk416d10", "rhsusf_acc_nt4_black", "rhsusf_acc_anpeq15_bk", "rhsusf_acc_eotech_552", ["rhs_mag_30Rnd_556x45_Mk318_PMAG"], [], "rhsusf_acc_kac_grip"]'
    i = ARRAY.parse_string(x, parse_all=True)
    print(i)
# endregion[Main_Exec]
