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
from dataclasses import dataclass
from typing import Optional


@dataclass
class Currency:

    code_name: str
    name: str
    ss58_format: int
    token_decimals: Optional[int] = None
    token_symbol: Optional[str] = None
    universal_dividend: Optional[int] = None
    monetary_mass: Optional[int] = None
    members_count: Optional[int] = None
