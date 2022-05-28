import enum
import typing

from mlfoundry.log_types.pydantic_base import PydanticBase


class StatsSource(enum.Enum):
    WHYLOGS = "WHYLOGS"


class DatasetStatsRunLog(PydanticBase):
    value: typing.Dict
    stats_source: StatsSource

    @staticmethod
    def get_log_type() -> str:
        return "dataset/stats"
