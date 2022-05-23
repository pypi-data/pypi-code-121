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

import abc

from tikka.domains.application import Application


class MainApplicationInterface(abc.ABC):
    """
    MainApplicationInterface class
    """

    @abc.abstractmethod
    def __init__(self, application: Application) -> None:
        """
        Start main application with domain application

        :param application: Application instance
        :return:
        """
        raise NotImplementedError
