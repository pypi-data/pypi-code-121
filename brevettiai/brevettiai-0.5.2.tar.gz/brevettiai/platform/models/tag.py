from pydantic import Field, BaseModel
from typing import Optional, List
from uuid import uuid4


class Tag(BaseModel):
    """
    Model defining a Tag on the Brevetti platform
    """
    name: str
    id: str = Field(default_factory=lambda: str(uuid4()))
    parent_id: Optional[str] = Field(default=None, alias="parentId")
    created: str = ""
    children: List['Tag'] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True

    @staticmethod
    def find(tree, key, value):
        items = tree.children if isinstance(tree, Tag) else tree
        for item in items:
            if getattr(item, key) == value:
                yield item
            else:
                yield from Tag.find(item, key, value)

    @staticmethod
    def find_path(tree, key, value, path=()):
        items = tree.children if isinstance(tree, Tag) else tree
        for item in items:
            if getattr(item, key) == value:
                yield (*path, item)
            else:
                yield from Tag.find_path(item, key, value, (*path, item))

Tag.update_forward_refs()