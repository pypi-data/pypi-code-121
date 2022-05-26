def get_gift_points_amount(
    user_gift_points: int,
    gift_points_ratio: int,
    use_points_ratio: float,
    current_total: int,
    gift_points: int = 0,
) -> int:
    if gift_points > 0:
        gift_points_amount = min(
            # 計算用戶點數比例金額後的數值
            int(user_gift_points / gift_points_ratio),
            # 計算帶入點數比例金額後的數值
            int(gift_points / gift_points_ratio),
            # 與目前能夠折抵的訂單折扣後價格的金額
            round(use_points_ratio * current_total),
        )
    else:
        gift_points_amount = min(
            # 計算用戶點數比例金額後的數值
            int(user_gift_points / gift_points_ratio),
            # 與目前能夠折抵的訂單折扣後價格的金額
            round(use_points_ratio * current_total),
        )
    return gift_points_amount


def get_points_amount(
    user_points: int,
    points_ratio: int,
    use_points_ratio: float,
    current_total: int,
    points: int = 0,
) -> int:
    if points > 0:
        points_amount = min(
            # 計算用戶點數比例金額後的數值
            user_points * points_ratio,
            # 計算帶入點數比例金額後的數值
            points * points_ratio,
            # 與目前能夠折抵的訂單折扣後價格的金額
            round(use_points_ratio * current_total),
        )
    else:
        points_amount = min(
            # 計算用戶點數比例金額後的數值
            user_points * points_ratio,
            # 與目前能夠折抵的訂單折扣後價格的金額
            round(use_points_ratio * current_total),
        )
    return points_amount
