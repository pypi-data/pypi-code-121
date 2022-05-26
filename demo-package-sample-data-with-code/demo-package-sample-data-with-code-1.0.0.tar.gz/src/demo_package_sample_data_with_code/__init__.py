# The following import (from . __version__ import __version__) is a component
# of the mechanism to provide a single source for the version number.
# For more information, see the docstring comments in the __version__.py file.

from . __version__ import __version__

# The following import was apparently required to get the  console script
# entry point to work. Without this import, I got errors at run time (when
# issuing the command `demo-command` on the command line, but not when using
# `runpy`, i.e., `python -m`):
#    AttributeError: module 'demo_package_sample_data_with_code' has no attribute 'main'
# Thus by importing main() in __init__.py, `main` was in the proper namespace.

from . __main__ import main