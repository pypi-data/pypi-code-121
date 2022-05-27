#######################################################################
#
# Copyright (C) 2022 David Palao
#
# This file is part of PacBioDataProcessing.
#
#  PacBioDataProcessing is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  PacBio data processing is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with PacBioDataProcessing. If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor
import logging


SLEEP_SECONDS = 20
TOO_OLD_AGE_SECONDS = 10*SLEEP_SECONDS
_ABANDONED_FILE_TEMPLATE_STR = "Abandoned sentinel '{}' detected; overwritten."


class SentinelFileFound(Exception):
    """Exception expected when the sentinel file is
    there before its creation.
    """


class SentinelFileNotFound(Exception):
    """Exception expected if the sentinel file is missing
    before the ``Sentinel`` removes it.
    """


class Sentinel:
    """This class creates objects that are expected to be used as
    context managers. At ``__enter__`` a sentinel file is created.
    At ``__exit__`` the sentinel file is removed.
    If the file is there before entering the context, or is not
    there when the context is exited, an exception is raised.
    """
    def __init__(self, checkpoint: Path):
        path_name = "."+checkpoint.name+".wip"
        self.path = checkpoint.with_name(path_name)
        self._executor = ThreadPoolExecutor(max_workers=1)

    def __enter__(self):
        try:
            self.path.touch(exist_ok=False)
        except FileExistsError:
            if self.is_file_too_old:
                self.path.touch(exist_ok=True)
                logging.info(_ABANDONED_FILE_TEMPLATE_STR.format(self.path))
            else:
                raise SentinelFileFound()
        self._executor.submit(self._anti_aging)

    def _anti_aging(self):
        """:meta public:
        Method that updates the modification time of the sentinel file
        every :py:data:`SLEEP_SECONDS` seconds. This is part of the
        mechanism to ensure that the sentinel does not get fooled by
        an abandoned leftover sentinel file.
        """
        while self.path.exists():
            self.path.touch()
            time.sleep(SLEEP_SECONDS)

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.path.unlink()
        except FileNotFoundError:
            raise SentinelFileNotFound()

    @property
    def is_file_too_old(self):
        """Property that answers the question: is the sentinel
        file too old to be taken as an active sentinel file, or not?
        """
        result = False
        if self.path.exists():
            now = time.time()
            age = now-self.path.stat().st_mtime
            if age > TOO_OLD_AGE_SECONDS:
                result = True
        return result

###############################################################
#
#  Note to developers:
#  -------------------
#
#  Something like the following implementation is *simpler*
#  but I found it *harder to test*. (DPalao, 21March2022):
#
# @contextlib.contextmanager
# def sentinel(checkpoint):
#     path_name = "."+checkpoint.name+".wip"
#     path = checkpoint.with_name(path_name)
#     try:
#         path.touch(exist_ok=False)
#     except FileExistsError:
#         raise SentinelFileExists()
#     yield path
#     try:
#         path.unlink()
#     except FileNotFoundError:
#         raise SentinelFileNotFound()
#
#  [Obviously it lacks the (anti-)aging mechanism as well
#   (DPalao, 25March2022)]
