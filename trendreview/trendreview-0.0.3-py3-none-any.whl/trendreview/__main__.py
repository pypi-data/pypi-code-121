"""
Created on Thu Dec 16 16:11:17 2021
@author: jvorsten
Execute package as main
Begin command line entrypoint to package
"""
# Python imports
import sys

# Third party imports

# Local imports
from trendreview.trendreview import main, parser

# Declarations

# %%

if __name__ == '__main__':
    sys.exit(main(parser))
