import os
import sys

# 来源 ：https://ost.51cto.com/posts/370
ABSPATH = os.path.abspath(sys.argv[0])
ABSPATH = os.path.dirname(ABSPATH)
print(ABSPATH)
