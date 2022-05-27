import sys

if sys.version_info < (3, 5):
    print("Chaanbot requires at least Python 3.5.")
    sys.exit(1)

__version__ = "2.1.0"
