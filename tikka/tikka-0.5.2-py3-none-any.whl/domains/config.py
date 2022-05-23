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

from typing import Any

from tikka.interfaces.adapters.repository.config import ConfigRepositoryInterface
from tikka.interfaces.domains.config import ConfigInterface


class Config(ConfigInterface):
    """
    Config domain class
    """

    def __init__(self, repository: ConfigRepositoryInterface):
        """
        Init Config instance

        :param repository: ConfigRepositoryInterface instance
        """
        self.repository = repository
        self.data = self.repository.load()

    def set(self, name: str, value: Any):
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConfigInterface.set.__doc__
        )
        self.data[name] = value
        self.repository.save(self.data)

    def get(self, name: str):
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConfigInterface.get.__doc__
        )
        return self.data[name]
