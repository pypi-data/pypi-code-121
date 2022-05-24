from enum import (
    Enum,
)


class StandStateEnum(Enum):
    """
    Перечисление возможных состояний стендов
    """

    AVAILABLE = 'available'
    UNAVAILABLE = 'unavailable'
    ALL = 'all'


class BuildResultEnum(Enum):
    """
    Перечисление результатов сборок
    """

    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    ABORTED = 'ABORTED'
