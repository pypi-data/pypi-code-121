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
from enum import Enum, auto


class EventEnum(Enum):
    AW_EVENT_AVATAR_ADD = 0
    AW_EVENT_AVATAR_CHANGE = auto()
    AW_EVENT_AVATAR_DELETE = auto()
    AW_EVENT_CELL_BEGIN = auto()
    AW_EVENT_CELL_OBJECT = auto()
    AW_EVENT_CELL_END = auto()
    AW_EVENT_CHAT = auto()
    AW_EVENT_OBJECT_ADD = auto()
    AW_EVENT_OBJECT_DELETE = auto()
    AW_EVENT_UNIVERSE_ATTRIBUTES = auto()
    AW_EVENT_UNIVERSE_DISCONNECT = auto()
    AW_EVENT_WORLD_ATTRIBUTES = auto()
    AW_EVENT_WORLD_INFO = auto()
    AW_EVENT_WORLD_DISCONNECT = auto()
    AW_EVENT_SEND_FILE = auto()
    AW_EVENT_CONTACT_STATE = auto()
    AW_EVENT_TELEGRAM = auto()
    AW_EVENT_JOIN = auto()
    AW_EVENT_OBJECT_CLICK = auto()
    AW_EVENT_OBJECT_SELECT = auto()
    AW_EVENT_AVATAR_CLICK = auto()
    AW_EVENT_URL = auto()
    AW_EVENT_URL_CLICK = auto()
    AW_EVENT_TELEPORT = auto()
    AW_EVENT_ADMIN_WORLD_INFO = auto()
    AW_EVENT_ADMIN_WORLD_DELETE = auto()
    AW_EVENT_TERRAIN_BEGIN = auto()
    AW_EVENT_TERRAIN_DATA = auto()
    AW_EVENT_TERRAIN_END = auto()
    AW_EVENT_CONSOLE_MESSAGE = auto()
    AW_EVENT_TERRAIN_CHANGED = auto()
    AW_EVENT_BOTGRAM = auto()
    AW_EVENT_TOOLBAR_CLICK = auto()
    AW_EVENT_USER_INFO = auto()
    AW_EVENT_VOIP_DATA = auto()
    AW_EVENT_NOISE = auto()
    AW_EVENT_CAMERA = auto()
    AW_EVENT_BOTMENU = auto()
    AW_EVENT_OBJECT_BUMP = auto()
    AW_EVENT_ENTITY_ADD = auto()
    AW_EVENT_ENTITY_CHANGE = auto()
    AW_EVENT_ENTITY_DELETE = auto()
    AW_EVENT_ENTITY_RIDER_ADD = auto()
    AW_EVENT_ENTITY_RIDER_DELETE = auto()
    AW_EVENT_ENTITY_RIDER_CHANGE = auto()
    AW_EVENT_AVATAR_RELOAD = auto()
    AW_EVENT_ENTITY_LINKS = auto()
    AW_EVENT_HUD_CLICK = auto()
    AW_EVENT_HUD_CREATE = auto()
    AW_EVENT_HUD_DESTROY = auto()
    AW_EVENT_HUD_CLEAR = auto()
    AW_EVENT_CAV_DEFINITION_CHANGE = auto()
    AW_EVENT_WORLD_CAV_DEFINITION_CHANGE = auto()
    AW_EVENT_XFER_DISCONNECT = auto()
    AW_EVENT_XFER_OFFER = auto()
    AW_EVENT_XFER_REPLY = auto()
    AW_EVENT_XFER_SEND = auto()
    AW_EVENT_XFER_REQUEST = auto()
    AW_EVENT_XFER_CANCEL = auto()
    AW_EVENT_LASER_BEAM = auto()
    AW_EVENT_XFER_QUERY = auto()
    AW_EVENT_CAV_TEMPLATE_CHANGE = auto()
    AW_EVENT_PURCHASE_OFFER = auto()
    AW_EVENT_DIALOG = auto()
    AW_EVENT_DIALOG_ANSWER = auto()
    AW_EVENT_TELEGRAM_PENDING = auto()
    AW_EVENT_TELEGRAM_JOURNAL = auto()
