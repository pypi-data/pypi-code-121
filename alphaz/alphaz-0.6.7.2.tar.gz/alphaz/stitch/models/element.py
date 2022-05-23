from enum import Enum

class Types(Enum):
    INPUT = "input"

class Element():
    id      = None
    etype   = None
    value   = None

    def __init__(self,id, properties):
        keys        = properties.keys()
        self.id     = id

        self.value  = None if not "value" in keys else properties["value"]
        self.type   = None if not "type" in keys else properties["type"]
