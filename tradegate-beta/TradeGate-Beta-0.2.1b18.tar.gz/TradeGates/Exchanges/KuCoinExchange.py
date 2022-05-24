import time
from datetime import datetime

import pandas as pd

from Exchanges.BaseExchange import BaseExchange
from Utils import KuCoinHelpers
from kucoin.client import User, Trade, Market
from kucoin_futures.client import FuturesUser, FuturesTrade, FuturesMarket


class KuCoinExchange(BaseExchange):
    timeIntervals = ['1min', '3min', '5min', '15min', '30min', '1hour', '2hour', '4hour', '6hour', '8hour', '12hour',
                     '1day', '1week']

    timeIntervalTranslate = {'1m': '1min', '3m': '3min', '5m': '5min', '15m': '15min', '30m': '30min', '1h': '1hour',
                             '2h': '2hour', '4h': '4hour', '6h': '6hour', '8h': '8hour', '12h': '12hour', '1d': '1day',
                             '1w': '1week'}

    def __init__(self, credentials, sandbox=False, unifiedInOuts=True):
        self.spotApiKey = credentials['spot']['key']
        self.spotSecret = credentials['spot']['secret']
        self.spotPassphrase = credentials['spot']['passphrase']

        self.futuresApiKey = credentials['futures']['key']
        self.futuresSecret = credentials['futures']['secret']
        self.futuresPassphrase = credentials['futures']['passphrase']

        self.sandbox = sandbox
        self.unifiedInOuts = unifiedInOuts

        if sandbox:
            self.spotUser = User(key=self.spotApiKey, secret=self.spotSecret, passphrase=self.spotPassphrase,
                                 is_sandbox=True)
            self.spotTrade = Trade(key=self.spotApiKey, secret=self.spotSecret, passphrase=self.spotPassphrase,
                                   is_sandbox=True)
            self.spotMarket = Market(key=self.spotApiKey, secret=self.spotSecret, passphrase=self.spotPassphrase,
                                     is_sandbox=True)

            self.futuresUser = FuturesUser(key=self.futuresApiKey, secret=self.futuresSecret,
                                           passphrase=self.futuresPassphrase, is_sandbox=True)
            self.futuresTrade = FuturesTrade(key=self.futuresApiKey, secret=self.futuresSecret,
                                             passphrase=self.futuresPassphrase, is_sandbox=True)
            self.futuresMarket = FuturesMarket(key=self.futuresApiKey, secret=self.futuresSecret,
                                               passphrase=self.futuresPassphrase, is_sandbox=True)
        else:
            self.spotUser = User(key=self.spotApiKey, secret=self.spotSecret, passphrase=self.spotPassphrase)
            self.spotTrade = Trade(key=self.spotApiKey, secret=self.spotSecret, passphrase=self.spotPassphrase)
            self.spotMarket = Market(key=self.spotApiKey, secret=self.spotSecret, passphrase=self.spotPassphrase)

            self.futuresUser = FuturesUser(key=self.futuresApiKey, secret=self.futuresSecret,
                                           passphrase=self.futuresPassphrase)
            self.futuresTrade = FuturesTrade(key=self.futuresApiKey, secret=self.futuresSecret,
                                             passphrase=self.futuresPassphrase)
            self.futuresMarket = FuturesMarket(key=self.futuresApiKey, secret=self.futuresSecret,
                                               passphrase=self.futuresPassphrase)

    def getBalance(self, asset=None, futures=False):
        if futures:
            raise NotImplementedError()
        else:
            if asset is None:
                return KuCoinHelpers.unifyGetBalanceSpotOut(self.spotUser.get_account_list(currency=asset))
            else:
                return KuCoinHelpers.unifyGetBalanceSpotOut(self.spotUser.get_account_list(currency=asset),
                                                            isSingle=True)

    def symbolAccountTradeHistory(self, symbol, futures=False, fromId=None, limit=None):
        if futures:
            raise NotImplementedError()
        else:

            return KuCoinHelpers.unifyTradeHistory(self.spotTrade.get_fill_list(tradeType='TRADE')['items'])

    def testSpotOrder(self, orderData):
        pass

    def makeSpotOrder(self, orderData):
        pass

    def createAndTestSpotOrder(self, symbol, side, orderType, quantity=None, price=None, timeInForce=None,
                               stopPrice=None, icebergQty=None, newOrderRespType=None, recvWindow=None,
                               newClientOrderId=None):
        pass

    def getSymbolOrders(self, symbol, futures=False, orderId=None, startTime=None, endTime=None, limit=None):
        pass

    def getOpenOrders(self, symbol, futures=False):
        pass

    def cancelAllSymbolOpenOrders(self, symbol, futures=False):
        pass

    def cancelOrder(self, symbol, orderId=None, localOrderId=None, futures=False):
        pass

    def getOrder(self, symbol, orderId=None, localOrderId=None, futures=False):
        pass

    def getTradingFees(self, symbol=None, futures=False):
        if futures:
            if symbol is None:
                raise ValueError('Must specify futures contract symbol name.')
            contractInfo = self.futuresMarket.get_contract_detail(symbol=symbol)
            return {
                'symbol': contractInfo['symbol'],
                'takerFeeRate': contractInfo['takerFeeRate'],
                'makerFeeRate': contractInfo['makerFeeRate']
            }
        else:
            if symbol is None:
                return self.spotUser.get_base_fee()['data']
            else:
                return self.spotUser.get_actual_fee(symbols=[symbol])['data']

    def getSymbolTickerPrice(self, symbol, futures=False):
        if futures:
            return float(self.futuresMarket.get_ticker(symbol=symbol)['price'])
        else:
            return float(self.spotMarket.get_ticker(symbol=symbol)['price'])

    def getSymbolKlines(self, symbol, interval, startTime=None, endTime=None, limit=500, futures=False, blvtnav=False,
                        convertDateTime=False, doClean=False, toCleanDataframe=False):
        if interval not in KuCoinExchange.timeIntervals:
            if interval in KuCoinExchange.timeIntervalTranslate.keys():
                timeInterval = KuCoinExchange.timeIntervalTranslate[interval]
            else:
                raise ValueError('Time interval is not valid.')
        else:
            timeInterval = interval

        if futures:
            data = self._getFuturesSymbolKlines(endTime, timeInterval, limit, startTime, symbol)
        else:
            data = self._getSpotSymbolKlines(endTime, timeInterval, limit, startTime, symbol)

        if convertDateTime or toCleanDataframe:
            if futures:
                for datum in data:
                    datum.append(datum[-1])
                    datum[-1] = datetime.fromtimestamp((float(datum[0]) - 1) / 1000)
                    datum[0] = datetime.fromtimestamp(float(datum[0]) / 1000)
                    datum.append(None)
            else:
                for datum in data:
                    datum.append(datum[-1])
                    datum[-2] = datetime.fromtimestamp(float(datum[0]) - 1)
                    datum[0] = datetime.fromtimestamp(float(datum[0]))

        if doClean or toCleanDataframe:
            if toCleanDataframe:
                cleanDataFrame = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume',
                                                             'closeDate', 'tradesNum'])
                cleanDataFrame.set_index('date', inplace=True)
                cleanDataFrame[cleanDataFrame.columns[:5]] = cleanDataFrame[cleanDataFrame.columns[:5]].apply(
                    pd.to_numeric, errors='coerce')
                cleanDataFrame[cleanDataFrame.columns[-1]] = cleanDataFrame[cleanDataFrame.columns[-1]].apply(
                    pd.to_numeric, errors='coerce')
                return cleanDataFrame
            return data
        else:
            return data

    def _getSpotSymbolKlines(self, endTime, timeInterval, limit, startTime, symbol):
        if limit is None:
            if startTime is None:
                if endTime is None:
                    data = self.spotMarket.get_kline(symbol=symbol, kline_type=timeInterval)
                else:
                    raise ValueError('Can\'t use endTime without limit.')
            else:
                if endTime is None:
                    data = self.spotMarket.get_kline(symbol=symbol, kline_type=timeInterval, startAt=startTime)
                else:
                    data = self.spotMarket.get_kline(symbol=symbol, kline_type=timeInterval, startAt=startTime,
                                                     endAt=endTime)
        else:
            if startTime is None:
                if endTime is None:
                    startAt = int(time.time()) - limit * self._getTimeIntervalInSeconds(timeInterval)
                    data = self.spotMarket.get_kline(symbol=symbol, kline_type=timeInterval, startAt=startAt,
                                                     endAt=int(time.time()))
                else:
                    startAt = endTime - limit * self._getTimeIntervalInSeconds(timeInterval)
                    data = self.spotMarket.get_kline(symbol=symbol, kline_type=timeInterval, startAt=startAt,
                                                     endAt=endTime)
            else:
                if endTime is None:
                    endAt = startTime + limit * self._getTimeIntervalInSeconds(timeInterval)
                    data = self.spotMarket.get_kline(symbol=symbol, kline_type=timeInterval, startAt=startTime,
                                                     endAt=endAt)
                else:
                    data = self.spotMarket.get_kline(symbol=symbol, kline_type=timeInterval, startAt=startTime,
                                                     endAt=endTime)
        return data[::-1]

    def _getFuturesSymbolKlines(self, endTime, timeInterval, limit, startTime, symbol):
        granularity = int(self._getTimeIntervalInSeconds(timeInterval) / 60)
        if limit is None:
            if startTime is None:
                if endTime is None:
                    data = self.futuresMarket.get_kline_data(symbol=symbol, granularity=granularity)
                else:
                    endTime = endTime - endTime % (granularity * 60)
                    data = self.futuresMarket.get_kline_data(symbol=symbol, granularity=granularity,
                                                             end_t=endTime * 1000)
            else:
                if endTime is None:
                    startTime = startTime - startTime % (granularity * 60)
                    data = self.futuresMarket.get_kline_data(symbol=symbol, granularity=granularity,
                                                             begin_t=startTime * 1000)
                else:
                    endTime = endTime - endTime % (granularity * 60)
                    startTime = startTime - startTime % (granularity * 60)

                    data = self.futuresMarket.get_kline_data(symbol=symbol, granularity=granularity,
                                                             begin_t=startTime * 1000, end_t=endTime * 1000)
        else:
            if startTime is None:
                if endTime is None:
                    endTime = int(time.time())
                    endTime = endTime - endTime % (granularity * 60)

                    startAt = endTime - limit * granularity * 60
                    startAt = startAt - startAt % (granularity * 60)

                    data = self.futuresMarket.get_kline_data(symbol=symbol, granularity=granularity,
                                                             begin_t=startAt * 1000)
                else:
                    endTime = endTime - endTime % (granularity * 60)

                    startTime = endTime - limit * granularity * 60
                    startTime = startTime - startTime % (granularity * 60)

                    data = self.futuresMarket.get_kline_data(symbol=symbol, granularity=granularity,
                                                             begin_t=startTime * 1000, end_t=endTime * 1000)
            else:
                if endTime is None:
                    startTime = startTime - startTime % (granularity * 60)

                    endTime = startTime + limit * granularity * 60
                    endTime = endTime - endTime % (granularity * 60)

                    data = self.futuresMarket.get_kline_data(symbol=symbol, granularity=granularity,
                                                             begin_t=startTime * 1000, end_t=endTime * 1000)
                else:
                    startTime = startTime - startTime % (granularity * 60)
                    endTime = endTime - endTime % (granularity * 60)

                    data = self.futuresMarket.get_kline_data(symbol=symbol, granularity=granularity,
                                                             begin_t=startTime * 1000, end_t=endTime * 1000)
        return data

    def _getTimeIntervalInSeconds(self, timeInterval):
        if not timeInterval in self.timeIntervals:
            raise ValueError('Time interval is not valid.')

        if timeInterval == '1min':
            return 60
        elif timeInterval == '3min':
            return 3 * 60
        elif timeInterval == '5min':
            return 5 * 60
        elif timeInterval == '15min':
            return 15 * 60
        elif timeInterval == '30min':
            return 40 * 60
        elif timeInterval == '1hour':
            return 3600
        elif timeInterval == '2hour':
            return 2 * 3600
        elif timeInterval == '4hour':
            return 4 * 3600
        elif timeInterval == '6hour':
            return 6 * 3600
        elif timeInterval == '8hour':
            return 8 * 3600
        elif timeInterval == '12hour':
            return 12 * 3600
        elif timeInterval == '1day':
            return 24 * 3600
        elif timeInterval == '1week':
            return 7 * 24 * 3600

    def getExchangeTime(self, futures=False):
        if futures:
            return self.futuresMarket.get_server_timestamp()
        else:
            return self.spotMarket.get_server_timestamp()

    def getSymbol24hTicker(self, symbol):
        pass

    def testFuturesOrder(self, futuresOrderData):
        pass

    def makeFuturesOrder(self, futuresOrderData):
        pass

    def createAndTestFuturesOrder(self, symbol, side, orderType, positionSide=None, timeInForce=None, quantity=None,
                                  reduceOnly=None, price=None, newClientOrderId=None,
                                  stopPrice=None, closePosition=None, activationPrice=None, callbackRate=None,
                                  workingType=None, priceProtect=None, newOrderRespType=None,
                                  recvWindow=None, extraParams=None):
        pass

    def makeBatchFuturesOrder(self, futuresOrderDatas):
        pass

    def changeInitialLeverage(self, symbol, leverage):
        pass

    def changeMarginType(self, symbol, marginType, params):
        pass

    def changePositionMargin(self, symbol, amount, marginType=None):
        pass

    def getPosition(self):
        pass

    def spotBestBidAsks(self, symbol=None):
        pass

    def getSymbolOrderBook(self, symbol, limit=None, futures=False):
        if futures:
            orderBook = self.futuresMarket.l2_order_book(symbol)
            return orderBook
        else:
            orderBook = self.spotMarket.get_aggregated_order(symbol)
            return orderBook

    def getSymbolRecentTrades(self, symbol, limit=None, futures=False):
        if futures:
            tradeHistory = self.futuresMarket.get_trade_history(symbol=symbol)
            return KuCoinHelpers.unifyRecentTrades(tradeHistory, futures=True)
        else:
            tradeHistory = self.spotMarket.get_trade_histories(symbol=symbol)
            return KuCoinHelpers.unifyRecentTrades(tradeHistory)

    def getPositionInfo(self, symbol=None):
        pass

    def getSymbolMinTrade(self, symbol, futures=False):
        pass

    def makeSlTpLimitFuturesOrder(self, symbol, orderSide, quantity=None, quoteQuantity=None, enterPrice=None,
                                  takeProfit=None, stopLoss=None, leverage=None, marginType=None):
        pass

    def getSymbol24hChanges(self, futures=False):
        changesList = []
        if futures:
            for ticker in self.futuresMarket.get_contracts_list():
                changesList.append((ticker['symbol'], float(ticker['priceChgPct']) * 100))
        else:
            for ticker in self.spotMarket.get_all_tickers()['ticker']:
                changesList.append((ticker['symbol'], float(ticker['changeRate']) * 100))

        return sorted(changesList, key=lambda x: x[1], reverse=True)

    def getSymbolList(self, futures=False):
        symbolNames = []
        if futures:
            for ticker in self.futuresMarket.get_contracts_list():
                symbolNames.append(ticker['symbol'])
        else:
            for ticker in self.spotMarket.get_all_tickers()['ticker']:
                symbolNames.append(ticker['symbol'])

        return symbolNames

    def getLatestSymbolNames(self, numOfSymbols=None, futures=False):
        symbolDatas = []
        if futures:
            for symbolInfo in self.futuresMarket.get_contracts_list():
                symbolDatas.append(
                    (symbolInfo['symbol'], datetime.fromtimestamp(float(symbolInfo['firstOpenDate']) / 1000)))
                symbolDatas.sort(key=lambda x: x[1], reverse=True)
        else:
            pass
