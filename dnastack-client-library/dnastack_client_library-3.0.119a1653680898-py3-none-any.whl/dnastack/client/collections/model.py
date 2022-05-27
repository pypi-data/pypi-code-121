import re

from typing import Optional

from pydantic import BaseModel


class Collection(BaseModel):
    """
    A model representing a collection

    .. note:: This is not a full representation of the object.
    """

    id: Optional[str]
    name: str
    slugName: str
    description: Optional[str]
    itemsQuery: str

    @classmethod
    def make(cls,
             name: str,
             items_query: str,
             slug_name: Optional[str] = None,
             description: Optional[str] = None):
        if not slug_name:
            slug_name = re.sub(r'[^a-z0-9-]', '-', name.lower()) + str(int(time()))
            slug_name = re.sub(r'-+', '-', slug_name)
        return cls(name=name, itemsQuery=items_query, slugName=slug_name, description=description)