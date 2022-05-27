from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import Generic, TypeVar, List

T = TypeVar('T')


class PerPageRequest(BaseModel):
    per_page: int = 25
    page: int = 1


class PagedListResponse(GenericModel, Generic[T]):
    count: int
    per_page: int
    page: int
    pages: int
    items: List[T]
