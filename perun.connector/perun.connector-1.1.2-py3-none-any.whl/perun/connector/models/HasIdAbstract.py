import abc


class HasIdAbstract(metaclass=abc.ABCMeta):
    def __init__(self, id: int):
        self.id = id

    def __eq__(self, other):
        if isinstance(other, HasIdAbstract):
            return self.id == other.id
        return False
