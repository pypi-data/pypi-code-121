import os
import sys

filepath = os.path.abspath(__file__)
pathlist = filepath.split(os.sep)
pathlist = pathlist[:-4]
TopPath = os.sep.join(pathlist)
sys.path.insert(0, TopPath)
print(TopPath)

from re_common.libtest.get_attr_test import settings
from re_common.baselibrary.tools.get_attr import get_attrs

print(get_attrs(settings))
