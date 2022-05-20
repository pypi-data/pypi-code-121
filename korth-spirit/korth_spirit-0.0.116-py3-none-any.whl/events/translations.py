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
from korth_spirit.sdk import AttributeEnum, CallBackEnum, EventEnum

TRANSLATIONS = {
    EventEnum.AW_EVENT_ADMIN_WORLD_DELETE: [
        (int, AttributeEnum.AW_SERVER_ID),
    ],
    EventEnum.AW_EVENT_ADMIN_WORLD_INFO: [
        (int, AttributeEnum.AW_SERVER_ID),
        (int, AttributeEnum.AW_SERVER_INSTANCE),
        (str, AttributeEnum.AW_SERVER_CARETAKERS),
        (bool, AttributeEnum.AW_SERVER_ENABLED),
        (int, AttributeEnum.AW_SERVER_EXPIRATION),
        (int, AttributeEnum.AW_SERVER_MAX_USERS),
        (str, AttributeEnum.AW_SERVER_NAME),
        (int, AttributeEnum.AW_SERVER_OBJECTS),
        (str, AttributeEnum.AW_SERVER_PASSWORD),
        (int, AttributeEnum.AW_SERVER_REGISTRY),
        (int, AttributeEnum.AW_SERVER_SIZE),
        (int, AttributeEnum.AW_SERVER_START_RC),
        (int, AttributeEnum.AW_SERVER_STATE),
        (int, AttributeEnum.AW_SERVER_TERRAIN_NODES),
        (int, AttributeEnum.AW_SERVER_USERS),
    ],
    EventEnum.AW_EVENT_AVATAR_ADD: [
        (int, AttributeEnum.AW_AVATAR_SESSION),
        (str, AttributeEnum.AW_AVATAR_NAME),
        (int, AttributeEnum.AW_AVATAR_X),
        (int, AttributeEnum.AW_AVATAR_Y),
        (int, AttributeEnum.AW_AVATAR_Z),
        (int, AttributeEnum.AW_AVATAR_YAW),
        (int, AttributeEnum.AW_AVATAR_TYPE),
        (int, AttributeEnum.AW_AVATAR_GESTURE),
        (int, AttributeEnum.AW_AVATAR_VERSION),
        (int, AttributeEnum.AW_AVATAR_CITIZEN),
        (int, AttributeEnum.AW_AVATAR_PRIVILEGE),
        (int, AttributeEnum.AW_AVATAR_PITCH),
        (int, AttributeEnum.AW_AVATAR_STATE),
        (str, AttributeEnum.AW_PLUGIN_STRING),
    ],
    EventEnum.AW_EVENT_AVATAR_CHANGE: [
        (int, AttributeEnum.AW_AVATAR_SESSION),
        (str, AttributeEnum.AW_AVATAR_NAME),
        (int, AttributeEnum.AW_AVATAR_X),
        (int, AttributeEnum.AW_AVATAR_Y),
        (int, AttributeEnum.AW_AVATAR_Z),
        (int, AttributeEnum.AW_AVATAR_YAW),
        (int, AttributeEnum.AW_AVATAR_TYPE),
        (int, AttributeEnum.AW_AVATAR_GESTURE),
        (int, AttributeEnum.AW_AVATAR_PITCH),
        (int, AttributeEnum.AW_AVATAR_STATE),
        (int, AttributeEnum.AW_AVATAR_FLAGS),
        (bool, AttributeEnum.AW_AVATAR_LOCK),
        (str, AttributeEnum.AW_PLUGIN_STRING),
    ],
    EventEnum.AW_EVENT_AVATAR_DELETE: [
        (int, AttributeEnum.AW_AVATAR_SESSION),
        (str, AttributeEnum.AW_AVATAR_NAME),
    ],
    EventEnum.AW_EVENT_AVATAR_RELOAD: [
        (int, AttributeEnum.AW_AVATAR_CITIZEN),
        (int, AttributeEnum.AW_AVATAR_SESSION),
    ],
    EventEnum.AW_EVENT_AVATAR_CLICK: [
        (int, AttributeEnum.AW_AVATAR_SESSION),
        (str, AttributeEnum.AW_AVATAR_NAME),
        (int, AttributeEnum.AW_CLICKED_SESSION),
        (str, AttributeEnum.AW_CLICKED_NAME),
    ],
    EventEnum.AW_EVENT_BOTGRAM: [
        (str, AttributeEnum.AW_BOTGRAM_FROM_NAME),
        (int, AttributeEnum.AW_BOTGRAM_FROM),
        (str, AttributeEnum.AW_BOTGRAM_TEXT),
    ],
    EventEnum.AW_EVENT_BOTMENU: [
        (str, AttributeEnum.AW_BOTMENU_FROM_NAME),
        (int, AttributeEnum.AW_BOTMENU_FROM_SESSION),
        (str, AttributeEnum.AW_BOTMENU_QUESTION),
        (str, AttributeEnum.AW_BOTMENU_ANSWER),
    ],
    EventEnum.AW_EVENT_CAMERA: [
    ],
    EventEnum.AW_EVENT_CAV_DEFINITION_CHANGE: [
        (int, AttributeEnum.AW_CAV_CITIZEN),
        (int, AttributeEnum.AW_CAV_SESSION),
    ],
    EventEnum.AW_EVENT_CELL_BEGIN: [
        (int, AttributeEnum.AW_CELL_X),
        (int, AttributeEnum.AW_CELL_Z),
        (int, AttributeEnum.AW_CELL_SEQUENCE),
        (int, AttributeEnum.AW_CELL_SIZE),
    ],
    EventEnum.AW_EVENT_CELL_END: [
    ],
    EventEnum.AW_EVENT_CELL_OBJECT: [
        (int, AttributeEnum.AW_OBJECT_TYPE),
        (int, AttributeEnum.AW_OBJECT_ID),
        (int, AttributeEnum.AW_OBJECT_NUMBER),
        (int, AttributeEnum.AW_OBJECT_OWNER),
        (int, AttributeEnum.AW_OBJECT_BUILD_TIMESTAMP),
        (int, AttributeEnum.AW_OBJECT_X),
        (int, AttributeEnum.AW_OBJECT_Y),
        (int, AttributeEnum.AW_OBJECT_Z),
        (int, AttributeEnum.AW_OBJECT_YAW),
        (int, AttributeEnum.AW_OBJECT_TILT),
        (int, AttributeEnum.AW_OBJECT_ROLL),
        (str, AttributeEnum.AW_OBJECT_MODEL),
        (str, AttributeEnum.AW_OBJECT_DESCRIPTION),
        (str, AttributeEnum.AW_OBJECT_ACTION),
        (bytes, AttributeEnum.AW_OBJECT_DATA),
    ],
    EventEnum.AW_EVENT_CHAT: [
        (str, AttributeEnum.AW_AVATAR_NAME),
        (str, AttributeEnum.AW_CHAT_MESSAGE),
        (int, AttributeEnum.AW_CHAT_TYPE),
        (int, AttributeEnum.AW_CHAT_CITIZEN),
        (int, AttributeEnum.AW_CHAT_SESSION),
    ],
    EventEnum.AW_EVENT_CONSOLE_MESSAGE: [
        (int, AttributeEnum.AW_CONSOLE_RED),
        (int, AttributeEnum.AW_CONSOLE_GREEN),
        (int, AttributeEnum.AW_CONSOLE_BLUE),
        (str, AttributeEnum.AW_CONSOLE_MESSAGE),
        (bool, AttributeEnum.AW_CONSOLE_BOLD),
        (bool, AttributeEnum.AW_CONSOLE_ITALICS),
    ],
    EventEnum.AW_EVENT_CONTACT_STATE: [
    ],
    EventEnum.AW_EVENT_ENTITY_ADD: [
        (int, AttributeEnum.AW_ENTITY_TYPE),
        (int, AttributeEnum.AW_ENTITY_ID),
        (int, AttributeEnum.AW_ENTITY_STATE),
        (int, AttributeEnum.AW_ENTITY_FLAGS),
        (int, AttributeEnum.AW_ENTITY_X),
        (int, AttributeEnum.AW_ENTITY_Y),
        (int, AttributeEnum.AW_ENTITY_Z),
        (int, AttributeEnum.AW_ENTITY_YAW),
        (int, AttributeEnum.AW_ENTITY_PITCH),
        (int, AttributeEnum.AW_ENTITY_ROLL),
        (int, AttributeEnum.AW_ENTITY_OWNER_SESSION),
        (int, AttributeEnum.AW_ENTITY_MODEL_NUM),
        (int, AttributeEnum.AW_ENTITY_OWNER_CITIZEN),
    ],
    EventEnum.AW_EVENT_ENTITY_CHANGE: [
        (int, AttributeEnum.AW_ENTITY_TYPE),
        (int, AttributeEnum.AW_ENTITY_ID),
        (int, AttributeEnum.AW_ENTITY_STATE),
        (int, AttributeEnum.AW_ENTITY_FLAGS),
        (int, AttributeEnum.AW_ENTITY_X),
        (int, AttributeEnum.AW_ENTITY_Y),
        (int, AttributeEnum.AW_ENTITY_Z),
        (int, AttributeEnum.AW_ENTITY_YAW),
        (int, AttributeEnum.AW_ENTITY_PITCH),
        (int, AttributeEnum.AW_ENTITY_ROLL),
        (int, AttributeEnum.AW_ENTITY_OWNER_SESSION),
        (int, AttributeEnum.AW_ENTITY_MODEL_NUM),
    ],
    EventEnum.AW_EVENT_ENTITY_DELETE: [
        (int, AttributeEnum.AW_ENTITY_TYPE),
        (int, AttributeEnum.AW_ENTITY_ID),
    ],
    EventEnum.AW_EVENT_ENTITY_LINKS: [
        (int, AttributeEnum.AW_ENTITY_TYPE),
        (int, AttributeEnum.AW_ENTITY_ID),
    ],
    EventEnum.AW_EVENT_ENTITY_RIDER_ADD: [
        (int, AttributeEnum.AW_ENTITY_TYPE),
        (int, AttributeEnum.AW_ENTITY_ID),
        (int, AttributeEnum.AW_AVATAR_SESSION),
    ],
    EventEnum.AW_EVENT_ENTITY_RIDER_CHANGE: [
        (int, AttributeEnum.AW_ENTITY_TYPE),
        (int, AttributeEnum.AW_ENTITY_ID),
        (int, AttributeEnum.AW_AVATAR_SESSION),
    ],
    EventEnum.AW_EVENT_ENTITY_RIDER_DELETE: [
        (int, AttributeEnum.AW_ENTITY_TYPE),
        (int, AttributeEnum.AW_ENTITY_ID),
        (int, AttributeEnum.AW_AVATAR_SESSION),
    ],
    EventEnum.AW_EVENT_HUD_CLEAR: [
    ],
    EventEnum.AW_EVENT_HUD_CLICK: [
        (int, AttributeEnum.AW_HUD_ELEMENT_SESSION),
        (int, AttributeEnum.AW_HUD_ELEMENT_ID),
        (int, AttributeEnum.AW_HUD_ELEMENT_CLICK_X),
        (int, AttributeEnum.AW_HUD_ELEMENT_CLICK_Y),
    ],
    EventEnum.AW_EVENT_HUD_CREATE: [
    ],
    EventEnum.AW_EVENT_HUD_DESTROY: [
    ],
    EventEnum.AW_EVENT_LASER_BEAM: [
        (int, AttributeEnum.AW_LASER_BEAM_SOURCE_TYPE),
    ],
    EventEnum.AW_EVENT_JOIN: [
    ],
    EventEnum.AW_EVENT_NOISE: [
        (str, AttributeEnum.AW_SOUND_NAME),
    ],
    EventEnum.AW_EVENT_OBJECT_ADD: [
        (int, AttributeEnum.AW_OBJECT_SESSION),
        (int, AttributeEnum.AW_CELL_SEQUENCE),
        (int, AttributeEnum.AW_CELL_X),
        (int, AttributeEnum.AW_CELL_Z),
        (int, AttributeEnum.AW_OBJECT_TYPE),
        (int, AttributeEnum.AW_OBJECT_ID),
        (int, AttributeEnum.AW_OBJECT_NUMBER),
        (int, AttributeEnum.AW_OBJECT_OWNER),
        (int, AttributeEnum.AW_OBJECT_BUILD_TIMESTAMP),
        (int, AttributeEnum.AW_OBJECT_X),
        (int, AttributeEnum.AW_OBJECT_Y),
        (int, AttributeEnum.AW_OBJECT_Z),
        (int, AttributeEnum.AW_OBJECT_YAW),
        (int, AttributeEnum.AW_OBJECT_TILT),
        (int, AttributeEnum.AW_OBJECT_ROLL),
        (str, AttributeEnum.AW_OBJECT_MODEL),
        (str, AttributeEnum.AW_OBJECT_DESCRIPTION),
        (str, AttributeEnum.AW_OBJECT_ACTION),
        (bytes, AttributeEnum.AW_OBJECT_DATA),
    ],
    EventEnum.AW_EVENT_OBJECT_BUMP: [
        (int, AttributeEnum.AW_AVATAR_SESSION),
        (int, AttributeEnum.AW_AVATAR_NAME),
        (int, AttributeEnum.AW_OBJECT_TYPE),
        (int, AttributeEnum.AW_OBJECT_SYNC),
        (int, AttributeEnum.AW_OBJECT_X),
        (int, AttributeEnum.AW_OBJECT_Y),
        (int, AttributeEnum.AW_OBJECT_Z),
        (int, AttributeEnum.AW_OBJECT_YAW),
        (int, AttributeEnum.AW_OBJECT_TILT),
        (int, AttributeEnum.AW_OBJECT_ROLL),
        (int, AttributeEnum.AW_OBJECT_BUILD_TIMESTAMP),
        (int, AttributeEnum.AW_OBJECT_OWNER),
        (str, AttributeEnum.AW_OBJECT_MODEL),
        (str, AttributeEnum.AW_OBJECT_DESCRIPTION),
        (str, AttributeEnum.AW_OBJECT_ACTION),
        (bytes, AttributeEnum.AW_OBJECT_DATA),
    ],
    EventEnum.AW_EVENT_OBJECT_CLICK: [
        (int, AttributeEnum.AW_AVATAR_SESSION),
        (int, AttributeEnum.AW_AVATAR_NAME),
        (int, AttributeEnum.AW_CELL_X),
        (int, AttributeEnum.AW_CELL_Z),
        (int, AttributeEnum.AW_OBJECT_ID),
        (int, AttributeEnum.AW_OBJECT_NUMBER),
        (int, AttributeEnum.AW_OBJECT_TYPE),
        (int, AttributeEnum.AW_OBJECT_SYNC),
        (int, AttributeEnum.AW_OBJECT_X),
        (int, AttributeEnum.AW_OBJECT_Y),
        (int, AttributeEnum.AW_OBJECT_Z),
        (int, AttributeEnum.AW_OBJECT_YAW),
        (int, AttributeEnum.AW_OBJECT_TILT),
        (int, AttributeEnum.AW_OBJECT_ROLL),
        (int, AttributeEnum.AW_OBJECT_BUILD_TIMESTAMP),
        (int, AttributeEnum.AW_OBJECT_OWNER),
        (str, AttributeEnum.AW_OBJECT_MODEL),
        (str, AttributeEnum.AW_OBJECT_DESCRIPTION),
        (str, AttributeEnum.AW_OBJECT_ACTION),
        (bytes, AttributeEnum.AW_OBJECT_DATA),
    ],
    EventEnum.AW_EVENT_OBJECT_DELETE: [
        (int, AttributeEnum.AW_OBJECT_SESSION),
        (int, AttributeEnum.AW_OBJECT_ID),
        (int, AttributeEnum.AW_OBJECT_NUMBER),
        (int, AttributeEnum.AW_CELL_X),
        (int, AttributeEnum.AW_CELL_Z),
        (int, AttributeEnum.AW_CELL_SEQUENCE),
    ],
    EventEnum.AW_EVENT_OBJECT_SELECT: [
        (int, AttributeEnum.AW_AVATAR_SESSION),
        (str, AttributeEnum.AW_AVATAR_NAME),
        (int, AttributeEnum.AW_CELL_X),
        (int, AttributeEnum.AW_CELL_Z),
        (int, AttributeEnum.AW_OBJECT_ID),
        (int, AttributeEnum.AW_OBJECT_NUMBER),
    ],
    EventEnum.AW_EVENT_SEND_FILE: [
    ],
    EventEnum.AW_EVENT_TELEGRAM: [
    ],
    EventEnum.AW_EVENT_TELEPORT: [
        (str, AttributeEnum.AW_TELEPORT_WORLD),
        (int, AttributeEnum.AW_TELEPORT_X),
        (int, AttributeEnum.AW_TELEPORT_Y),
        (int, AttributeEnum.AW_TELEPORT_Z),
        (int, AttributeEnum.AW_TELEPORT_YAW),
        (bool, AttributeEnum.AW_TELEPORT_WARP),
    ],
    EventEnum.AW_EVENT_TERRAIN_BEGIN: [
        (int, AttributeEnum.AW_TERRAIN_PAGE_X),
        (int, AttributeEnum.AW_TERRAIN_PAGE_Z),
    ],
    EventEnum.AW_EVENT_TERRAIN_CHANGED: [
        (int, AttributeEnum.AW_TERRAIN_PAGE_X),
        (int, AttributeEnum.AW_TERRAIN_PAGE_Z),
    ],
    EventEnum.AW_EVENT_TERRAIN_DATA: [
        (int, AttributeEnum.AW_TERRAIN_NODE_X),
        (int, AttributeEnum.AW_TERRAIN_NODE_Z),
        (int, AttributeEnum.AW_TERRAIN_NODE_SIZE),
        (bytes, AttributeEnum.AW_TERRAIN_NODE_TEXTURES),
        (bytes, AttributeEnum.AW_TERRAIN_NODE_HEIGHTS),
    ],
    EventEnum.AW_EVENT_TERRAIN_END: [
        (bool, AttributeEnum.AW_TERRAIN_COMPLETE),
        (int, AttributeEnum.AW_TERRAIN_SEQUENCE),
    ],
    EventEnum.AW_EVENT_TOOLBAR_CLICK: [
        (int, AttributeEnum.AW_TOOLBAR_SESSION),
        (int, AttributeEnum.AW_TOOLBAR_ID),
    ],
    EventEnum.AW_EVENT_UNIVERSE_ATTRIBUTES: [
        (bool, AttributeEnum.AW_UNIVERSE_ALLOW_TOURISTS),
        (str, AttributeEnum.AW_UNIVERSE_ANNUAL_CHARGE),
        (int, AttributeEnum.AW_UNIVERSE_BROWSER_BETA),
        (int, AttributeEnum.AW_UNIVERSE_BROWSER_MINIMUM),
        (int, AttributeEnum.AW_UNIVERSE_BROWSER_RELEASE),
        (int, AttributeEnum.AW_UNIVERSE_BUILD_NUMBER),
        (bool, AttributeEnum.AW_UNIVERSE_CITIZEN_CHANGES_ALLOWED),
        (str, AttributeEnum.AW_UNIVERSE_MONTHLY_CHARGE),
        (int, AttributeEnum.AW_UNIVERSE_REGISTER_METHOD),
        (bool, AttributeEnum.AW_UNIVERSE_REGISTRATION_REQUIRED),
        (int, AttributeEnum.AW_UNIVERSE_SEARCH_URL),
        (int, AttributeEnum.AW_UNIVERSE_TIME),
        (int, AttributeEnum.AW_UNIVERSE_WELCOME_MESSAGE),
        (int, AttributeEnum.AW_UNIVERSE_WORLD_BETA),
        (int, AttributeEnum.AW_UNIVERSE_WORLD_MINIMUM),
        (int, AttributeEnum.AW_UNIVERSE_WORLD_RELEASE),
        (str, AttributeEnum.AW_UNIVERSE_WORLD_START),
        (bool, AttributeEnum.AW_UNIVERSE_USER_LIST_ENABLED),
        (str, AttributeEnum.AW_UNIVERSE_NOTEPAD_URL),
        (str, AttributeEnum.AW_UNIVERSE_CAV_PATH),
        (str, AttributeEnum.AW_UNIVERSE_CAV_PATH2),
    ],
    EventEnum.AW_EVENT_UNIVERSE_DISCONNECT: [
        (int, AttributeEnum.AW_DISCONNECT_REASON),
    ],
    EventEnum.AW_EVENT_URL: [
        (int, AttributeEnum.AW_AVATAR_SESSION),
        (str, AttributeEnum.AW_AVATAR_NAME),
        (str, AttributeEnum.AW_URL_NAME),
        (str, AttributeEnum.AW_URL_POST),
        (str, AttributeEnum.AW_URL_TARGET),
        (bool, AttributeEnum.AW_URL_TARGET_3D),
    ],
    EventEnum.AW_EVENT_URL_CLICK: [
        (str, AttributeEnum.AW_AVATAR_NAME),
        (int, AttributeEnum.AW_AVATAR_SESSION),
        (str, AttributeEnum.AW_URL_NAME),
    ],
    EventEnum.AW_EVENT_USER_INFO: [
        (int, AttributeEnum.AW_USERLIST_ID),
        (str, AttributeEnum.AW_USERLIST_NAME),
        (str, AttributeEnum.AW_USERLIST_WORLD),
        (int, AttributeEnum.AW_USERLIST_CITIZEN),
        (int, AttributeEnum.AW_USERLIST_STATE),
        (str, AttributeEnum.AW_USERLIST_EMAIL),
        (int, AttributeEnum.AW_USERLIST_PRIVILEGE),
        (int, AttributeEnum.AW_USERLIST_ADDRESS),
    ],
    EventEnum.AW_EVENT_WORLD_ATTRIBUTES: [
        (int, AttributeEnum.AW_ATTRIB_SENDER_SESSION),
    ],
    EventEnum.AW_EVENT_WORLD_CAV_DEFINITION_CHANGE: [
        (int, AttributeEnum.AW_CAV_CITIZEN),
        (int, AttributeEnum.AW_CAV_SESSION),
    ],
    EventEnum.AW_EVENT_WORLD_DISCONNECT: [
        (int, AttributeEnum.AW_DISCONNECT_REASON),
    ],
    EventEnum.AW_EVENT_WORLD_INFO: [
        (str, AttributeEnum.AW_WORLDLIST_NAME),
        (int, AttributeEnum.AW_WORLDLIST_USERS),
        (int, AttributeEnum.AW_WORLDLIST_STATUS),
        (int, AttributeEnum.AW_WORLDLIST_RATING),
    ],
    CallBackEnum.AW_CALLBACK_ADDRESS: [
        (int, AttributeEnum.AW_AVATAR_SESSION),
        (int, AttributeEnum.AW_AVATAR_ADDRESS),
    ],
    CallBackEnum.AW_CALLBACK_ADMIN: [
        (int, AttributeEnum.AW_SERVER_BUILD),
        (int, AttributeEnum.AW_WORLD_BUILD_NUMBER),
    ],
    CallBackEnum.AW_CALLBACK_ADMIN_WORLD_LIST: [
        (int, AttributeEnum.AW_SERVER_ID),
    ],
    CallBackEnum.AW_CALLBACK_ADMIN_WORLD_RESULT: [
        (int, AttributeEnum.AW_SERVER_ID),
        (int, AttributeEnum.AW_SERVER_INSTANCE),
        (int, AttributeEnum.AW_SERVER_NAME),
    ],
    CallBackEnum.AW_CALLBACK_ATTRIBUTES_RESET_RESULT: [
    ],
    CallBackEnum.AW_CALLBACK_AVATAR_LOCATION: [
    ],
    CallBackEnum.AW_CALLBACK_BOTGRAM_RESULT: [
    ],
    CallBackEnum.AW_CALLBACK_BOTMENU_RESULT: [
    ],
    CallBackEnum.AW_CALLBACK_CAV: [
        (int, AttributeEnum.AW_CAV_CITIZEN),
        (int, AttributeEnum.AW_CAV_SESSION),
        (int, AttributeEnum.AW_CAV_DEFINITION),
    ],
    CallBackEnum.AW_CALLBACK_CAV_RESULT: [
        (int, AttributeEnum.AW_CAV_CITIZEN),
        (int, AttributeEnum.AW_CAV_SESSION),
    ],
    CallBackEnum.AW_CALLBACK_CELL_RESULT: [
        (int, AttributeEnum.AW_CELL_ITERATOR),
    ],
    CallBackEnum.AW_CALLBACK_CITIZEN_ATTRIBUTES: [
        (int, AttributeEnum.AW_CITIZEN_NUMBER),
        (int, AttributeEnum.AW_CITIZEN_NAME),
        (int, AttributeEnum.AW_CITIZEN_PASSWORD),
        (int, AttributeEnum.AW_CITIZEN_EMAIL),
        (int, AttributeEnum.AW_CITIZEN_ENABLED),
        (int, AttributeEnum.AW_CITIZEN_BETA),
        (int, AttributeEnum.AW_CITIZEN_TRIAL),
        (int, AttributeEnum.AW_CITIZEN_CAV_ENABLED),
        (int, AttributeEnum.AW_CITIZEN_PAV_ENABLED),
        (int, AttributeEnum.AW_CITIZEN_BOT_LIMIT),
        (int, AttributeEnum.AW_CITIZEN_COMMENT),
        (int, AttributeEnum.AW_CITIZEN_EXPIRATION_TIME),
        (int, AttributeEnum.AW_CITIZEN_IMMIGRATION_TIME),
        (int, AttributeEnum.AW_CITIZEN_LAST_LOGIN),
        (int, AttributeEnum.AW_CITIZEN_PRIVILEGE_PASSWORD),
        (int, AttributeEnum.AW_CITIZEN_PRIVACY),
        (int, AttributeEnum.AW_CITIZEN_TOTAL_TIME),
        (int, AttributeEnum.AW_CITIZEN_URL),
    ],
    CallBackEnum.AW_CALLBACK_CITIZEN_RESULT: [
        (int, AttributeEnum.AW_CITIZEN_NUMBER),
    ],
    CallBackEnum.AW_CALLBACK_CREATE: [
    ],
    CallBackEnum.AW_CALLBACK_DELETE_ALL_OBJECTS_RESULT: [
    ],
    CallBackEnum.AW_CALLBACK_ENTER: [
        (int, AttributeEnum.AW_WORLD_NAME),
    ],
    CallBackEnum.AW_CALLBACK_HUD_RESULT: [
        (int, AttributeEnum.AW_HUD_ELEMENT_SESSION),
        (int, AttributeEnum.AW_HUD_ELEMENT_ID),
    ],
    CallBackEnum.AW_CALLBACK_LICENSE_ATTRIBUTES: [
        (int, AttributeEnum.AW_LICENSE_PASSWORD),
        (int, AttributeEnum.AW_LICENSE_USERS),
        (int, AttributeEnum.AW_LICENSE_RANGE),
        (int, AttributeEnum.AW_LICENSE_EMAIL),
        (int, AttributeEnum.AW_LICENSE_COMMENT),
        (int, AttributeEnum.AW_LICENSE_CREATION_TIME),
        (int, AttributeEnum.AW_LICENSE_EXPIRATION_TIME),
        (int, AttributeEnum.AW_LICENSE_LAST_START),
        (int, AttributeEnum.AW_LICENSE_LAST_ADDRESS),
        (int, AttributeEnum.AW_LICENSE_HIDDEN),
        (int, AttributeEnum.AW_LICENSE_ALLOW_TOURISTS),
        (int, AttributeEnum.AW_LICENSE_VOIP),
        (int, AttributeEnum.AW_LICENSE_PLUGINS),
    ],
    CallBackEnum.AW_CALLBACK_LICENSE_RESULT: [
    ],
    CallBackEnum.AW_CALLBACK_LOGIN: [
        (int, AttributeEnum.AW_CITIZEN_BETA),
        (int, AttributeEnum.AW_CITIZEN_CAV_ENABLED),
        (int, AttributeEnum.AW_CITIZEN_NAME),
        (int, AttributeEnum.AW_CITIZEN_NUMBER),
        (int, AttributeEnum.AW_CITIZEN_PAV_ENABLED),
        (int, AttributeEnum.AW_CITIZEN_TIME_LEFT),
        (int, AttributeEnum.AW_LOGIN_PRIVILEGE_NAME),
    ],
    CallBackEnum.AW_CALLBACK_OBJECT_QUERY: [
        (int, AttributeEnum.AW_OBJECT_TYPE),
        (int, AttributeEnum.AW_OBJECT_ID),
        (int, AttributeEnum.AW_OBJECT_NUMBER),
        (int, AttributeEnum.AW_OBJECT_OWNER),
        (int, AttributeEnum.AW_OBJECT_BUILD_TIMESTAMP),
        (int, AttributeEnum.AW_OBJECT_X),
        (int, AttributeEnum.AW_OBJECT_Y),
        (int, AttributeEnum.AW_OBJECT_Z),
        (int, AttributeEnum.AW_OBJECT_YAW),
        (int, AttributeEnum.AW_OBJECT_TILT),
        (int, AttributeEnum.AW_OBJECT_ROLL),
        (int, AttributeEnum.AW_OBJECT_MODEL),
        (int, AttributeEnum.AW_OBJECT_DESCRIPTION),
        (int, AttributeEnum.AW_OBJECT_ACTION),
        (int, AttributeEnum.AW_OBJECT_DATA),
    ],
    CallBackEnum.AW_CALLBACK_OBJECT_RESULT: [
        (int, AttributeEnum.AW_OBJECT_NUMBER),
        (int, AttributeEnum.AW_OBJECT_ID),
        (int, AttributeEnum.AW_OBJECT_CALLBACK_REFERENCE),
        (int, AttributeEnum.AW_CELL_X),
        (int, AttributeEnum.AW_CELL_Z),
    ],
    CallBackEnum.AW_CALLBACK_QUERY: [
        (int, AttributeEnum.AW_QUERY_COMPLETE),
    ],
    CallBackEnum.AW_CALLBACK_RELOAD_REGISTRY: [
    ],
    CallBackEnum.AW_CALLBACK_TERRAIN_DELETE_ALL_RESULT: [
    ],
    CallBackEnum.AW_CALLBACK_TERRAIN_LOAD_NODE_RESULT: [
    ],
    CallBackEnum.AW_CALLBACK_TERRAIN_NEXT_RESULT: [
        (int, AttributeEnum.AW_TERRAIN_COMPLETE),
    ],
    CallBackEnum.AW_CALLBACK_TERRAIN_SET_RESULT: [
        (int, AttributeEnum.AW_TERRAIN_X),
        (int, AttributeEnum.AW_TERRAIN_Z),
    ],
    CallBackEnum.AW_CALLBACK_UNIVERSE_EJECTION: [
        (int, AttributeEnum.AW_EJECTION_ADDRESS),
        (int, AttributeEnum.AW_EJECTION_CREATION_TIME),
        (int, AttributeEnum.AW_EJECTION_EXPIRATION_TIME),
        (int, AttributeEnum.AW_EJECTION_COMMENT),
    ],
    CallBackEnum.AW_CALLBACK_UNIVERSE_EJECTION_RESULT: [
    ],
    CallBackEnum.AW_CALLBACK_USER_LIST: [
        (int, AttributeEnum.AW_USERLIST_MORE)
    ],
    CallBackEnum.AW_CALLBACK_WORLD_CAV: [
        (int, AttributeEnum.AW_CAV_CITIZEN),
        (int, AttributeEnum.AW_CAV_SESSION),
        (int, AttributeEnum.AW_CAV_DEFINITION),
    ],
    CallBackEnum.AW_CALLBACK_WORLD_CAV_RESULT: [
        (int, AttributeEnum.AW_CAV_CITIZEN),
        (int, AttributeEnum.AW_CAV_SESSION),
    ],
    CallBackEnum.AW_CALLBACK_WORLD_EJECTION: [
        (int, AttributeEnum.AW_EJECTION_TYPE),
        (int, AttributeEnum.AW_EJECTION_ADDRESS),
        (int, AttributeEnum.AW_EJECTION_CREATION_TIME),
        (int, AttributeEnum.AW_EJECTION_EXPIRATION_TIME),
        (int, AttributeEnum.AW_EJECTION_COMMENT),
    ],
    CallBackEnum.AW_CALLBACK_WORLD_EJECTION_RESULT: [
    ],
    CallBackEnum.AW_CALLBACK_WORLD_INSTANCE: [
        (int, AttributeEnum.AW_AVATAR_CITIZEN),
        (int, AttributeEnum.AW_AVATAR_WORLD_INSTANCE),
    ],
    CallBackEnum.AW_CALLBACK_WORLD_LIST: [
        (int, AttributeEnum.AW_WORLDLIST_MORE),
    ],
}
