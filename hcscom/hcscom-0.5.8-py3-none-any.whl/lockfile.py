""" module:: hcscom.lockfile
    :synopsis: A small helper until an official python lockfile module is available.
    moduleauthor:: Patrick Menschel (menschel.p@posteo.de)
    license:: GPLv3 or later.
"""

import os
from hashlib import sha1

import psutil
import logging
from shutil import chown
from os import chmod
import stat

LOGGER = logging.getLogger(__name__)


class DeviceAlreadyInUseException(BaseException):
    """
    Prevent usage of a serial port by multiple processes
    """
    pass


class LockFile:
    """
    A helper class to prevent resource usage by multiple instances of HcsCom class
    """

    def __init__(self, device_name):
        real_device_path = os.path.realpath(device_name)
        m = sha1()
        m.update(real_device_path.encode())
        self.lockfile_path = "/var/lock/hcscom_port_{0}.lock".format(m.hexdigest())
        self.acquire()

    def acquire(self) -> None:
        """
        Acquire a Lockfile
        :return: None.
        """
        lockfile_path = self.lockfile_path
        if os.path.exists(lockfile_path):
            with open(lockfile_path) as f:
                pid_in_lock_file = int(f.readline())

            if os.getpid() != pid_in_lock_file and psutil.pid_exists(pid_in_lock_file):
                LOGGER.error("device already used by PID {0}".format(pid_in_lock_file))
                raise DeviceAlreadyInUseException
            else:
                LOGGER.warning("found lockfile with our PID {0}".format(pid_in_lock_file))

        with open(lockfile_path, "w") as f:
            f.write(str(os.getpid()))

        # it can be assumed that every user is in group dialout
        # make sure another user may delete a stale lockfile

        chown(lockfile_path, group="dialout")
        chmod(lockfile_path, mode=(stat.S_IRGRP | stat.S_IWGRP | stat.S_IWUSR | stat.S_IRUSR | stat.S_IROTH))

        self.lockfile_path = lockfile_path

    def release(self) -> None:
        """
        Release a Lockfile
        :return: None.
        """
        if self.lockfile_path is not None:
            try:
                os.remove(self.lockfile_path)
            except OSError:
                # we obviously do not own the file
                pass

    def __del__(self):
        self.release()
