"""
Reads data from packaged resources for π, e, and the meaning of life.

Entry point for package.
See, e.g., https://docs.python.org/3/library/__main__.html#main-py-in-python-packages
"""

import sys


# Note the the following import appears not to work if you attempt to run my_module.py directly
# with `python src/demo_package_sample_data_with_code/my_module.py`, returning the following error:
#     ImportError: attempted relative import with no known parent package
# However, I plan to run this from within a package, in which case it works fine.
from . my_module import main

if __name__ == "__main__":
    sys.exit(main())