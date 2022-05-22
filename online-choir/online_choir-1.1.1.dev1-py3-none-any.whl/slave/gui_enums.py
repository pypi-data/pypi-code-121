from enum import Enum


class GuiEvent(Enum):
    SESSION_STARTS = 1
    SETTINGS_BUTTON = 2
    GUI_READY = 3


class GuiState(Enum):
    CONNECTING = 0
    READY = 1
    PLAYING = 2
    SETTINGS = 3
    DISCONNECTED = 4
    DEAD = 5
    ERROR = 6
