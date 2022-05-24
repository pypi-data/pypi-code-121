"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import pyparsing as ppa

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


SINGLE_QUOTE = ppa.Suppress("'")
DOUBLE_QUOTE = ppa.Suppress('"')

COMMA = ppa.Suppress(",")
SEMI_COLON = ppa.Suppress(";")
COLON = ppa.Suppress(":")

EQUALS_SIGN = ppa.Suppress("=")
EXCLAMATION_MARK = ppa.Suppress("!")
OCTOTHORP = ppa.Suppress("#")
BACKSLASH = ppa.Suppress("\\")
FORWARD_SLASH = ppa.Suppress("/")
GREATER_THAN = ppa.Suppress("<")
LESS_THAN = ppa.Suppress(">")
PIPE = ppa.Suppress("|")

PARENTHESES_OPEN = ppa.Suppress("(")
PARENTHESES_CLOSE = ppa.Suppress(")")
BRACKETS_OPEN = ppa.Suppress("[")
BRACKETS_CLOSE = ppa.Suppress("]")
BRACES_OPEN = ppa.Suppress("{")
BRACES_CLOSE = ppa.Suppress("}")


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
