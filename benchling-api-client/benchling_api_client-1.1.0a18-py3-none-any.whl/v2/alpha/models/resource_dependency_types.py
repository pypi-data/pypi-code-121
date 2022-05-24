from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ResourceDependencyTypes(Enums.KnownString):
    AA_SEQUENCE = "aa_sequence"
    BOX = "box"
    CONTAINER = "container"
    CUSTOM_ENTITY = "custom_entity"
    DNA_OLIGO = "dna_oligo"
    DNA_SEQUENCE = "dna_sequence"
    ENTRY = "entry"
    FOLDER = "folder"
    LOCATION = "location"
    MIXTURE = "mixture"
    PLATE = "plate"
    PROJECT = "project"
    REGISTRY = "registry"
    WORKFLOW_TASK_STATUS = "workflow_task_status"
    WORKLIST = "worklist"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ResourceDependencyTypes":
        if not isinstance(val, str):
            raise ValueError(f"Value of ResourceDependencyTypes must be a string (encountered: {val})")
        newcls = Enum("ResourceDependencyTypes", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ResourceDependencyTypes, getattr(newcls, "_UNKNOWN"))
