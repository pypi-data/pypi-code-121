from python_framework import Enum, EnumItem


@Enum()
class ModelStateEnumeration :
    INSTANTIATED = EnumItem()
    PERSISTED = EnumItem()
    MODIFIED = EnumItem()
    PROCESSED = EnumItem()
    NOT_INFORMED = EnumItem()


ModelState = ModelStateEnumeration()
