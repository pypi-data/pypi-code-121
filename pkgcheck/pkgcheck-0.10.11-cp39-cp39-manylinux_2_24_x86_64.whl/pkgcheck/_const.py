import os.path as osp
import sys
INSTALL_PREFIX = osp.abspath(sys.prefix)
DATA_PATH = osp.join(INSTALL_PREFIX, 'share/pkgcheck')
