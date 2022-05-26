from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .base import BaseCart
from .collections import get_collection
from .datastructures import CartConfig
from .product_items import ProductItems
from .utils import get_gift_points_amount, get_points_amount


class Cart(BaseCart):
    product_multi_item_cls = ProductItems
    config_cls = CartConfig

    def _init_cart_extra(self) -> Dict[str, Any]:
        return {}

    def _calc_fee(self) -> Tuple[int, List[Dict[str, Any]]]:
        fee_items: List[Dict[str, Any]] = [
            {
                "name": "運費",
                "amount": 0,
            }
        ]
        return (sum(i["amount"] for i in fee_items), fee_items)

    def _calc_coupon_discounts(
        self, subtotal: int, coupon_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        items = []
        now = datetime.now().timestamp() * 1000

        if coupon_code:
            coupon = get_collection("coupon").find_one(
                {
                    "code": coupon_code,
                    "start_time": {"$lte": now},
                    "end_time": {"$gte": now},
                    "threshold": {"$lte": subtotal},
                    "usage": {"$ne": 0},
                    "is_void": {"$ne": True},
                }
            )

            if coupon:
                assigned_user_id = coupon.get("user_id", None)
                if (not assigned_user_id) or (
                    assigned_user_id == self._cache_cart["owner"]
                ):
                    items.append(
                        {
                            "type": "coupon",
                            "name": coupon["name"],
                            "sales_amount": round(
                                coupon["discount"] / self._tax_ratio, 7
                            ),
                            "amount": coupon["discount"],
                            "coupon": coupon,
                        }
                    )

        return items

    def _calc_threshold_discounts(self, subtotal: int) -> List[Dict[str, Any]]:
        items = []
        now = datetime.now().timestamp() * 1000

        if get_collection("discount") is not None:
            discounts = get_collection("discount").find(
                {
                    "start_time": {"$lte": now},
                    "end_time": {"$gte": now},
                    "threshold": {"$lte": subtotal},
                }
            )

            if discounts:
                discounts.sort((("threshold", -1),))
                for discount in discounts:
                    items.append(
                        {
                            "type": "discount",
                            "name": discount["name"],
                            "sales_amount": round(
                                discount["discount"] / self._tax_ratio, 7
                            ),
                            "amount": discount["discount"],
                            "discount": discount,
                        }
                    )
                    break

        return items

    def _calc_extra_discount(self, subtotal: int) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        return items

    def _calc_points_discount(
        self, subtotal: int, discount_amount: int
    ) -> List[Dict[str, Any]]:
        items = []
        current_total = subtotal - discount_amount
        if current_total < 0:
            current_total = 0
        private_profile = get_collection("private_profile").find_one(
            {"owner": str(self._user["_id"])}
        )
        points_amount = 0
        gift_points_amount = 0

        user_points = private_profile.get("points", 0)
        user_gift_points = private_profile.get("gift_points", 0)
        if self.use_full_points:
            if user_gift_points > 0:
                # 使用 _gift_points_ratio 1金額：n點數 比例計算
                gift_points_amount = get_gift_points_amount(
                    user_gift_points=user_gift_points,
                    gift_points_ratio=self._gift_points_ratio,
                    use_points_ratio=self._use_points_ratio,
                    current_total=current_total,
                )
                current_total -= gift_points_amount
            if user_points > 0:
                # 使用 _points_ratio 1點數：n金額 比例計算
                points_amount = get_points_amount(
                    user_points=user_points,
                    points_ratio=self._points_ratio,
                    use_points_ratio=self._use_points_ratio,
                    current_total=current_total,
                )
        else:
            if self.gift_points > 0:
                # 使用 _gift_points_ratio 1金額：n點數 比例計算
                gift_points_amount = get_gift_points_amount(
                    user_gift_points=user_gift_points,
                    gift_points_ratio=self._gift_points_ratio,
                    use_points_ratio=self._use_points_ratio,
                    current_total=current_total,
                    gift_points=self.gift_points,
                )
                current_total -= gift_points_amount
            if self.points > 0:
                # 使用 _points_ratio 1點數：n金額 比例計算
                points_amount = get_points_amount(
                    user_points=user_points,
                    points_ratio=self._points_ratio,
                    use_points_ratio=self._use_points_ratio,
                    current_total=current_total,
                    points=self.points,
                )

        gift_points = gift_points_amount * self._gift_points_ratio

        points = (
            points_amount % self._points_ratio
            and int(points_amount / self._points_ratio) + 1
            or int(points_amount / self._points_ratio)
        )
        if gift_points > 0:
            items.append(
                {
                    "type": "gift_points",
                    "name": "紅利點數折扣",
                    "sales_amount": round(gift_points_amount / self._tax_ratio, 7),
                    "amount": gift_points_amount,
                    "points": gift_points,
                }
            )
        if points > 0:
            items.append(
                {
                    "type": "points",
                    "name": "點數折扣",
                    "sales_amount": round(points_amount / self._tax_ratio, 7),
                    "amount": points_amount,
                    "points": points,
                }
            )

        return items

    def _calc_discounts(
        self,
        subtotal: int,
        coupon_code: Optional[str] = None,
    ) -> Tuple[int, List[Dict[str, Any]]]:
        items = []

        items += self._calc_coupon_discounts(subtotal, coupon_code)
        items += self._calc_threshold_discounts(subtotal)
        items += self._calc_extra_discount(subtotal)
        items += self._calc_points_discount(
            subtotal, sum([item["amount"] for item in items])
        )
        return sum([item["amount"] for item in items]), items

    def _calc_addon(self, **kwargs: Any) -> Any:
        return 0, [], 0, []
