from python_framework import Enum, EnumItem


@Enum()
class ModelStatusEnumeration :
    ACCEPTED = EnumItem()
    PROCESSING = EnumItem()
    PROCESSED = EnumItem()
    PROCESSED_WITH_ERRORS = EnumItem()
    UNPROCESSED = EnumItem()
    DELIVERED = EnumItem()
    ERROR = EnumItem()
    NOT_INFORMED = EnumItem()


ModelStatus = ModelStatusEnumeration()
