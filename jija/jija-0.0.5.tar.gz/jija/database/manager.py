from tortoise.manager import Manager as TortoiseManager, QuerySet


class Manager(TortoiseManager, QuerySet):
    def __init__(self):
        super().__init__()
