# ecpay
import io
from typing import Any, Dict, List, Tuple

import boto3
from bs4 import BeautifulSoup
from requests import Response

from fastel.collections import get_site_config
from fastel.config import SdkConfig
from fastel.exceptions import APIException
from fastel.payment.cryptors import MD5Cryptor
from fastel.payment.ecpay.models.checkout import CheckoutModel
from fastel.payment.ecpay.models.invoice import IssueB2BModel, IssueB2CModel
from fastel.payment.ecpay.models.logistics import (
    LogisticModel,
    LogisticsDataModel,
    LogisticsDetailModel,
)
from fastel.utils import requests

PAYMENT_SUBTYPE = {
    "default": "ALL",
    "credit": "Credit",
    "atm": "ATM",
    "web_atm": "WebATM",
    "cvs": "CVS",
    "barcode": "BARCODE",
}

CARRIER_TYPE_TABLE = {
    "0": "",
    "1": "1",
    "2": "2",
    "3": "3",
}


def ecpay_url() -> str:
    return SdkConfig.payment_host + "/ecpay"


def client_id() -> str:
    return SdkConfig.client_id


def client_secret() -> str:
    return SdkConfig.client_secret


def _replace_limit_name(name: str, limit: int) -> str:
    if len(name) > limit:
        return name[: limit - 3] + "..."
    return name


def checkout_request(
    checkout: Dict[str, Any],
) -> str:
    url = (
        ecpay_url()
        + f"/request?client_id={client_id()}&client_secret={client_secret()}"
    )
    name = "#".join([item["name"] for item in checkout.get("items", [])])
    item_name = _replace_limit_name(name=name, limit=400)
    common_props = {
        "MerchantTradeNo": checkout["order_number"]
        + "{:02d}".format(checkout["attempt"]),
        "ChoosePayment": PAYMENT_SUBTYPE.get(checkout["payment_subtype"], "ALL"),
        "TotalAmount": checkout["total"],
    }

    if checkout.get("is_custom", False):
        validated = CheckoutModel(
            **common_props,
            ItemName=checkout["custom_name"],
        )
    else:
        validated = CheckoutModel(
            **common_props,
            ItemName=item_name,
        )

    validated_dict = validated.dict(exclude_none=True)
    resp: Response = requests.post(url, json=validated_dict)
    resp_json = resp.json()
    assert isinstance(resp_json, dict)
    return resp_json.get("url", "")


def cvs_map(cart: Dict[str, Any]) -> str:
    url = (
        ecpay_url()
        + f"/logistics/map/request?client_id={client_id()}&client_secret={client_secret()}"
    )
    resp: Response = requests.post(
        url,
        json={
            "LogisticsType": "CVS",
            "LogisticsSubType": cart.get("logistics_subtype", "FAMIC2C"),
            "IsCollection": "Y"
            if cart.get("payment_subtype", "credit") == "cod"
            else "N",
        },
    )
    resp_json = resp.json()
    assert isinstance(resp_json, dict)
    return resp_json.get("url", "")


