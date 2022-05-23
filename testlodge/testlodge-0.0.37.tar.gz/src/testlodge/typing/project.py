from typing import List
from typing import TypedDict

from testlodge.typing.shared import DateTimeStr
from testlodge.typing.shared import Pagination


class ProjectJSON(TypedDict):

    id: int
    name: str
    description: str
    issue_tracker_credential_id: int
    issue_tracker_project_id: str
    created_at: DateTimeStr
    updated_at: DateTimeStr


class ProjectListJSON(TypedDict):

    pagination: Pagination
    steps: List[ProjectJSON]
