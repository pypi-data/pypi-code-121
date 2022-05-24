# true 确定环境是python2
import sys

PY2 = sys.version_info[0] == 2
# true 确定环境是否是windows
WIN = sys.platform.startswith('win')

_identity = lambda x: x