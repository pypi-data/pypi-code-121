from typing import List
from typing import TypedDict


class CustomFieldJSON(TypedDict):

    id: int
    name: str
    value: str


class CustomFieldListJSON(TypedDict):

    plan_content_custom_fields: List[CustomFieldJSON]
    requirement_custom_fields: List[CustomFieldJSON]
    step_custom_fields: List[CustomFieldJSON]
    executed_step_custom_fields: List[CustomFieldJSON]
