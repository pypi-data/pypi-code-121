from typing import List
from typing import TypedDict

from testlodge.typing.shared import DateTimeStr
from testlodge.typing.shared import Pagination


class PlanJSON(TypedDict):

    id: int
    name: str
    test_plan_identifier: str
    project_id: int
    created_at: DateTimeStr
    updated_at: DateTimeStr


class PlanListJSON(TypedDict):

    pagination: Pagination
    steps: List[PlanJSON]
