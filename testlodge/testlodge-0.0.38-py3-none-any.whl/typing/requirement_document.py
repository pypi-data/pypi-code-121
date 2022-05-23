from typing import List
from typing import TypedDict

from testlodge.typing.shared import DateTimeStr
from testlodge.typing.shared import Pagination


class RequirementDocumentJSON(TypedDict):

    id: int
    title: str
    should_version: bool
    project_id: int
    created_at: DateTimeStr
    updated_at: DateTimeStr


class RequirementDocumentListJSON(TypedDict):

    pagination: Pagination
    requirement_documents: List[RequirementDocumentJSON]
