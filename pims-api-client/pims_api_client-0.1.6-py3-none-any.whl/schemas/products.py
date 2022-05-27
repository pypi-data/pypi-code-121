from typing import Optional, Union
from pydantic import BaseModel, validator, Field
from pims_api_client.schemas.attributes import AttributeListItem

class ProductFilterItem(BaseModel):
    id: str
    name: str
    code: str
    type: str
    field: Optional[str]


class ProductId(BaseModel):
    uid: str
    node: str = None


class ProductItemList(BaseModel):
    id: str
    attributes: list


class ProductListFilter(BaseModel):
    count: str = None
    page: str
    pages: str = None
    per_page: str


class ProductList(ProductListFilter):
    items: list[ProductItemList]

    
