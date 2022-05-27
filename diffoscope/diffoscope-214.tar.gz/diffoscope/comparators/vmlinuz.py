#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2022 Chris Lamb <lamby@debian.org>
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

import logging
import os.path
import pathlib
import re
import subprocess

from diffoscope.tools import tool_required

from .utils.file import File
from .utils.archive import Archive

logger = logging.getLogger(__name__)


class VmlinuzContainer(Archive):
    def open_archive(self):
        return self

    def close_archive(self):
        pass

    def get_member_names(self):
        return [self.get_compressed_content_name(".vmlinuz")]

    @tool_required("readelf")
    def extract(self, member_name, dest_dir):
        dest_path = os.path.join(dest_dir, member_name)
        logger.debug("extracting vmlinuz to %s", dest_path)

        # Locate extract-vmlinux script
        script = pathlib.Path(__file__).parent.parent.parent.joinpath(
            "scripts", "extract-vmlinux"
        )
        with open(dest_path, "wb") as f:
            subprocess.check_call(
                [script, self.source.path],
                stdout=f,
                stderr=None,
            )

        return dest_path


class VmlinuzFile(File):
    DESCRIPTION = "Linux kernel images"
    CONTAINER_CLASSES = [VmlinuzContainer]
    FILE_TYPE_RE = re.compile(r"^Linux kernel\b")
