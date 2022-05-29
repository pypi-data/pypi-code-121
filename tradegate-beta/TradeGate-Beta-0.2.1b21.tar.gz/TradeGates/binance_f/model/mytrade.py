class MyTrade:

    def __init__(self):
        self.isBuyer = False
        self.commission = 0.0
        self.commissionAsset = ""
        self.counterPartyId = None
        self.id = None
        self.isMaker = False
        self.orderId = None
        self.price = 0.0
        self.qty = 0.0
        self.quoteQty = 0.0
        self.realizedPnl = 0.0
        self.side = ""
        self.symbol = ""
        self.time = 0

    @staticmethod
    def json_parse(json_data):
        result = MyTrade()
        result.isBuyer = json_data.get_boolean("buyer")
        result.commission = json_data.get_float("commission")
        result.commissionAsset = json_data.get_string("commissionAsset")
        result.counterPartyId = json_data.get_int_or_default("counterPartyId", None)
        result.id = json_data.get_int("id")
        result.isMaker = json_data.get_boolean("maker")
        result.orderId = json_data.get_int("orderId")
        result.price = json_data.get_float("price")
        result.qty = json_data.get_float("qty")
        result.quoteQty = json_data.get_float("quoteQty")
        result.realizedPnl = json_data.get_float("realizedPnl")
        result.side = json_data.get_string("side")
        result.symbol = json_data.get_string("symbol")
        result.time = json_data.get_int("time")
        
        return result

    def toDict(self):
        outDict = {'symbol': self.symbol,
                    'id': self.id,
                    'orderId': self.orderId,
                    'orderListId': self.counterPartyId,
                    'price': self.price,
                    'qty': self.qty,
                    'quoteQty': self.quoteQty,
                    'commission': self.commission,
                    'commissionAsset': self.commissionAsset,
                    'time': self.time,
                    'isBuyer': self.isBuyer,
                    'isMaker': self.isMaker,
                    'isBestMatch': None}

        return outDict

# {'symbol': 'BTCUSDT',
#   'id': 12786,
#   'orderId': 15005,
#   'orderListId': -1,
#   'price': '35000.00000000',
#   'qty': '0.00200000',
#   'quoteQty': '70.00000000',
#   'commission': '0.00000000',
#   'commissionAsset': 'BTC',
#   'time': 1646213286609,
#   'isBuyer': True,
#   'isMaker': True,
#   'isBestMatch': True}
