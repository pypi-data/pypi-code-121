from typing import Any, List, Literal, Optional

from pydantic import BaseModel, validator


class TcatOrderData(BaseModel):
    """
    ProductTypeId
    - 0001:一般食品
    - 0002:名特產/甜產
    - 0003:酒/油/醋/醬
    - 0004:穀物蔬果
    - 0005:水產/肉品
    - 0006:3C
    - 0007:家電
    - 0008:服飾配件
    - 0009:生活用品
    - 0010:美容彩妝
    - 0011:保健食品
    - 0012:醫療相關用品
    - 0013:寵物用品飼料
    - 0014:印刷品
    - 0015:其他
    """

    OBTNumber: str = ""  # 託運單號(列印類別欄位為01請填空)
    OrderId: str  # 客戶訂單號碼
    Thermosphere: Literal["0001", "0002", "0003"]  # 常溫/冷藏/冷凍
    Spec: Literal["0001", "0002", "0003", "0004"]  # 60-150cm
    ReceiptLocation: Literal["01", "02"] = "01"  # 到宅/站所
    ReceiptStationNo: Optional[str]  # 站所編號(若收付地點02必填)
    RecipientName: str
    RecipientTel: str
    RecipientMobile: str
    RecipientAddress: str
    SenderName: str
    SenderTel: str
    SenderMobile: str
    SenderZipCode: str
    SenderAddress: str
    ShipmentDate: str  # 出貨日期(yyyyMMdd/國定假日、周日不配送)
    DeliveryDate: str  # 希望配達日期(yyyyMMdd/國定假日、周日不配送)
    DeliveryTime: Literal["01", "02", "04"] = "04"  # 13前/14-18/不指定
    IsFreight: Literal["Y", "N"] = "N"  # 是否到付
    IsCollection: Literal["Y", "N"]  # 是否代收貨款
    CollectionAmount: int
    IsSwipe: Literal["Y", "N"] = "N"  # 是否允許刷卡
    IsDeclare: Literal["Y", "N"] = "N"  # 是否報值
    DeclareAmount: int = 0
    ProductTypeId: Literal[
        "0001",
        "0002",
        "0003",
        "0004",
        "0005",
        "0006",
        "0007",
        "0008",
        "0009",
        "0010",
        "0011",
        "0012",
        "0013",
        "0014",
        "0015",
    ] = "0015"
    ProductName: str
    Memo: Optional[str]

    @validator("SenderZipCode")
    def check_sender_zip(cls, v: str) -> str:
        if len(v) != 6:
            raise ValueError("zip code need in 6 digits")
        return v

    @validator("ProductName")
    def check_product_name(cls, v: str) -> str:
        if len(v) > 20:
            return v[:20]
        return v

    @validator("CollectionAmount")
    def verify_collection_amount(cls, v: int, values: Any) -> int:
        if values["IsCollection"] == "N":
            return 0
        return v


class TcatLogsiticsData(BaseModel):
    PrintType: str = "01"  # 列印類別
    PrintOBTType: Literal["01", "02", "03"] = "02"  # A4三模宅配
    Orders: List[TcatOrderData]


class TcatPickingBody(BaseModel):
    OrderId: str
    ProductTypeId: Literal[
        "0001",
        "0002",
        "0003",
        "0004",
        "0005",
        "0006",
        "0007",
        "0008",
        "0009",
        "0010",
        "0011",
        "0012",
        "0013",
        "0014",
        "0015",
    ] = "0015"
    ProductName: str
    Quantity: int
    Price: int
    Amount: int
    Column01: str = ""
    Column02: str = ""
    Column03: str = ""
    Column04: str = ""

    @validator("ProductName")
    def check_product_name(cls, v: str) -> str:
        if len(v) > 20:
            return v[:20]
        return v


class TcatPickingTitle(BaseModel):
    Column01: str = ""
    Column02: str = ""
    Column03: str = ""
    Column04: str = ""


class TcatPickingFooter(BaseModel):
    Row01: str = ""
    Row02: str = ""
    Row03: str = ""
    Row04: str = ""


class TcatPickingData(BaseModel):
    Title: TcatPickingTitle
    Body: List[TcatPickingBody]
    Footer: TcatPickingFooter


class TcatPickingOrderData(BaseModel):
    OBTNumber: str = ""
    Thermosphere: Literal["0001", "0002", "0003"]
    Spec: Literal["0001", "0002", "0003", "0004"]
    ReceiptLocation: Literal["01", "02"] = "01"
    ReceiptStationNo: Optional[str]
    RecipientName: str
    RecipientTel: str
    RecipientMobile: str
    RecipientAddress: str
    SenderName: str
    SenderTel: str
    SenderMobile: str
    SenderZipCode: str
    SenderAddress: str
    ShipmentDate: str
    DeliveryDate: str
    DeliveryTime: Literal["01", "02", "04"] = "04"
    IsFreight: Literal["Y", "N"] = "N"
    IsCollection: Literal["Y", "N"] = "N"
    CollectionAmount: int
    IsSwipe: Literal["Y", "N"] = "N"
    IsDeclare: Literal["Y", "N"] = "N"
    DeclareAmount: int = 0
    Memo: Optional[str]
    Detail: TcatPickingData

    @validator("SenderZipCode")
    def check_sender_zip(cls, v: str) -> str:
        if len(v) != 6:
            raise ValueError("zip code need in 6 digits")
        return v

    @validator("CollectionAmount")
    def verify_collection_amount(cls, v: int, values: Any) -> int:
        if values["IsCollection"] == "N":
            return 0
        return v


class TcatPickingRequestData(BaseModel):
    PrintType: str = "01"
    PrintOBTType: Literal["01"] = "01"
    Orders: List[TcatPickingOrderData]
