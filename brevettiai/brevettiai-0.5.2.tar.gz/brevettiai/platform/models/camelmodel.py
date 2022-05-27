from pydantic import BaseModel, PrivateAttr
from brevettiai.io import io_tools, IoTools


def _to_camel(x):
    init, *fol = x.split("_")
    return "".join((init.lower(), *map(lambda x: x.title(), fol)))


class CamelModel(BaseModel):
    """ Model with camel cased aliases for all fields by default """
    class Config:
        alias_generator = _to_camel
        allow_population_by_field_name = True
