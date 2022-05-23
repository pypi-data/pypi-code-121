from typing import List
from typing import Optional
from typing import TypedDict

from testlodge.typing.custom_field import CustomFieldJSON
from testlodge.typing.requirement_document import RequirementDocumentJSON
from testlodge.typing.shared import DateTimeStr
from testlodge.typing.shared import Pagination
from testlodge.typing.user import UserJSON


class CaseJSON(TypedDict):

    id: int
    project_id: int
    suite_section_id: int
    position: int
    last_saved_by_id: int
    last_saved_by: UserJSON
    created_at: DateTimeStr
    updated_at: DateTimeStr
    custom_fields: List[CustomFieldJSON]
    requirements: List[RequirementDocumentJSON]
    step_number: str
    title: str
    description: Optional[str]
    test_steps: Optional[str]
    expected_result: Optional[str]


class CaseListJSON(TypedDict):

    pagination: Pagination
    steps: List[CaseJSON]
