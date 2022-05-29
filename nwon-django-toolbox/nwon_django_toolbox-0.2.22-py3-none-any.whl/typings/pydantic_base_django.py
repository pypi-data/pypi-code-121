import humps
from pydantic import BaseModel


class PydanticBaseDjango(BaseModel):
    class Config:
        # no additional properties
        extra = "forbid"

        # Allow initialization via attribute names and aliases
        allow_population_by_field_name = True

        # auto generate camelized aliases
        alias_generator = humps.camelize


__all__ = ["PydanticBaseDjango"]
