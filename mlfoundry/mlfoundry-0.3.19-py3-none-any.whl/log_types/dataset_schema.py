import typing

from mlfoundry.log_types.pydantic_base import PydanticBase


class DatasetSchemaRunLog(PydanticBase):
    value: typing.Dict

    @staticmethod
    def get_log_type() -> str:
        return "dataset/schema"
