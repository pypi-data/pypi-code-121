from ktrader import utils


class Rule():
    # 【1.购买、卖出、抛出】---------------------
    # TP = 0.005
    # SL = 0.04  # 正负号问题

    SIDE_BUY_TP =  0.005
    SIDE_BUY_SL = 0.01

    SIDE_SELL_TP = 0.015
    SIDE_SELL_SL = 0.035


    # 运行购买的时间
    BUY_PERIODS = [
        # ['00:00:00', '23:59:00']
    ]
    # 运行卖出的时间
    SELL_PERIODS = [
        # ['00:00:00', '23:59:59']
    ]
    # 运行抛出的时间
    THROW_PERIODS = [
        # ['23:59:00', '23:59:00'],
    ]

    # 手续费率
    COMMISSION_RATE = 0.0003
    # 本金
    money = 100
    # 杠杆
    LEVEL = 10

    def __init__(self):
        BUY_PERIODS_MINUTE = []
        if not self.BUY_PERIODS or not self.BUY_PERIODS[0]:
            self.BUY_PERIODS = [['00:00:00', '23:59:59']]
        for buy_period in self.BUY_PERIODS:
            BUY_PERIODS_MINUTE.append(
                [
                    utils.date.time_to_minute(buy_period[0]),
                    utils.date.time_to_minute(buy_period[1]),
                ],
            )
        self.BUY_PERIODS = BUY_PERIODS_MINUTE

        SELL_PERIODS_MINUTE = []
        if not self.SELL_PERIODS or not self.SELL_PERIODS[0]:
            self.SELL_PERIODS = [['00:00:00', '23:59:59']]

        for sell_period in self.SELL_PERIODS:
            SELL_PERIODS_MINUTE.append(
                [
                    utils.date.time_to_minute(sell_period[0]),
                    utils.date.time_to_minute(sell_period[1]),
                ],
            )
        self.SELL_PERIODS = SELL_PERIODS_MINUTE

        THROW_PERIODS_MINUTE = []
        if self.THROW_PERIODS and self.THROW_PERIODS[0]:
            for throw_period in self.THROW_PERIODS:
                THROW_PERIODS_MINUTE.append(
                    [
                        utils.date.time_to_minute(throw_period[0]),
                        utils.date.time_to_minute(throw_period[1]),
                    ],
                )
        self.THROW_PERIODS = THROW_PERIODS_MINUTE
