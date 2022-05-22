class Candlestick:

    def __init__(self):
        self.openTime = 0
        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0
        self.volume = 0.0
        self.closeTime = 0
        self.quoteAssetVolume = 0.0
        self.numTrades = 0
        self.takerBuyBaseAssetVolume = 0.0
        self.takerBuyQuoteAssetVolume = 0.0
        self.ignore = 0.0

    def toArray(self):
        outArr = []

        outArr.append(self.openTime)
        outArr.append(self.open)
        outArr.append(self.high)
        outArr.append(self.low)
        outArr.append(self.close)
        outArr.append(self.volume)
        outArr.append(self.closeTime)
        outArr.append(self.quoteAssetVolume)
        outArr.append(self.numTrades)
        outArr.append(self.takerBuyBaseAssetVolume)
        outArr.append(self.takerBuyQuoteAssetVolume)
        outArr.append(self.ignore)

        return outArr

    @staticmethod
    def json_parse(json_data):
        result = Candlestick()
        val = json_data.convert_2_list()
        result.openTime = val[0]
        result.open = float(val[1])
        result.high = float(val[2])
        result.low = float(val[3])
        result.close = float(val[4])
        result.volume = float(val[5])
        result.closeTime = val[6]
        result.quoteAssetVolume = float(val[7])
        result.numTrades = float(val[8])
        result.takerBuyBaseAssetVolume = float(val[9])
        result.takerBuyQuoteAssetVolume = float(val[10])
        result.ignore = val[11]
  
        return result