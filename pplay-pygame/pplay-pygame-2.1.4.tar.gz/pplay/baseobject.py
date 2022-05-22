# coding= utf-8

"""The most basic game class"""


class BaseObject:
    """Creates a BaseObject in X, Y co-ords, with Width x Height"""

    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0


class BaseRectObject(BaseObject):
    """Creates a BaseRectObject in X, Y co-ords, with Width x Height"""

    def __init__(self):
        super(BaseRectObject, self).__init__()
        self.rect = None
        self.image = None
