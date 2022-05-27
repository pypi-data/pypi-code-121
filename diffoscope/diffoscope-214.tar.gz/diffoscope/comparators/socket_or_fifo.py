#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2021 Brent Spillner <s p i l l n e r @ a c m . o r g>
#
# diffoscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# diffoscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with diffoscope.  If not, see <https://www.gnu.org/licenses/>.

import os
import stat
import logging

from diffoscope.tempfiles import get_named_temporary_file
from diffoscope.difference import Difference

from .binary import FilesystemFile
from .utils.file import File

logger = logging.getLogger(__name__)


class SocketOrFIFO(File):
    DESCRIPTION = "local (UNIX domain) sockets and named pipes (FIFOs)"

    @classmethod
    def recognizes(cls, file):
        return file.is_socket_or_fifo()

    def get_type(self):
        assert isinstance(self, FilesystemFile)
        st = os.lstat(self.name)
        return stat.S_IFMT(st.st_mode)

    def has_same_content_as(self, other):
        try:
            # (filesystem ID, inode) pair uniquely identifies the socket/pipe
            # Path comparison allows matching against pipes inside an archive
            # (i.e. that would be created by extraction), while using .samefile()
            # lets us match endpoints that might have more than one "canonical"
            # pathname after a mount -o rebind
            if self.get_type() != other.get_type():
                return False
            if os.path.exists(self.name) and os.path.exists(other.name):
                return os.path.samefile(self.name, other.name)
            return os.path.realname(self.name) == os.path.realname(other.name)
        except (AttributeError, OSError):
            # 'other' is likely something odd that doesn't support stat() and/or
            # can't supply an fs_uuid/inode pair for samefile()
            logger.debug(
                "has_same_content: Not a socket, FIFO, or ordinary file: %s",
                other,
            )
            return False

    def create_placeholder(self):
        with get_named_temporary_file(mode="w+", delete=False) as f:
            f.write(format_socket(self.get_type(), self.name))
            f.flush()
            return f.name

    @property
    def path(self):
        if not hasattr(self, "_placeholder"):
            self._placeholder = self.create_placeholder()
        return self._placeholder

    def cleanup(self):
        if hasattr(self, "_placeholder"):
            os.remove(self._placeholder)
            del self._placeholder
        super().cleanup()

    def compare(self, other, source=None):
        with open(self.path) as my_content, open(other.path) as other_content:
            return Difference.from_text_readers(
                my_content,
                other_content,
                self.name,
                other.name,
                source=source,
                comment="socket/FIFO",
            )


def format_socket(mode, filename):
    if stat.S_ISSOCK(mode):
        kind = "UNIX domain socket"
    elif stat.S_ISFIFO(mode):
        kind = "named pipe (FIFO)"
    else:
        kind = "ERROR: problem with an is_socket_or_fifo() predicate"
    return f"{kind}: {filename}\n"
