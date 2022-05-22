from enum import (
    Enum,
)


class BranchEnum(Enum):
    """
    Перечисление основных веток
    """
    DEV = 'dev'
    TEST = 'test'
    DEFAULT = 'default'
    MASTER = 'master'

    @classmethod
    def get_all_str(cls):
        """
        Все ветки
        """
        return (
            cls.DEV.value,
            cls.TEST.value,
            cls.DEFAULT.value,
            cls.MASTER.value,
        )

    @classmethod
    def get_branches_weight(cls):
        """
        Возвращает веса веток
        """
        return {
            cls.DEV: 1,
            cls.TEST: 2,
            cls.DEFAULT: 3,
            cls.MASTER: 4,
        }

    def weight(self):
        """
        Возвращает вес ветки
        """
        return self.get_branches_weight()[self]
