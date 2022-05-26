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
from pathlib import Path
from typing import List

import yaml

from tikka.domains.entities.constants import CURRENCIES_FILENAME
from tikka.domains.entities.currency import Currency
from tikka.interfaces.adapters.repository.currencies import (
    CurrenciesRepositoryInterface,
)

ASSETS_PATH = Path(__file__).parent.joinpath("assets")
CURRENCIES_PATH = ASSETS_PATH.joinpath(CURRENCIES_FILENAME)


class FileCurrenciesRepository(CurrenciesRepositoryInterface):
    """
    FileCurrenciesRepository class
    """

    PARAMETER_NAME = "name"
    PARAMETER_SS58_FORMAT = "ss58_format"
    PARAMETER_ENTRY_POINTS = "entry_points"

    filepath = None

    def __init__(self):
        """
        Load Yaml file of currencies

        :return:
        """
        with open(
            Path(CURRENCIES_PATH).expanduser(), "r", encoding="utf-8"
        ) as filehandler:
            self.currencies = yaml.safe_load(filehandler)

    def get(self, code_name: str) -> Currency:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            FileCurrenciesRepository.get.__doc__
        )
        parameters = self._parameters(code_name)
        return Currency(
            code_name,
            parameters[self.PARAMETER_NAME],
            parameters[self.PARAMETER_SS58_FORMAT],
        )

    def code_names(self) -> list:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            FileCurrenciesRepository.code_names.__doc__
        )
        return list(self.currencies.keys())

    def names(self) -> list:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            FileCurrenciesRepository.names.__doc__
        )
        names = []
        for code_name in self.currencies:
            names.append(self.currencies[code_name]["name"])

        return names

    def get_entry_point_urls(self, code_name: str) -> List[str]:
        """
        Return currency entry point urls

        :param code_name: Currency code name
        :return:
        """
        parameters = self._parameters(code_name)
        return parameters[self.PARAMETER_ENTRY_POINTS]

    def _parameters(self, code_name: str) -> dict:
        """
        Return currency parameters for code name

        :param code_name: Currency code name
        :return:
        """
        return self.currencies[code_name]
