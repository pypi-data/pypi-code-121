import enum
import random


auto = enum.auto


class AutoNameEnumMeta(enum.EnumMeta):
    def __contains__(cls, member):
        if isinstance(member, str):
            return member in cls.__members__.keys()
        else:
            super().__contains__(member)


class AutoNameEnum(str, enum.Enum, metaclass=AutoNameEnumMeta):
    """
    An implementation of enum that automatically assigns the value of each item to its name.

    Example:
        class Pets(AutoNameEnum):
            DOG = auto()
            CAT = auto()

        >> fido = Pets.DOG
        >> print(fido)
        'DOG'

    Note:
        This class inherits from str as well as Enum so that it will be properly
        presented by swagger when used in api apps.
    """

    def _generate_next_value_(name: str, *_):  # type: ignore
        return name

    def __str__(self):
        return self.value

    @classmethod
    def rando(cls, *_):
        return random.choice([e for e in cls])

    @classmethod
    def pretty_list(cls):
        return ", ".join(str(e) for e in cls)
