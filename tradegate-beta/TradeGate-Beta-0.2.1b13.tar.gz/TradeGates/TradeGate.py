from Exchanges import BinanceExchange, BybitExchange, KuCoinExchange


class TradeGate:
    def __init__(self, configDict, sandbox=False):
        self.exchangeName = configDict['exchangeName']
        exchangeClass = self.getCorrectExchange(self.exchangeName)
        if sandbox:
            self.apiKey = configDict['credentials']['test']['spot']['key']
            self.apiSecret = configDict['credentials']['test']['spot']['secret']

            self.exchange = exchangeClass(configDict['credentials']['test'], sandbox=True)
        else:
            self.apiKey = configDict['credentials']['main']['spot']['key']
            self.apiSecret = configDict['credentials']['main']['spot']['secret']

            self.exchange = exchangeClass(configDict['credentials']['main'], sandbox=False)

    def getBalance(self, asset=None, futures=False):
        return self.exchange.getBalance(asset, futures)

    @staticmethod
    def getCorrectExchange(exchangeName):
        if exchangeName.lower() == 'binance':
            return BinanceExchange.BinanceExchange
        if exchangeName.lower() == 'bybit':
            return BybitExchange.BybitExchange
        if exchangeName.lower() == 'kucoin':
            return KuCoinExchange.KuCoinExchange

    def createAndTestSpotOrder(self, symbol, side, orderType, quantity=None, price=None, timeInForce=None,
                               stopPrice=None, icebergQty=None, newOrderRespType=None, recvWindow=None,
                               newClientOrderId=None):

        return self.exchange.createAndTestSpotOrder(symbol, side, orderType, quantity, price, timeInForce, stopPrice,
                                                    icebergQty, newOrderRespType, recvWindow, newClientOrderId)

    def makeSpotOrder(self, orderData):
        return self.exchange.makeSpotOrder(orderData)

    def getSymbolOrders(self, symbol, futures=False, orderId=None, startTime=None, endTime=None, limit=None):
        return self.exchange.getSymbolOrders(symbol=symbol, futures=futures, orderId=orderId, startTime=startTime,
                                             endTime=endTime, limit=limit)

    def getOpenOrders(self, symbol, futures=False):
        return self.exchange.getOpenOrders(symbol, futures)

    def getOrder(self, symbol, orderId=None, localOrderId=None, futures=False):
        return self.exchange.getOrder(symbol, orderId, localOrderId, futures=futures)

    def cancelAllSymbolOpenOrders(self, symbol, futures=False):
        return self.exchange.cancelAllSymbolOpenOrders(symbol, futures)

    def cancelOrder(self, symbol, orderId=None, localOrderId=None, futures=False):
        return self.exchange.cancelOrder(symbol, orderId, localOrderId, futures)

    def getTradingFees(self):
        return self.exchange.getTradingFees()

    def getSymbolTickerPrice(self, symbol, futures=False):
        return self.exchange.getSymbolTickerPrice(symbol, futures)

    def getSymbolKlines(self, symbol, interval, startTime=None, endTime=None, limit=None, futures=False, blvtnav=False,
                        convertDateTime=False, doClean=False, toCleanDataframe=False):
        return self.exchange.getSymbolKlines(symbol, interval, startTime, endTime, limit, futures, blvtnav,
                                             convertDateTime, doClean, toCleanDataframe)

    def getExchangeTime(self, futures=False):
        return self.exchange.getExchangeTime(futures)

    def createAndTestFuturesOrder(self, symbol, side, orderType, positionSide=None, timeInForce=None, quantity=None,
                                  reduceOnly=None, price=None, newClientOrderId=None,
                                  stopPrice=None, closePosition=None, activationPrice=None, callbackRate=None,
                                  workingType=None, priceProtect=None, newOrderRespType=None,
                                  recvWindow=None, extraParams=None):

        return self.exchange.createAndTestFuturesOrder(symbol, side, orderType, positionSide, timeInForce,
                                                       quantity, reduceOnly, price, newClientOrderId, stopPrice,
                                                       closePosition, activationPrice, callbackRate, workingType,
                                                       priceProtect, newOrderRespType, recvWindow, extraParams)

    def makeFuturesOrder(self, futuresOrderData):
        return self.exchange.makeFuturesOrder(futuresOrderData)

    def makeBatchFuturesOrder(self, batchOrders):
        return self.exchange.makeBatchFuturesOrder(batchOrders)

    # def cancelAllSymbolFuturesOrdersWithCountDown(self, symbol, countdownTime):
    #     return self.exchange.cancellAllSymbolFuturesOrdersWithCountDown(symbol, countdownTime)

    def changeInitialLeverage(self, symbol, leverage):
        return self.exchange.changeInitialLeverage(symbol, leverage)

    def changeMarginType(self, symbol, marginType, params=None):
        return self.exchange.changeMarginType(symbol, marginType, params)

    def changePositionMargin(self, symbol, amount, marginType):
        return self.exchange.changePositionMargin(symbol, amount, marginType)

    def getPosition(self):
        return self.exchange.getPosition()

    def spotBestBidAsks(self, symbol=None):
        return self.exchange.spotBestBidAsks(symbol)

    def getSymbolOrderBook(self, symbol, limit=None, futures=False):
        return self.exchange.getSymbolOrderBook(symbol, limit, futures)

    def getSymbolRecentTrades(self, symbol, limit=None, futures=False):
        return self.exchange.getSymbolRecentTrades(symbol, limit, futures)

    def symbolAccountTradeHistory(self, symbol, futures=False, fromId=None, limit=None):
        return self.exchange.symbolAccountTradeHistory(symbol=symbol, futures=futures, fromId=fromId, limit=limit)

    def makeSlTpLimitFuturesOrder(self, symbol, orderSide, quantity=None, quoteQuantity=None, enterPrice=None,
                                  takeProfit=None, stopLoss=None, leverage=None, marginType=None):
        return self.exchange.makeSlTpLimitFuturesOrder(symbol, orderSide, quantity, quoteQuantity, enterPrice,
                                                       takeProfit, stopLoss, leverage, marginType)

    def makeSlTpMarketFuturesOrder(self, symbol, orderSide, quantity=None, quoteQuantity=None,
                                   takeProfit=None, stopLoss=None, leverage=None, marginType=None):
        return self.exchange.makeSlTpMarketFuturesOrder(symbol, orderSide, quantity, quoteQuantity, takeProfit,
                                                        stopLoss, leverage, marginType)

    def getPositionInfo(self, symbol=None):
        return self.exchange.getPositionInfo(symbol)

    def getSymbolMinTrade(self, symbol, futures=False):
        return self.exchange.getSymbolMinTrade(symbol, futures)

    def getIncomeHistory(self, symbol, incomeType=None, startTime=None, endTime=None, limit=None):
        return self.exchange.getIncomeHistory(symbol, incomeType, startTime, endTime, limit)

    def getSymbolList(self, futures=True):
        return self.exchange.getSymbolList(futures=futures)

    def getSymbol24hChanges(self, futures=False):
        return self.exchange.getSymbol24hChanges(futures=futures)

    def getLatestSymbolNames(self, numOfSymbols=None, futures=True):
        return self.exchange.getLatestSymbolNames(numOfSymbols=numOfSymbols, futures=futures)
