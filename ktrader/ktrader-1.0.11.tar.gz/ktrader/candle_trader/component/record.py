from ktrader.candle_trader.component.rule import Rule
from ktrader import utils


class Record():
    def __init__(self, candle, rule: Rule, index=0):
        self.candle = candle
        self.rule = rule
        self.money = rule.money
        self.index = index
        self.currentOrderDatas = []
        self.historyOrderDatas = []
        self.minutes = [utils.date.ts_to_minute(ts) for ts in candle[:, 0]]
        self.last_sellLine = {
            'buy': None,
            'sell': None,
        }

    def update(self):
        if self.minutes[self.index] == 0:
            self.day_index = self.index
            self.day_open = self.candle[self.index, 1]
            self.day_high = self.candle[self.index, 2]
            self.day_low = self.candle[self.index, 3]

        else:
            # try:
            #     self.day_high = self.candle[self.day_index:self.index, 2].max()
            #     self.day_low = self.candle[self.day_index:self.index, 3].min()
            # except:
            #     self.day_high = None
            #     self.day_low = None
            if hasattr(self, 'day_index'):
                self.day_high = self.candle[self.day_index:self.index, 2].max()
                self.day_low = self.candle[self.day_index:self.index, 3].min()
            else:
                self.day_high = None
                self.day_low = None

        if self.index > 0:
            self.last_open = self.candle[self.index - 1, 1]
            self.last_high = self.candle[self.index - 1, 2]
            self.last_low = self.candle[self.index - 1, 3]
            self.last_close = self.candle[self.index - 1, 4]
        else:
            self.last_open = None
            self.last_high = None
            self.last_low = None
            self.last_close = None

        self.open = self.candle[self.index, 1]
        self.high = self.candle[self.index, 2]
        self.low = self.candle[self.index, 3]
        self.close = self.candle[self.index, 4]

        for currentOrderData in self.currentOrderDatas:
            currentOrderData['processMax'] = max(self.high, currentOrderData['processMax'])
            currentOrderData['processMin'] = min(self.low, currentOrderData['processMin'])
            currentOrderData['processMaxV'] = round(
                (currentOrderData['processMax'] - currentOrderData['buyLine']) / currentOrderData['buyLine'], 5)
            currentOrderData['processMinV'] = round(
                (currentOrderData['processMin'] - currentOrderData['buyLine']) / currentOrderData['buyLine'], 5)

    def get_minute(self):
        return self.minutes[self.index]
