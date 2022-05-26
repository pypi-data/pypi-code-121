from pydantic import EmailStr, BaseModel

from fastapi_interface.schemas.base import BaseOrmSchema


class BaseUser(BaseModel):
    username: str
    email: EmailStr


class UserPd(BaseUser, BaseOrmSchema):
    hashed_password: str
