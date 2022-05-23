from enum import Enum


class OrderedEnum(Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __str__(self):
        return self.name.split('.')[-1]


    @classmethod
    def from_str(cls, text, case_sensitive=False):
        if case_sensitive:
            items = [item for item in dir(cls) if not item.startswith('_')]
            if text in items:
                return getattr(cls, text)
            return None
        else:
            for item in dir(cls):
                if item.startswith('_'): continue
                if text.lower() == item.lower(): 
                    return getattr(cls, item)
            return None