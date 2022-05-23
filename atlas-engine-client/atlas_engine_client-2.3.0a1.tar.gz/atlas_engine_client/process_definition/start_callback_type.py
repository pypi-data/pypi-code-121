from enum import IntEnum

class StartCallbackType(IntEnum):
    ON_PROCESSINSTANCE_CREATED = 1
    ON_PROCESSINSTANCE_FINISHED = 2
    ON_ENDEVENT_REACHED = 3
