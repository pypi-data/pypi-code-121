from sym.shared.cli.helpers.config import init as config_init

config_init("symflow")

from sym.shared.cli.helpers.init import sym_init

from .commands import import_all
from .commands.symflow import symflow

import_all()
sym_init()

if __name__ == "__main__":
    symflow()
