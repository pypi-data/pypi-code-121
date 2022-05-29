from typing import Callable, Optional

from django.contrib.auth.models import AbstractBaseUser
from pydantic import BaseModel

LoginFunction = Callable[[AbstractBaseUser, str], str]


class PermissionTestExpectation(BaseModel):
    user: AbstractBaseUser
    password: str
    get_list_status_code: Optional[int] = None
    get_list_return_number: Optional[int] = None
    get_detail_status_code: Optional[int] = None
    create_status_code: Optional[int] = None
    patch_status_code: Optional[int] = None
    put_status_code: Optional[int] = None
    delete_status_code: Optional[int] = None
