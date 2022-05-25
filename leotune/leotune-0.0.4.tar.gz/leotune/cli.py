# (CLI (Command-line Interface))
# GNU General Public License v3.0,
#             Copyright (C) 2022 凪坤 (GitHub ID: sandyzikun)
# -*-
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# -*-
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# -*-
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# -*-
from . import lrc
import argparse
def newparser(): # TODO: Complete the helping-message of the parser.
    res = argparse.ArgumentParser()
    res.add_argument(
        "--source",
        "-s",
        help = "select the source from which the lyrics are output",
        default = "leoneed"
        )
    return res
def init():
    parser = newparser()
    parsed = parser.parse_args()
    lrc.fortune(parsed.source)