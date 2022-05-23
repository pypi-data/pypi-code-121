from typing import List
from typing import TypedDict

from testlodge.typing.shared import DateTimeStr
from testlodge.typing.shared import Pagination


class UserJSON(TypedDict):

    id: int
    firstname: str
    lastname: str
    email: str
    created_at: DateTimeStr
    updated_at: DateTimeStr


class UserListJSON(TypedDict):

    pagination: Pagination
    users: List[UserJSON]
