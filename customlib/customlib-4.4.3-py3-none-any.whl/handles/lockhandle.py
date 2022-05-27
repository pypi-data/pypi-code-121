# -*- coding: UTF-8 -*-

from msvcrt import LK_NBLCK, LK_LOCK, LK_NBRLCK, LK_RLCK, locking
from sys import version_info
from typing import IO

# noinspection PyUnresolvedReferences
from pywintypes import OVERLAPPED, error as pywintypes_error
from win32con import LOCKFILE_FAIL_IMMEDIATELY
# noinspection PyProtectedMember
from win32file import LockFileEx, UnlockFileEx, _get_osfhandle as get_osfhandle
from winerror import ERROR_NOT_LOCKED, ERROR_LOCK_VIOLATION

from ..constants import LOCK
from ..exceptions import LockException


class FileLock(object):
    """File locking class."""

    @staticmethod
    def _flags(mode: str):
        flags: dict = {
            "w": LOCK.EX,
            "a": LOCK.EX,
            "x": LOCK.EX,
            "r": LOCK.SH,
        }
        return flags.get(mode)

    @staticmethod
    def _mode(handle: IO):
        """Return the `handle` mode."""
        mode = handle.mode
        return mode.strip("tb+")

    def __init__(self):
        self.__overlapped = OVERLAPPED()

        if version_info.major == 2:
            self.lock_length = -1
        else:
            self.lock_length = int(2**31 - 1)

    def lock(self, handle: IO, flags: int):
        if flags & LOCK.SH:
            if version_info.major == 2:
                if flags & LOCK.NB:
                    mode = LOCKFILE_FAIL_IMMEDIATELY
                else:
                    mode = 0

            else:
                if flags & LOCK.NB:
                    mode = LK_NBRLCK
                else:
                    mode = LK_RLCK

            # is there any reason not to reuse the following structure?
            file_handle = get_osfhandle(handle.fileno())
            try:
                LockFileEx(file_handle, mode, 0, -0x10000, self.__overlapped)
            except pywintypes_error as exc_value:
                # error: (
                #   33, 'LockFileEx',
                #   'The process cannot access the file because another process has locked a portion of the file.'
                # )
                if exc_value.winerror == ERROR_LOCK_VIOLATION:
                    raise LockException(LockException.LOCK_FAILED, exc_value.strerror, handle=handle)
                else:
                    # Q:  Are there exceptions/codes we should be dealing with here?
                    raise
        else:
            if flags & LOCK.NB:
                mode = LK_NBLCK
            else:
                mode = LK_LOCK

            # windows locks byte ranges, so make sure to lock from file start
            try:
                save_position = handle.tell()
                if save_position:
                    # [ ] test exclusive lock fails on seek here
                    # [ ] test if shared lock passes this point
                    handle.seek(0)
                    # [x] check if 0 param locks entire file (not documented in Python)
                    # [x] fails with "IOError: [Errno 13] Permission denied", but -1 seems to do the trick

                try:
                    locking(handle.fileno(), mode, self.lock_length)
                except IOError as exc_value:
                    # [ ] be more specific here
                    raise LockException(LockException.LOCK_FAILED, exc_value.strerror, handle=handle)
                finally:
                    if save_position:
                        handle.seek(save_position)
            except IOError as exc_value:
                raise LockException(LockException.LOCK_FAILED, exc_value.strerror, handle=handle)

    def unlock(self, handle: IO):
        try:
            save_position = handle.tell()
            if save_position:
                handle.seek(0)

            try:
                locking(handle.fileno(), LOCK.UN, self.lock_length)
            except IOError as exc:

                if exc.strerror == 'Permission denied':
                    file_handle = get_osfhandle(handle.fileno())
                    try:
                        UnlockFileEx(file_handle, 0, -0x10000, self.__overlapped)
                    except pywintypes_error as exc:

                        if exc.winerror == ERROR_NOT_LOCKED:
                            # error: (158, 'UnlockFileEx', 'The segment is already unlocked.')
                            # To match the 'posix' implementation, silently ignore this error
                            pass
                        else:
                            # Q:  Are there exceptions/codes we should be dealing with here?
                            raise LockException(LockException.LOCK_FAILED, exc.strerror, handle=handle)
                else:
                    raise LockException(LockException.LOCK_FAILED, exc.strerror, handle=handle)
            finally:
                if save_position:
                    handle.seek(save_position)
        except IOError as exc:
            raise LockException(LockException.LOCK_FAILED, exc.strerror, handle=handle)

    def get_flags(self, handle: IO):
        mode = self._mode(handle)
        return self._flags(mode)
