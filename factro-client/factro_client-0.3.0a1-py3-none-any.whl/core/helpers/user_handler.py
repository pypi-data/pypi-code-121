from typing import Optional

from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, Undefined

from .base_handler import BaseHandler

@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class User:
    id: str
    mandant_id: str
    account_id: str
    anonymized: bool
    employee_number: int
    is_active: bool
    security_group: str
    user_name: str
    city: Optional[str] = ''
    email_address: Optional[str] = ''
    street: Optional[str] = ''
    zip_code: Optional[str] = ''
    first_name: Optional[str] = ''
    last_name: Optional[str] = ''
    salutation: Optional[str] = ''

class UserHandler(BaseHandler):

    def __init__(self, url: str, api_key: str):
        super(UserHandler, self).__init__(url, api_key)

    def get_user_by_id(self, user_id) -> User:
        path = f"/api/core/users/{user_id}"

        json_data = self.do_get(path)

        user = User.schema().load(json_data)

        return user