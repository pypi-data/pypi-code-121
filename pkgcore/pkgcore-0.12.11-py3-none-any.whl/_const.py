import os.path as osp
import sys

from snakeoil import process

INSTALL_PREFIX = osp.abspath(sys.prefix)
DATA_PATH = osp.join(INSTALL_PREFIX, 'share/pkgcore')
CONFIG_PATH = osp.join(INSTALL_PREFIX, 'share/pkgcore/config')
LIBDIR_PATH = osp.join(INSTALL_PREFIX, 'lib/pkgcore')
EBD_PATH = osp.join(INSTALL_PREFIX, 'lib/pkgcore/ebd')
INJECTED_BIN_PATH = ()
CP_BINARY = process.find_binary('cp')
