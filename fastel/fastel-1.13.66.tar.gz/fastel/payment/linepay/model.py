from typing import List, Literal

from pydantic import BaseModel


class LinePayRequestProduct(BaseModel):
    id: str
    name: str
    imageUrl: str
    quantity: int
    price: int


class LinePayRequestPackage(BaseModel):
    id: str
    amount: int
    products: List[LinePayRequestProduct]


class LinePayRedirectUrl(BaseModel):
    confirmUrl: str
    cancelUrl: str


class LinePayRequestModel(BaseModel):
    amount: int
    currency: Literal["USD", "JPY", "TWD", "THB"] = "TWD"
    orderId: str
    packages: List[LinePayRequestPackage]
    redirectUrls: LinePayRedirectUrl
