from pydantic import BaseModel


class UserModel(BaseModel):
    uuid: str
    telephone: str
    password: str
    is_active: bool

    class Config:
        orm_mode = True
