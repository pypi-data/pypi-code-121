# (Processing of Lyrics)
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
from . import data
import random, time, re
class Constants(object):
    PATTERN_DOT = re.compile("\.")
    STR_BASE = "\x1b[%s;3%sm%s\x1b[0m"
    STR_BASE_L = STR_BASE % (1, "%s", "%s")
rs = random.Random(time.localtime().tm_sec)
def display(item: dict):
    print()
    enders = []
    for each in item["content"]:
        if isinstance(each, str):
            enders.append("\n")
            print(each)
        else:
            enders.append(each[2] if len(each) >= 3 else "\n")
            print(Constants.STR_BASE_L % (each[0], each[1]), end=enders[-1])
    print()
    if "translation" in item:
        assert len(item["content"]) == len(item["translation"])
        k = 0
        for each in item["translation"]:
            print(each, end=enders[0])
            k += 1
        print()
    authorstring = " " * 8 + "---- %s %s" % (item["author"] if isinstance(item["author"], str) else " ".join(item["author"]), Constants.STR_BASE_L % (6, item["title"]))
    print(authorstring)
    if "vocal" in item:
        featvocal = " " * 4 + "featuring: %s" % (item["vocal"] if isinstance(item["vocal"], str) else ", ".join(item["vocal"]))
        for k_line in range(len(featvocal) // len(authorstring) + 1):
            print(featvocal[ k_line * len(authorstring) : (k_line + 1) * len(authorstring) ])
    print()
    return item
def fortune(source: str):
    source = Constants.PATTERN_DOT.split(source)
    lrclist = data.LRC_SOURCE_MAP[source[0]]
    for k in range(1, len(source)):
        if source[k] in lrclist.keys():
            lrclist = lrclist[source[k]]
    lrclist = lrclist.lyrics
    lrcitem = rs.choice(lrclist)
    return display(lrcitem)