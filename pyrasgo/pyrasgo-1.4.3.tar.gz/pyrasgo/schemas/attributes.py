from pydantic import BaseModel


class Attribute(BaseModel):
    key: str
    value: str
