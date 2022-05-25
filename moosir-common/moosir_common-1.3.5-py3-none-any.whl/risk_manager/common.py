class PositionTypeConstants:
    POSITION_LONG = "LONG"
    POSITION_NONE = "NONE"
    POSITION_SHORT = "SHORT"


class BrokerMinLotSizeConstants:
    """
    - these are used for decimal points rounding for position size in lot
    - i.e. micro lot will be converted to 0.01 decimal point of lot
    - e.x. 2 micro lot = 0.02 lot

    """
    COMPLETE_LOT = 0
    MINI_LOT = 1
    MICRO_LOT = 2


class OrderPosition:
    def __init__(self, position_size_lot, trail_amount, price, leverage_used):
        # self.position_size = position_size
        self.position_size_lot = position_size_lot
        self.trail_amount = trail_amount
        self.price = price
        self.leverage_used = leverage_used


class Constants:

    @staticmethod
    def LOT_SIZE():
        return 100000

    @staticmethod
    def MINI_LOT_SIZE():
        return 10000

    @staticmethod
    def MICRO_LOT_SIZE():
        return 1000

    @staticmethod
    def PIP_CONST():
        return 0.0001

    @staticmethod
    def PIP_IN_DOLLAR():
        return Constants.LOT_SIZE() * Constants.PIP_CONST()

    @staticmethod
    def PIP_VALUE():
        return 10


class IRiskManager:
    def calculate_order(self, request) -> OrderPosition:
        pass

    def calculate_trade_type(self, request) -> PositionTypeConstants:
        pass

    def make_orders_long(self, request):
        pass

    def make_orders_short(self, request):
        pass

class IRiskManagerFactory:
    def create_risk_mgr(self) -> IRiskManager:
        """
        Create a Risk Manager
        """
        pass