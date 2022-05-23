from typing import List
from typing import Optional
from typing import TypedDict

from testlodge.typing.shared import DateTimeStr
from testlodge.typing.shared import Pagination


class RunJSON(TypedDict):

    id: int
    name: str
    incomplete_number: int
    passed_number: int
    skipped_number: int
    failed_number: int
    user_id: Optional[int]
    project_id: int
    executed_plan_id: Optional[int]
    created_at: DateTimeStr
    updated_at: DateTimeStr


class RunListJSON(TypedDict):

    pagination: Pagination
    steps: List[RunJSON]
