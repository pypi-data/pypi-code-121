from enum import Enum


class StatisticsPeriod(str, Enum):
    ONEDAY = "OneDay"
    FIVEMINUTES = "FiveMinutes"

    def __str__(self) -> str:
        return str(self.value)
