from typing import List
from typing import Optional
from typing import TypedDict

from testlodge.typing.shared import DateTimeStr
from testlodge.typing.shared import Pagination


class SuiteJSON(TypedDict):

    id: int
    name: str
    plan_id: Optional[int]
    project_id: int
    created_at: DateTimeStr
    updated_at: DateTimeStr


class SuiteListJSON(TypedDict):

    pagination: Pagination
    suites: List[SuiteJSON]
