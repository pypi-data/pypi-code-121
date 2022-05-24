# Backport of shutil.copytree from Python 3.8

from __future__ import absolute_import

from sys import version_info
from os import lstat
from os import readlink
from os import symlink
from os import listdir
from os import name as osname
from os.path import join
from os.path import exists
from os.path import islink
from os.path import isdir

from shutil import copy
from shutil import copy2
from shutil import copystat
from shutil import Error

from struct import unpack_from
from contextlib import closing
import stat

from pathlib2 import Path

try:
    from os import fspath
except ImportError:
    fspath = lambda e: e  # noqa: E731

def _copytree(entries, src, dst, symlinks, ignore, copy_function,
              ignore_dangling_symlinks, dirs_exist_ok=False):
    if ignore is not None:
        ignored_names = ignore(fspath(src), entries)
    else:
        ignored_names = set()

    Path(dst).mkdir(parents=True, exist_ok=dirs_exist_ok)
    errors = []

    for srcentry in entries:
        if srcentry in ignored_names:
            continue
        srcname = join(src, srcentry)
        dstname = join(dst, srcentry)

        try:
            is_symlink = islink(srcname)
            if is_symlink and osname == 'nt':
                # Special check for directory junctions, which appear as
                # symlinks but we want to recurse.
                if version_info >= (3,8):
                    lstat_ = lstat(srcname)
                    if lstat_.st_reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT:
                        is_symlink = False
                else:
                    import win32file
                    import winioctlcon
                    import winnt
                    with closing(win32file.CreateFile(srcname, win32file.GENERIC_READ, 0, None, win32file.OPEN_EXISTING, win32file.FILE_FLAG_OPEN_REPARSE_POINT | win32file.FILE_FLAG_BACKUP_SEMANTICS, None)) as h:
                        ret = win32file.DeviceIoControl(h, winioctlcon.FSCTL_GET_REPARSE_POINT, None, winnt.MAXIMUM_REPARSE_DATA_BUFFER_SIZE, None)
                        if unpack_from('<i', ret)[0] & winnt.IO_REPARSE_TAG_MOUNT_POINT:
                            is_symlink = False
            if is_symlink:
                linkto = readlink(srcname)
                if symlinks:
                    # We can't just leave it to `copy_function` because legacy
                    # code with a custom `copy_function` may rely on copytree
                    # doing the right thing.
                    symlink(linkto, dstname)
                    if version_info >= (3,3):
                        copystat(srcname, dstname, follow_symlinks=False)
                    else:
                        # maybe no need to copy according to Python2 original impl
                        pass
                else:
                    # ignore dangling symlink if the flag is on
                    if exists(linkto) and ignore_dangling_symlinks:
                        continue
                    # otherise let the copy occur. copy2 will raise an error
                    if isdir(srcname):
                        copytree(srcname, dstname, symlinks, ignore,
                                 copy_function, dirs_exist_ok=dirs_exist_ok)
                    else:
                        copy_function(srcname, dstname)
            elif isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore, copy_function,
                         dirs_exist_ok=dirs_exist_ok)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy_function(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
        except OSError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        # Copying file access times may fail on Windows
        if getattr(why, 'winerror', None) is None:
            errors.append((src, dst, str(why)))
    if errors:
        raise Error(errors)
    return dst

def copytree(src, dst, symlinks=False, ignore=None, copy_function=copy2,
             ignore_dangling_symlinks=False, dirs_exist_ok=False):
    entries = listdir(src)
    return _copytree(entries=entries, src=src, dst=dst, symlinks=symlinks,
                     ignore=ignore, copy_function=copy_function,
                     ignore_dangling_symlinks=ignore_dangling_symlinks,
                     dirs_exist_ok=dirs_exist_ok)
