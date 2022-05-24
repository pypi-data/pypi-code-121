"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import pyparsing as ppa
from pyparsing.common import pyparsing_common as ppc

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


STRING = ppa.dbl_quoted_string.setParseAction(ppa.remove_quotes)
INTEGER = ppc.integer
FLOAT = ppc.real

VARIABLE = ppa.Word(init_chars="_" + ppa.alphas, body_chars=ppa.alphanums + '_')

# region[Main_Exec]

if __name__ == '__main__':
    pass
# endregion[Main_Exec]
