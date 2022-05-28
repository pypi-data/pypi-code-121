from ktrader.candle_trader.component.record import Record


class Period():

    def __init__(self, record):
        self.__record: Record = record

    def isPeriodAllowd(self, index, periods):
        if not periods or not periods[0]:
            return False
        for [minute_start, minute_end] in periods:
            if self.__record.minutes[index] >= minute_start and self.__record.minutes[index] <= minute_end:
                return True
        return False

    def isPeriodBuy(self, index=None):
        return self.isPeriodAllowd(
            index=index or self.__record.index,
            periods=self.__record.rule.BUY_PERIODS,
        )

    def isPeriodSell(self, index=None):
        return self.isPeriodAllowd(
            index=index or self.__record.index,
            periods=self.__record.rule.SELL_PERIODS,
        )

    def isPeriodThrow(self, index=None):
        return self.isPeriodAllowd(
            index=index or self.__record.index,
            periods=self.__record.rule.THROW_PERIODS,
        )
