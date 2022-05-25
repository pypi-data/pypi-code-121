import enum


class StrEnum(enum.Enum):
    def __str__(self):
        return self.name


class MetaEnum(enum.EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class EnumExtension(StrEnum, metaclass=MetaEnum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
