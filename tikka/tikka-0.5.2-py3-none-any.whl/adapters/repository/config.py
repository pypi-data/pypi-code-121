# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import os
import shutil
from pathlib import Path

from tikka.domains.entities.constants import CONFIG_FILENAME
from tikka.interfaces.adapters.repository.config import ConfigRepositoryInterface

ASSETS_PATH = Path(__file__).parent.joinpath("assets")
DEFAULT_CONFIG_PATH = ASSETS_PATH.joinpath(CONFIG_FILENAME)


class FileConfigRepository(ConfigRepositoryInterface):
    """
    FileConfigRepository class
    """

    filepath = None

    def __init__(self, path: Path):
        """
        Create config file in user config path

        :param path: Path instance of config file path
        :return:
        """
        self.filepath = Path().joinpath(path, CONFIG_FILENAME).expanduser()

        if not path.expanduser().exists():
            os.makedirs(path.expanduser())

        if not self.filepath.exists():
            # copy default config in user config path
            shutil.copyfile(DEFAULT_CONFIG_PATH.expanduser(), self.filepath)

    def load(self):
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConfigRepositoryInterface.load.__doc__
        )
        with DEFAULT_CONFIG_PATH.expanduser().open(
            "r", encoding="utf-8"
        ) as file_handler:
            default_data = json.load(file_handler)

        with self.filepath.open("r", encoding="utf-8") as file_handler:
            data = json.load(file_handler)

        data_keys_updated = False
        # add new config key if default config file updated
        for key in default_data:
            if key not in data:
                data[key] = default_data[key]
                data_keys_updated = True
        data_keys_to_delete = []
        # purge obsolete keys if default config file updated
        for key in data:
            if key not in default_data:
                data_keys_to_delete.append(key)
                data_keys_updated = True
        for key in data_keys_to_delete:
            del data[key]

        if data_keys_updated is True:
            self.save(data)

        return data

    def save(self, data: dict):
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConfigRepositoryInterface.save.__doc__
        )
        if self.filepath is not None:
            with self.filepath.open("w", encoding="utf-8") as file_handler:
                json.dump(data, file_handler)