def logistics_create(order: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    if order["total"] > 20000:
        return (False, {"validation_error": "物流訂單商品不能超過20000元新台幣"})
    common_props = dict(
        MerchantTradeNo=order["order_id"],
        GoodsName=f"訂單{order['order_id']}",
        GoodsAmount=order["total"],
        ReceiverName=_replace_limit_name(name=order["receiver_name"], limit=10),
        ReceiverEmail=order["receiver_email"],
        ReceiverCellPhone=order["receiver_phone"],
        ReceiverZipCode=order["receiver_zip"],
        ReceiverAddress=(
            order["receiver_city"]
            + order["receiver_district"]
            + order["receiver_address"]
        ),
    )

    default_sender_info = dict(
        SenderName="忻旅科技",
        SenderPhone="02-77295130",
        SenderZipCode="10361",
        SenderCellPhone="0900000000",
        SenderAddress="台北市大同區民權西路136號10樓之5",
    )

    sender_info = get_site_config(
        key="logistics_sender_info", default=default_sender_info
    )
    sender_info["SenderName"] = _replace_limit_name(
        name=sender_info["SenderName"], limit=10
    )
    data: LogisticModel
    if order["logistics_type"] == "HOME":
        data = LogisticModel(
            **common_props,
            **sender_info,
            Distance=("00" if order["receiver_city"] == "台北市" else "01"),
            Temperature="0001",
        )
    elif order["logistics_type"] == "CVS":
        data = LogisticModel(
            **common_props,
            **sender_info,
            LogisticsType="CVS",
            LogisticsSubType=order["logistics_subtype"],
            IsCollection="Y" if order["payment_subtype"] == "cod" else "N",
            CollectionAmount=order["total"] if order["payment_subtype"] == "cod" else 0,
            ReceiverStoreID=order["logistics_cvs_store_id"],
        )
    else:
        return (
            False,
            {"validation_error": f"no such logistics_type {order['logistics_type']}"},
        )

    url = (
        ecpay_url()
        + f"/logistics/create?client_id={client_id()}&client_secret={client_secret()}"
    )
    try:
        resp: Response = requests.post(url, json=data.dict(exclude_none=True))
        resp.raise_for_status()
        logistics_resp = resp.json()
        if logistics_resp.get("error", ""):
            raise APIException(
                status_code=500, error="server_error", detail="logistics return error"
            )
    except APIException:
        return (False, logistics_resp)
    except Exception:
        return (False, {"error": "response error"})
    return (True, logistics_resp)


def issue_invoice(checkout: Dict[str, Any]) -> Dict[str, Any]:
    if checkout.get("category", "B2C") == "B2C":
        url = (
            ecpay_url()
            + f"/B2C/invoice/issue?client_id={client_id()}&client_secret={client_secret()}"
        )
        invoice_data = generate_B2C_invoice_data(checkout)
    else:
        url = (
            ecpay_url()
            + f"/B2B/invoice/issue?client_id={client_id()}&client_secret={client_secret()}"
        )
        invoice_data = generate_B2B_invoice_data(checkout)
    try:
        resp: Response = requests.post(url, json=invoice_data)
        resp.raise_for_status()
        print("issue invoice")
        resp_json = resp.json()
    except Exception as error:
        return {"error": error}
    assert isinstance(resp_json, dict)
    return resp_json


def generate_B2C_invoice_item(
    items: List[Dict[str, Any]],
    extra_items: List[Dict[str, Any]],
    discount_items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    result = []
    for item in items:
        item_result = {
            "ItemName": _replace_limit_name(name=item.get("name", ""), limit=100),
            "ItemCount": item["config"].get("qty", 1),
            "ItemWord": item["config"]["extra_data"]
            and item["config"]["extra_data"].get("word", "份")
            or "份",
            "ItemPrice": item.get("price", 0),
            "ItemAmount": item.get("amount", 0),
        }
        result.append(item_result)
    # 計算運費
    for extra_item in extra_items:
        item_result = {
            "ItemName": _replace_limit_name(name=extra_item.get("name", ""), limit=100),
            "ItemCount": 1,
            "ItemWord": "份",
            "ItemPrice": extra_item.get("amount", 0),
            "ItemAmount": extra_item.get("amount", 0),
        }
        result.append(item_result)
    # 計算折扣金額
    for discount_item in discount_items:
        item_result = {
            "ItemName": _replace_limit_name(
                name=discount_item.get("name", ""), limit=100
            ),
            "ItemCount": 1,
            "ItemWord": "份",
            "ItemPrice": -discount_item.get("amount", 0),
            "ItemAmount": -discount_item.get("amount", 0),
        }
        result.append(item_result)
    return result


def generate_B2C_invoice_data(checkout: Dict[str, Any]) -> Dict[str, Any]:
    items = checkout.get("items", [])
    extra_items = checkout.get("extra_items", [])
    discount_items = checkout.get("discount_items", [])
    carrier_type = CARRIER_TYPE_TABLE[checkout.get("invoice_carrier_type", "1")]
    love_code = (
        checkout.get("invoice_donation", "0") == "1"
        and checkout.get("invoice_love_code", None)
        or None
    )
    carrier_num = (
        carrier_type in ["2", "3"] and checkout.get("invoice_carrier_num", "") or ""
    )
    invoice_data = {
        "RelateNumber": checkout.get("order_number", ""),
        "CustomerEmail": checkout.get("buyer_email", ""),
        "Print": "0",
        "Donation": checkout.get("invoice_donation", "0"),
        "LoveCode": love_code,
        "CarrierType": carrier_type,
        "CarrierNum": carrier_num,
        "TaxType": checkout.get("invoice_tax_type", "1"),
        "SalesAmount": checkout.get("total", 0),
        "Items": generate_B2C_invoice_item(items, extra_items, discount_items),
        "InvType": checkout.get("invoice_tax_type", "") == "4" and "08" or "07",
    }
    return IssueB2CModel.validate(invoice_data).dict(exclude_none=True)


def generate_B2B_invoice_item(
    items: List[Dict[str, Any]],
    extra_items: List[Dict[str, Any]],
    discount_items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    result = []
    seq = 1
    for item in items:
        item_result = {
            "ItemSeq": seq,
            "ItemName": _replace_limit_name(name=item.get("name", ""), limit=256),
            "ItemCount": item["config"].get("qty", 1),
            "ItemWord": item["config"]["extra_data"]
            and item["config"]["extra_data"].get("word", "份")
            or "份",
            "ItemPrice": item.get("unit_sales", 0),
            "ItemAmount": item.get("sales_amount", 0),
        }
        result.append(item_result)
        seq += 1
    # 計算運費
    for extra_item in extra_items:
        item_result = {
            "ItemSeq": seq,
            "ItemName": _replace_limit_name(name=extra_item.get("name", ""), limit=256),
            "ItemCount": 1,
            "ItemWord": "份",
            "ItemPrice": extra_item.get("sales_amount", 0),
            "ItemAmount": extra_item.get("sales_amount", 0),
        }
        result.append(item_result)
        seq += 1
    # 計算折扣金額
    for discount_item in discount_items:
        item_result = {
            "ItemSeq": seq,
            "ItemName": _replace_limit_name(
                name=discount_item.get("name", ""), limit=256
            ),
            "ItemCount": 1,
            "ItemWord": "份",
            "ItemPrice": -discount_item.get("sales_amount", 0),
            "ItemAmount": -discount_item.get("sales_amount", 0),
        }
        result.append(item_result)
        seq += 1
    return result


def generate_B2B_invoice_data(checkout: Dict[str, Any]) -> Dict[str, Any]:
    items = checkout.get("items", [])
    extra_items = checkout.get("extra_items", [])
    discount_items = checkout.get("discount_items", [])
    invoice_data = {
        "RelateNumber": checkout.get("order_number", ""),
        "CustomerIdentifier": checkout.get("invoice_uni_no", ""),
        "CustomerEmail": checkout.get("buyer_email", ""),
        "TaxType": checkout.get("invoice_tax_type", "1"),
        "SalesAmount": checkout.get("sales", 0),
        "TaxAmount": checkout.get("tax", 0),
        "TotalAmount": checkout.get("total", 0),
        "Items": generate_B2B_invoice_item(items, extra_items, discount_items),
        "InvType": checkout.get("invoice_tax_type", "") == "4" and "08" or "07",
    }
    return IssueB2BModel.validate(invoice_data).dict(exclude_none=True)


def fetch_html_img(html: str) -> str:
    soup = BeautifulSoup(html)
    img_tag = soup.find("img")
    if not img_tag:
        return ""
    else:
        return str(img_tag.get("src", ""))


def _generate_shipping_data(
    cryptor: MD5Cryptor, logistics_data: LogisticsDataModel
) -> Tuple[str, Dict[str, Any]]:
    if logistics_data.logistics_sub_type == "FAMIC2C":
        url = f"{SdkConfig.ecpay_logistics_host}/Express/PrintFAMIC2COrderInfo"
        data = {
            "MerchantID": SdkConfig.logistics_merchant_id,
            "AllPayLogisticsID": logistics_data.logistics_id,
            "CVSPaymentNo": logistics_data.cvs_payment_no,
        }
    elif logistics_data.logistics_sub_type == "UNIMARTC2C":
        url = f"{SdkConfig.ecpay_logistics_host}/Express/PrintUniMartC2COrderInfo"
        data = {
            "MerchantID": SdkConfig.logistics_merchant_id,
            "AllPayLogisticsID": logistics_data.logistics_id,
            "CVSPaymentNo": logistics_data.cvs_payment_no,
            "CVSValidationNo": logistics_data.cvs_validation_no,
        }
    elif logistics_data.logistics_sub_type == "HILIFEC2C":
        url = f"{SdkConfig.ecpay_logistics_host}/Express/PrintHILIFEC2COrderInfo"
        data = {
            "MerchantID": SdkConfig.logistics_merchant_id,
            "AllPayLogisticsID": logistics_data.logistics_id,
            "CVSPaymentNo": logistics_data.cvs_payment_no,
        }
    elif logistics_data.logistics_sub_type == "OKMARTC2C":
        url = f"{SdkConfig.ecpay_logistics_host}/Express/PrintOKMARTC2COrderInfo"
        data = {
            "MerchantID": SdkConfig.logistics_merchant_id,
            "AllPayLogisticsID": logistics_data.logistics_id,
            "CVSPaymentNo": logistics_data.cvs_payment_no,
        }
    elif logistics_data.logistics_sub_type in [
        "FAMI",
        "UNIMART",
        "UNIMARTFREEZE",
        "HILIFE",
        "TCAT",
        "ECAN",
    ]:
        url = f"{SdkConfig.ecpay_logistics_host}/helper/printTradeDocument"
        data = {
            "MerchantID": SdkConfig.logistics_merchant_id,
            "AllPayLogisticsID": logistics_data.logistics_id,
        }
    else:
        return "", {}
    check_mac = cryptor.encrypt(data)
    data["CheckMacValue"] = check_mac
    return url, data


# return img bytes, content_type and logistics id
def get_shipping_note(logistics_data: LogisticsDataModel) -> Tuple[bytes, str]:
    if (
        SdkConfig.logistics_merchant_id
        and SdkConfig.logistics_hash_iv
        and SdkConfig.logistics_hash_key
    ):
        cryptor = MD5Cryptor(
            hash_key=SdkConfig.logistics_hash_key, hash_iv=SdkConfig.logistics_hash_iv
        )
        url, form_data = _generate_shipping_data(
            cryptor=cryptor, logistics_data=logistics_data
        )
        resp: Response = requests.post(url, data=form_data)
        resp.raise_for_status()
        html = resp.content.decode()
        img_url = fetch_html_img(html)
        # is dirty in uri encode
        print("shipping note url:", img_url)
        img_url = img_url.replace("amp;", "")
        img_resp: Response = requests.get(img_url)
        img_resp.raise_for_status()
        img = img_resp.content
        content_type = img_resp.headers.get("Content-Type", "image/png")
        return img, content_type
    else:
        return b"", ""


def upload_shipping_note(logistics_data: LogisticsDataModel) -> None:
    shipping_note, content_type = get_shipping_note(logistics_data)
    print(
        "[FASTEL] ------------------------- upload_shipping_note ------------------------"
    )
    if shipping_note and content_type:
        s3 = boto3.client("s3", "ap-northeast-1")
        buf = io.BytesIO()
        buf.write(shipping_note)
        buf.seek(0)
        s3.upload_fileobj(
            buf,
            SdkConfig.s3_bucket,
            f"shipping_note/{logistics_data.logistics_id}",
            # shipping note must be private file
            ExtraArgs={"ContentType": content_type},
        )
        print("[FASTEL] ------------------------- SUCCESS ------------------------")
    else:
        print("[FASTEL] ------------------------- FAIL ------------------------")
        print(
            f"logistics_merchant_id: {SdkConfig.logistics_merchant_id}",
            f"logistics_hash_key: {SdkConfig.logistics_hash_key}",
            f"logistics_hash_iv: {SdkConfig.logistics_hash_iv}",
        )


def logistics_data_transfer(
    logistics_detail: LogisticsDetailModel,
) -> LogisticsDataModel:
    logistics_data = {
        "trade_no": logistics_detail.MerchantTradeNo,
        "logistics_id": logistics_detail.AllPayLogisticsID,
        "logistics_type": logistics_detail.LogisticsType,
        "logistics_sub_type": logistics_detail.LogisticsSubType,
        "cvs_payment_no": logistics_detail.CVSPaymentNo,
        "cvs_validation_no": logistics_detail.CVSValidationNo,
        "goods_amount": logistics_detail.GoodsAmount,
        "update_status_date": logistics_detail.UpdateStatusDate,
        "rtn_code": logistics_detail.RtnCode,
        "rtn_msg": logistics_detail.RtnMsg,
        "receiver_name": logistics_detail.ReceiverName,
        "receiver_phone": logistics_detail.ReceiverPhone,
        "receiver_cell_phone": logistics_detail.ReceiverCellPhone,
        "receiver_email": logistics_detail.ReceiverEmail,
        "receiver_address": logistics_detail.ReceiverAddress,
    }
    result = LogisticsDataModel.validate(logistics_data)
    return result
