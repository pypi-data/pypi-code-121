from zetane.context import *
from zetane.socket import *
from zetane.version import __version__

from inspect import isclass
from importlib import import_module

 # import the module and iterate through its attributes
module = import_module(f"{__name__}.ZetaneViz")

for attribute_name in dir(module):
    attribute = getattr(module, attribute_name)

    if isclass(attribute):
        # Add the class to this package's variables
        globals()[attribute_name] = attribute
