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


class CallBackEnum(Enum):
    AW_CALLBACK_CREATE = 0
    AW_CALLBACK_LOGIN = auto()
    AW_CALLBACK_ENTER = auto()
    AW_CALLBACK_OBJECT_RESULT = auto()
    AW_CALLBACK_LICENSE_ATTRIBUTES = auto()
    AW_CALLBACK_LICENSE_RESULT = auto()
    AW_CALLBACK_CITIZEN_ATTRIBUTES = auto()
    AW_CALLBACK_CITIZEN_RESULT = auto()
    AW_CALLBACK_QUERY = auto()
    AW_CALLBACK_WORLD_LIST = auto()
    AW_CALLBACK_SEND_FILE = auto()
    AW_CALLBACK_JOIN = auto()
    AW_CALLBACK_PASSWORD_SEND = auto()
    AW_CALLBACK_IMMIGRATE = auto()
    AW_CALLBACK_REGISTER = auto()
    AW_CALLBACK_UNIVERSE_EJECTION = auto()
    AW_CALLBACK_UNIVERSE_EJECTION_RESULT = auto()
    AW_CALLBACK_ADDRESS = auto()
    AW_CALLBACK_WORLD_EJECTION = auto()
    AW_CALLBACK_WORLD_EJECTION_RESULT = auto()
    AW_CALLBACK_ADMIN_WORLD_LIST = auto()
    AW_CALLBACK_ADMIN_WORLD_RESULT = auto()
    AW_CALLBACK_DELETE_ALL_OBJECTS_RESULT = auto()
    AW_CALLBACK_CELL_RESULT = auto()
    AW_CALLBACK_RELOAD_REGISTRY = auto()
    AW_CALLBACK_ATTRIBUTES_RESET_RESULT = auto()
    AW_CALLBACK_ADMIN = auto()
    AW_CALLBACK_CONTACT_ADD = auto()
    AW_CALLBACK_TELEGRAM_RESULT = auto()
    AW_CALLBACK_TERRAIN_SET_RESULT = auto()
    AW_CALLBACK_TERRAIN_NEXT_RESULT = auto()
    AW_CALLBACK_TERRAIN_DELETE_ALL_RESULT = auto()
    AW_CALLBACK_TERRAIN_LOAD_NODE_RESULT = auto()
    AW_CALLBACK_BOTGRAM_RESULT = auto()
    AW_CALLBACK_USER_LIST = auto()
    AW_CALLBACK_BOTMENU_RESULT = auto()
    AW_CALLBACK_CAV = auto()
    AW_CALLBACK_CAV_RESULT = auto()
    AW_CALLBACK_WORLD_INSTANCE = auto()
    AW_CALLBACK_HUD_RESULT = auto()
    AW_CALLBACK_AVATAR_LOCATION = auto()
    AW_CALLBACK_OBJECT_QUERY = auto()
    AW_CALLBACK_WORLD_CAV_RESULT = auto()
    AW_CALLBACK_WORLD_CAV = auto()
    AW_CALLBACK_XFER_LOGIN = auto()
    AW_CALLBACK_XFER_REQUEST_SHOW_REPLY = auto()
    AW_CALLBACK_CAV_TEMPLATE_RESULT = auto()
    AW_CALLBACK_SHOPITEM_ATTRIBUTES = auto()
    AW_CALLBACK_SHOPITEM_RESULT = auto()
    AW_CALLBACK_SHOPITEM_QUERY = auto()
    AW_CALLBACK_SHOPTRANS_TOTAL = auto()
    AW_CALLBACK_SHOPTRANS_RESULT = auto()
    AW_CALLBACK_SHOPTRANS_BUY_RESULT = auto()
    AW_CALLBACK_SHOPTRANS_LIST = auto()
    AW_CALLBACK_PURCHASE_RESULT = auto()
    AW_CALLBACK_SHOPITEM_LIST = auto()
    AW_CALLBACK_CITIZEN_TITLE_RESULT = auto()
    AW_MAX_CALLBACK = auto()
