# Copyright (c) 2021-2022 Johnathan P. Irvin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from enum import Enum

from .attribute import AttributeEnum


class RightsEnum(Enum):
    AW_WORLD_BOTS_RIGHT = AttributeEnum.AW_WORLD_BOTS_RIGHT.value
    AW_WORLD_BUILD_RIGHT = AttributeEnum.AW_WORLD_BUILD_RIGHT.value
    AW_WORLD_EJECT_RIGHT = AttributeEnum.AW_WORLD_EJECT_RIGHT.value
    AW_WORLD_EMINENT_DOMAIN_RIGHT = AttributeEnum.AW_WORLD_EMINENT_DOMAIN_RIGHT.value
    AW_WORLD_ENTER_RIGHT = AttributeEnum.AW_WORLD_ENTER_RIGHT.value
    AW_WORLD_PUBLIC_SPEAKER_RIGHT = AttributeEnum.AW_WORLD_PUBLIC_SPEAKER_RIGHT.value
    AW_WORLD_SPEAK_RIGHT = AttributeEnum.AW_WORLD_SPEAK_RIGHT.value
    AW_WORLD_SPECIAL_COMMANDS_RIGHT = AttributeEnum.AW_WORLD_SPECIAL_COMMANDS_RIGHT.value
    AW_WORLD_SPECIAL_OBJECTS_RIGHT = AttributeEnum.AW_WORLD_SPECIAL_OBJECTS_RIGHT.value
    AW_WORLD_TERRAIN_RIGHT = AttributeEnum.AW_WORLD_TERRAIN_RIGHT.value
    AW_WORLD_VOIP_RIGHT = AttributeEnum.AW_WORLD_VOIP_RIGHT.value
    AW_WORLD_V4_OBJECTS_RIGHT = AttributeEnum.AW_WORLD_V4_OBJECTS_RIGHT.value
