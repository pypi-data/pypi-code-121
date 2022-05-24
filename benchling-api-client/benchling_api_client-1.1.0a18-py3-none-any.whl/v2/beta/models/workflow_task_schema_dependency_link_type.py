from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskSchemaDependencyLinkType(Enums.KnownString):
    WORKFLOW_TASK_SCHEMA = "workflow_task_schema"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskSchemaDependencyLinkType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of WorkflowTaskSchemaDependencyLinkType must be a string (encountered: {val})"
            )
        newcls = Enum("WorkflowTaskSchemaDependencyLinkType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskSchemaDependencyLinkType, getattr(newcls, "_UNKNOWN"))
