from enum import (
    Enum,
)


class JiraCustomFieldEnum(Enum):
    """
    Перечисление кастомных полей задач в Jira
    """

    ADDRESS_BUILD_SLICING_DB = 'customfield_18600'
    STATUS_BUILD_SLICING_DB = 'customfield_18601'


class JiraBuildSlicingDBStatusEnum(Enum):
    """
    Перечисление статусов сборок срезов БД в Jira
    """

    RUNNING = 'Запущена'
    FINISHED = 'Завершена'
    FINISHED_WITH_WARNINGS = 'Завершена с предупреждениями'
    BROKEN = 'Завершена с ошибками'
    ABORTED = 'Остановлена'
    STAND_UNAVAILABLE = 'Указанный тестовый стенд недоступен'
    CAN_NOT_PARSE_STAND_URL_AND_ENT_ID = 'Не удалось считать URL тестового стенда или идентификатор учреждения'


class JiraIssueStatusEnum(Enum):
    """
    Перечисление статусов задач в Jira
    """

    CLOSED = 'Закрыт'
