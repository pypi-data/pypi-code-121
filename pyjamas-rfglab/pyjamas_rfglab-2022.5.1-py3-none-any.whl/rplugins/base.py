"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from abc import ABC, abstractmethod

from pyjamas.rcallbacks.rcallback import RCallback


# To create a plugin, inherit from PJSPlugin.
class PJSPluginABC(ABC, RCallback):

    @property
    @abstractmethod
    def name(self) -> str:
        """

        :return: the name of the plugin to be displayed in the Plugins menu.
        """
        pass

    @abstractmethod
    def run(self, parameters: dict) -> bool:
        ## callback code
        pass
