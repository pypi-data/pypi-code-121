"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from pathlib import Path

# * Third Party Imports --------------------------------------------------------------------------------->
import click

# * Local Imports --------------------------------------------------------------------------------------->
from antistasi_sqf_tools.doc_creating import add_doc_sub_group

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


@click.group(name="antistasi-sqf-tools")
@click.help_option("-h", "--help")
def antistasi_sqf_tools_cli():
    ...


add_doc_sub_group(antistasi_sqf_tools_cli)


# region[Main_Exec]

if __name__ == '__main__':
    pass

# endregion[Main_Exec]
