import base64
import hmac
import json
import uuid
from hashlib import sha256
from typing import Any, Dict, List, Optional

import requests

from fastel.payment.linepay.exceptions import LinePayException


class LinePay:
    @property
    def linepay_url(self) -> str:
        if self.stage in ["prod", "PROD"]:
            return "https://api-pay.line.me"
        return "https://sandbox-api-pay.line.me"

    def __init__(
        self,
        stage: str,
        channel_id: str,
        channel_secret: str,
        callback_url: str,
    ):
        self.stage = stage
        self.channel_id = channel_id
        self.channel_secret = channel_secret
        self.callback_url = callback_url

    def build_headers(
        self,
        uri: str,
        request_body: str,
    ) -> Dict[str, Any]:
        nonce = str(uuid.uuid4())
        _signature = hmac.new(
            key=self.channel_secret.encode(),
            msg=(self.channel_secret + uri + request_body + nonce).encode(),
            digestmod=sha256,
        )
        signature = base64.b64encode(_signature.digest()).decode()
        return {
            "Content-Type": "application/json",
            "X-LINE-ChannelId": self.channel_id,
            "X-LINE-Authorization-Nonce": nonce,
            "X-LINE-Authorization": signature,
        }

    def _raise_exception(self, resp: requests.Response) -> None:
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise LinePayException(error="linepay_request_error", detail=str(err))

    def verify(self, response: Dict[str, Any]) -> bool:
        if response["returnCode"] == "0000":
            return True
        return False

    def _to_products(self, checkout_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        # only display one item for total order amount
        first_item = checkout_dict["items"][0]
        return [
            {
                "id": uuid.uuid4().__str__(),
                "amount": checkout_dict["total"],
                "products": [
                    {
                        "id": first_item["product"]["id"]["$oid"],
                        "name": first_item["name"] + "與其它商品",
                        "imageUrl": first_item["product"]["images"][0]["expected_url"],
                        "quantity": 1,
                        "price": checkout_dict["total"],
                    }
                ],
            }
        ]

    def request(self, checkout_dict: Dict[str, Any]) -> Any:
        products = self._to_products(checkout_dict)
        total = checkout_dict["total"]
        body = {
            "amount": total,
            "currency": "TWD",
            "orderId": checkout_dict["order_number"],
            "packages": products,
            "redirectUrls": {
                "confirmUrl": self.callback_url,
                "cancelUrl": self.callback_url,
            },
        }
        json_str = json.dumps(body)
        path = "/v3/payments/request"
        url = f"{self.linepay_url}{path}"
        headers = self.build_headers(path, json_str)

        resp = requests.post(
            url=url,
            json=body,
            headers=headers,
        )
        self._raise_exception(resp)

        resp_json = resp.json()

        if not self.verify(resp_json):
            print(resp_json)
            raise LinePayException(
                error="linepay_verify_error",
                detail="",
            )

        return resp_json["info"]["paymentUrl"]

    def confirm(self, transaction_id: str, amount: int) -> Any:
        body = {"amount": amount, "currency": "TWD"}
        json_str = json.dumps(body)
        path = f"/v3/payments/{transaction_id}/confirm"
        url = f"{self.linepay_url}{path}"
        headers = self.build_headers(path, json_str)
        resp = requests.post(url=url, json=body, headers=headers)
        self._raise_exception(resp)
        return resp.json()

    def refund(self, transaction_id: str, refund_amount: int) -> Any:
        body = {"refundAmount": refund_amount}
        json_str = json.dumps(body)
        path = f"/v3/payments/{transaction_id}/refund"
        url = f"{self.linepay_url}{path}"
        headers = self.build_headers(path, json_str)
        resp = requests.post(
            url=url,
            json=body,
            headers=headers,
        )
        self._raise_exception(resp)
        return resp.json()

    def get_details(
        self, transaction_id: Optional[str] = None, order_id: Optional[str] = None
    ) -> Any:
        path = f"/v3/payments"
        query = ""
        if transaction_id is not None:
            query += "transactionId={}&".format(str(transaction_id))
        if order_id is not None:
            query += "orderId={}".format(order_id)
        if query.endswith("?") or query.endswith("&"):
            query = query[:-1]

        url = (
            f"{self.linepay_url}{path}?{query}"
            if query
            else f"{self.linepay_url}{path}"
        )
        headers = self.build_headers(path, query)
        resp = requests.get(
            url=url,
            headers=headers,
        )
        self._raise_exception(resp)
        return resp.json()
