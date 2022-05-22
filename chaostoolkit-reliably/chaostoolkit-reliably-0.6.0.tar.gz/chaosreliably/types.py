from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, parse_obj_as

try:
    import ujson as jsonlib
except ImportError:
    try:
        import simplejson as jsonlib  # type: ignore
    except ImportError:
        import json as jsonlib  # type: ignore


OPTIONAL_DICT_LIST = Optional[List[Dict[str, Any]]]
RELATED_TO = Field(alias="relatedTo", default=[])


class BaseModel(PydanticBaseModel):
    class Config:
        allow_population_by_field_name = True
        use_enum_values = True
        json_loads = jsonlib.loads
        json_dumps = jsonlib.dumps


class ObjectiveResultMetadata(BaseModel):
    labels: Dict[str, str]
    annotations: Optional[Dict[str, str]]
    related_to: Optional[List[Dict[str, Any]]] = Field(alias="relatedTo")


class ObjectiveResultSpec(BaseModel):
    indicator_selector: Dict[str, str] = Field(alias="indicatorSelector")
    objective_percent: float = Field(alias="objectivePercent")
    actual_percent: float = Field(alias="actualPercent")
    remaining_percent: float = Field(alias="remainingPercent")


class ObjectiveResult(BaseModel):
    id: str
    metadata: ObjectiveResultMetadata
    spec: ObjectiveResultSpec

    def parse_list(obj: Any) -> "List[ObjectiveResult]":
        return parse_obj_as(List[ObjectiveResult], obj)


class EventType(Enum):
    ACTIVITY_END = "ACTIVITY_END"
    ACTIVITY_START = "ACTIVITY_START"
    EXPERIMENT_END = "EXPERIMENT_END"
    EXPERIMENT_START = "EXPERIMENT_START"
    HYPOTHESIS_END = "HYPOTHESIS_END"
    HYPOTHESIS_START = "HYPOTHESIS_START"
    METHOD_END = "METHOD_END"
    METHOD_START = "METHOD_START"
    ROLLBACK_END = "ROLLBACK_END"
    ROLLBACK_START = "ROLLBACK_START"


class ExperimentLabels(BaseModel):
    ref: str = Field(alias="experiment_ref")


class ExperimentMetadata(BaseModel):
    labels: ExperimentLabels
    annotations: Optional[Dict[str, str]]
    related_to: Optional[List[Dict[str, str]]] = Field(alias="relatedTo")


class ExperimentSpec(BaseModel):
    experiment: Optional[Any]


class ExperimentEntity(BaseModel):
    metadata: ExperimentMetadata
    spec: Optional[ExperimentSpec]


class ExperimentRunLabels(BaseModel):
    ref: str = Field(alias="experiment_run_ref")
    experiment_ref: str = Field(alias="experiment_ref")


class ExperimentRunMetadata(BaseModel):
    labels: ExperimentRunLabels
    annotations: Optional[Dict[str, str]]
    related_to: Optional[List[Dict[str, str]]] = Field(alias="relatedTo")


class ExperimentRunSpec(BaseModel):
    experiment: Optional[Any]
    result: Optional[Any]


class ExperimentRunEntity(BaseModel):
    metadata: ExperimentRunMetadata
    spec: Optional[ExperimentRunSpec]


class ExperimentRunEventLabels(BaseModel):
    event_type: EventType = Field(alias="experiment_run_event_type")
    ref: str = Field(alias="experiment_run_event_ref")
    experiment_run_ref: str = Field(alias="experiment_run_ref")
    experiment_ref: str = Field(alias="experiment_ref")


class ExperimentRunEventMetadata(BaseModel):
    labels: ExperimentRunEventLabels
    annotations: Dict[str, Optional[str]]
    related_to: Optional[List[Dict[str, str]]] = Field(alias="relatedTo")


class ExperimentRunEventSpec(BaseModel):
    result: Optional[Any]


class ExperimentRunEventEntity(BaseModel):
    metadata: ExperimentRunEventMetadata
    spec: Optional[ExperimentRunEventSpec]


class ObjectiveMetadata(BaseModel):
    labels: Dict[str, str]
    annotations: Optional[Dict[str, str]]
    related_to: Optional[List[Dict[str, str]]] = Field(alias="relatedTo")


class ObjectiveSpec(BaseModel):
    selector: Dict[str, str] = Field(alias="indicatorSelector")
    target: float = Field(alias="objectivePercent")
    window: str


class ObjectiveEntity(BaseModel):
    metadata: ObjectiveMetadata
    spec: ObjectiveSpec


class ObjectiveEntities(BaseModel):
    __root__: List[ObjectiveEntity]

    def parse_list(obj: Any) -> "List[ObjectiveEntity]":
        return parse_obj_as(List[ObjectiveEntity], obj)
