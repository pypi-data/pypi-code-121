import logging
import warnings
from datetime import datetime

from pybit import HTTP

from Exchanges.BaseExchange import BaseExchange
from Utils import DataHelpers, BybitHelpers


def isOrderDataValid(orderData: DataHelpers.OrderData):
    if orderData.symbol is None or orderData.quantity is None or orderData.side is None \
            or orderData.orderType is None:
        raise ValueError('Missing mandatory fields.')

    if orderData.orderType not in BybitExchange.spotOrderTypes:
        raise ValueError('Order type not correctly specified. Available order types for spot market: {}'.format(
            BybitExchange.spotOrderTypes))

    if orderData.side not in ['BUY', 'SELL']:
        raise ValueError('Order side can only be \'BUY\' or \'SELL\'')

    if orderData.timeInForce not in BybitExchange.spotTimeInForces:
        raise ValueError(
            'Time-in-force not correctly specified. Available time-in-force for spot market: {}'.format(
                BybitExchange.spotTimeInForces))

    if orderData.orderType in ['LIMIT', 'LIMIT_MAKER'] and orderData.price is None:
        raise ValueError('Price must be specified for limit orders.')


def isFuturesOrderDataValid(orderData: DataHelpers.futuresOrderData):
    if orderData.symbol is None:
        raise ValueError('Specify symbol.')
    if orderData.quantity is None:
        raise ValueError('Specify quantity.')
    if orderData.side is None:
        raise ValueError('Specify order side.')
    if orderData.orderType is None:
        raise ValueError('Specify order type.')
    if orderData.timeInForce is None:
        raise ValueError('Specify timeInForce.')
    if orderData.closePosition is None:
        raise ValueError('Specify closePosition.')
    if orderData.reduceOnly is None:
        raise ValueError('Specify reduceOnly.')

    if orderData.orderType not in BybitExchange.futuresOrderTypes:
        raise ValueError('Bad order type specified. Available order types for futures: {}'.format(
            BybitExchange.futuresOrderTypes))

    if orderData.orderType.startswith('STOP'):
        if orderData.extraParams is None:
            raise ValueError('Specify \'basePrice\' in \'extraParams\'')
        if 'basePrice' not in orderData.extraParams.keys():
            raise ValueError('Specify \'basePrice\' in \'extraParams\'')
        if orderData.stopPrice is None:
            raise ValueError('Specify \'stopPrice\'.')

    if 'LIMIT' in orderData.orderType and orderData.price is None:
        raise ValueError('Specify \'price\' for limit orders.')

    if orderData.timeInForce not in BybitExchange.futuresTimeInForces.keys() and \
            orderData.timeInForce not in BybitExchange.futuresTimeInForces.values():
        raise ValueError('\'timeInForce\' is not correct.')

    if orderData.extraParams is not None:
        if 'triggerBy' in orderData.extraParams.keys() \
                and orderData.extraParams['tpTriggerBy'] not in ['LastPrice', 'IndexPrice', 'MarkPrice']:
            raise ValueError('\'triggerBy\' was not correctly specified.')

        if 'tpTriggerBy' in orderData.extraParams.keys() \
                and orderData.extraParams['tpTriggerBy'] not in ['LastPrice', 'IndexPrice', 'MarkPrice']:
            raise ValueError('\'tpTriggerBy\' was not correctly specified.')

        if 'slTriggerBy' in orderData.extraParams.keys() \
                and orderData.extraParams['slTriggerBy'] not in ['LastPrice', 'IndexPrice', 'MarkPrice']:
            raise ValueError('\'slTriggerBy\' was not correctly specified.')

        if 'positionIdx' in orderData.extraParams.keys() and orderData.extraParams['positionIdx'] not in [0, 1, 2]:
            raise ValueError('\'positionIdx\' was not correctly specified.')


class PyBitHTTP(HTTP):
    def __init__(self, endpoint=None, api_key=None, api_secret=None, logging_level=logging.INFO, log_requests=False,
                 request_timeout=10, recv_window=5000, force_retry=False, retry_codes=None, ignore_codes=None,
                 max_retries=3, retry_delay=3, referral_id=None, spot=False):
        super().__init__(endpoint, api_key, api_secret, logging_level, log_requests, request_timeout, recv_window,
                         force_retry, retry_codes, ignore_codes, max_retries, retry_delay, referral_id, spot)

    def query_history_order(self, **kwargs):
        if self.spot is True:
            suffix = '/spot/v1/history-orders'

            return self._submit_request(
                method='GET',
                path=self.endpoint + suffix,
                query=kwargs,
                auth=True
            )
        else:
            raise NotImplementedError('Not implemented for futures market.')

    def get_active_order_spot(self, **kwargs):
        if self.spot is True:
            suffix = '/spot/v1/order'

            return self._submit_request(
                method='GET',
                path=self.endpoint + suffix,
                query=kwargs,
                auth=True
            )
        else:
            raise NotImplementedError('Not implemented for futures market.')


class BybitExchange(BaseExchange):
    timeIndexesInCandleData = [0, 6]
    desiredCandleDataIndexes = [0, 1, 2, 3, 4, 5, 6, 8]

    spotOrderTypes = ['LIMIT', 'MARKET', 'LIMIT_MAKER']
    spotTimeInForces = ['GTC', 'FOK', 'IOC']

    futuresOrderTypes = ['MARKET', 'LIMIT', 'STOP_MARKET', 'STOP_LIMIT']
    futuresTimeInForces = {'GTC': 'GoodTillCancel', 'IOC': 'ImmediateOrCancel', 'FIK': 'FillOrKill', 'PO': 'PostOnly'}

    timeIntervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '1w', '1M']

    def __init__(self, credentials, sandbox=False, unifiedInOuts=True):
        self.apiKey = credentials['spot']['key']
        self.secret = credentials['spot']['secret']
        self.sandbox = sandbox
        self.unifiedInOuts = unifiedInOuts

        if sandbox:
            self.spotSession = PyBitHTTP("https://api-testnet.bybit.com", api_key=self.apiKey, api_secret=self.secret,
                                         spot=True)
            self.futuresSession = PyBitHTTP("https://api-testnet.bybit.com", api_key=self.apiKey,
                                            api_secret=self.secret)
        else:
            self.spotSession = PyBitHTTP("https://api.bybit.com", api_key=self.apiKey, api_secret=self.secret,
                                         spot=True)
            self.futuresSession = PyBitHTTP("https://api.bybit.com", api_key=self.apiKey, api_secret=self.secret)

        self.futuresSymbols = []
        for symbol in self.futuresSession.query_symbol()['result']:
            if symbol['name'].endswith('USDT'):
                self.futuresSymbols.append(symbol['name'])

    def getBalance(self, asset='', futures=False):
        if futures:
            if asset in [None, '']:
                return BybitHelpers.getBalanceOut(self.futuresSession.get_wallet_balance()['result'], futures=True)
            else:
                return BybitHelpers.getBalanceOut(self.futuresSession.get_wallet_balance(coin=asset)['result'],
                                                  single=True, futures=True)
        else:
            if asset in [None, '']:
                return BybitHelpers.getBalanceOut(self.spotSession.get_wallet_balance()['result']['balances'])
            else:
                assets = self.spotSession.get_wallet_balance()['result']['balances']
                for coin in assets:
                    if asset == coin['coin']:
                        return BybitHelpers.getBalanceOut(coin, single=True)

                try:
                    self.futuresSession.get_wallet_balance(coin=asset)
                    return BybitHelpers.makeDummyBalance(asset)
                except Exception:
                    raise ValueError('Coin not found.')

    def symbolAccountTradeHistory(self, symbol, futures=False, fromId=None, limit=None):
        if futures:
            tradeHistory = self.futuresSession.user_trade_records(symbol=symbol, limit=limit, fromId=fromId)
            return BybitHelpers.getMyTradeHistoryOut(tradeHistory['result']['data'], futures=True)
        else:
            tradeHistory = self.spotSession.user_trade_records(symbol=symbol, limit=limit, fromId=fromId)
            return BybitHelpers.getMyTradeHistoryOut(tradeHistory['result'])

    def testSpotOrder(self, orderData: DataHelpers.OrderData):
        isOrderDataValid(orderData)

        if orderData.icebergQty is not None or orderData.newOrderRespType is not None \
                or orderData.quoteOrderQty is not None or orderData.recvWindow is not None \
                or orderData.stopPrice is not None:
            warnings.warn('Some of the given parameters have no use in ByBit exchange.')

        return orderData

    def makeSpotOrder(self, orderData):
        orderParams = BybitHelpers.getSpotOrderAsDict(orderData)

        return BybitHelpers.getMakeSpotOrderOut(self.spotSession.place_active_order(**orderParams)['result'])

    def createAndTestSpotOrder(self, symbol, side, orderType, quantity=None, price=None, timeInForce=None,
                               stopPrice=None, icebergQty=None, newOrderRespType=None, recvWindow=None,
                               newClientOrderId=None):

        currOrder = DataHelpers.setSpotOrderData(icebergQty, newClientOrderId, newOrderRespType, orderType, price,
                                                 quantity,
                                                 recvWindow, side, stopPrice, symbol, timeInForce)

        self.testSpotOrder(currOrder)

        return currOrder

    def getSymbolOrders(self, symbol, futures=False, orderId=None, startTime=None, endTime=None, limit=None):
        if futures:
            historyList = []
            pageNumber = 1
            endTimeString = None
            startTimeString = None
            done = False
            while not done:
                history = self.futuresSession.get_active_order(symbol=symbol, page=pageNumber, limit=50)

                if startTime is not None:
                    startTimeString = startTime.strftime('%Y-%m-%dT%H:%M:%SZ')
                if endTime is not None:
                    endTimeString = endTime.strftime('%Y-%m-%dT%H:%M:%SZ')

                for order in history['result']['data']:
                    if endTime is not None:
                        if endTimeString < order['create_time']:
                            continue

                    if startTime is not None:
                        if order['created_time'] < startTimeString:
                            done = True
                            break

                    historyList.append(order)

                if limit is not None and limit <= len(historyList):
                    done = True

                if len(history['result']['data']) < 50:
                    done = True

                pageNumber += 1

            return historyList
        else:
            history = self.spotSession.query_history_order(symbol=symbol, orderId=orderId, startTime=startTime,
                                                           endtime=endTime, limit=limit)
            return history['result']

    def getOpenOrders(self, symbol, futures=False):
        if futures:
            openOrders = []

            openActiveOrders = self.futuresSession.query_active_order(symbol=symbol)
            for activeOrder in openActiveOrders['result']:
                openOrders.append(BybitHelpers.futuresOrderOut(activeOrder))

            openConditionalOrders = self.futuresSession.query_conditional_order(symbol=symbol)
            for conditionalOrder in openConditionalOrders['result']:
                openOrders.append(BybitHelpers.futuresOrderOut(conditionalOrder, isConditional=True))

            return openOrders
        else:
            if symbol is None:
                openOrders = self.spotSession.query_active_order()['result']
            else:
                openOrders = self.spotSession.query_active_order(symbol=symbol)['result']
            return BybitHelpers.getOpenOrdersOut(openOrders)

    def cancelAllSymbolOpenOrders(self, symbol, futures=False):
        if futures:
            canceledOrdersIds = []
            result = self.futuresSession.cancel_all_active_orders(symbol=symbol)
            canceledOrdersIds.append(result['result'])

            result = self.futuresSession.cancel_all_conditional_orders(symbol=symbol)
            canceledOrdersIds.append(result['result'])
        else:
            result = self.spotSession.batch_fast_cancel_active_order(symbol=symbol,
                                                                     orderTypes="LIMIT,LIMIT_MAKER,MARKET")
            return result['result']['success']

    def cancelOrder(self, symbol, orderId=None, localOrderId=None, futures=False):
        if futures:
            if orderId is not None:
                try:
                    result = self.futuresSession.cancel_active_order(symbol=symbol, order_id=orderId)
                except Exception as e:
                    try:
                        result = self.futuresSession.cancel_conditional_order(symbol=symbol, order_id=orderId)
                    except Exception as e:
                        raise RuntimeError('Problem in canceling order in bybit: {}'.format(str(e)))
            elif localOrderId is not None:
                try:
                    result = self.futuresSession.cancel_active_order(symbol=symbol, order_link_id=localOrderId)
                except Exception as e:
                    try:
                        result = self.futuresSession.cancel_conditional_order(symbol=symbol, order_link_id=localOrderId)
                    except Exception as e:
                        raise RuntimeError('Problem in canceling order in bybit: {}'.format(str(e)))
            else:
                raise ValueError('Must specify either \'orderId\' or \'localOrderId\'')

            return result['result']
        else:
            if orderId is not None:
                result = self.spotSession.cancel_active_order(orderId=orderId)
            elif localOrderId is not None:
                result = self.spotSession.cancel_active_order(orderLinkId=localOrderId)
            else:
                raise ValueError('Must specify either \'orderId\' or \'localOrderId\'')
            return result['result']

    def getOrder(self, symbol, orderId=None, localOrderId=None, futures=False):
        if futures:
            if orderId is not None:
                try:
                    order = self.futuresSession.query_active_order(symbol=symbol, order_id=orderId)
                except Exception as e:
                    try:
                        order = self.futuresSession.query_conditional_order(symbol=symbol, order_id=orderId)
                    except Exception as e:
                        raise RuntimeError('Problem in fetching order from bybit: {}'.format(str(e)))
            elif localOrderId is not None:
                try:
                    order = self.futuresSession.query_active_order(symbol=symbol, order_link_id=localOrderId)
                except Exception as e:
                    try:
                        order = self.futuresSession.query_conditional_order(symbol=symbol, order_link_id=localOrderId)
                    except Exception as e:
                        raise RuntimeError('Problem in fetching order from bybit: {}'.format(str(e)))
            else:
                raise ValueError('Specify either order Id in the exchange or local Id sent with the order')

            return BybitHelpers.futuresOrderOut(order['result'])
        else:
            if orderId is not None:
                try:
                    order = self.spotSession.get_active_order_spot(orderId=orderId)['result']
                except Exception as e:
                    raise RuntimeError('Problem in fetching order from bybit.')
            elif localOrderId is not None:
                try:
                    order = self.spotSession.get_active_order_spot(orderLinkId=localOrderId)['result']
                except Exception as e:
                    raise RuntimeError('Problem in fetching order from bybit.')
            else:
                raise ValueError('Specify either order Id in the exchange or local Id sent with the order')

            return BybitHelpers.getOrderOut(order)

    def getTradingFees(self, futures=False):
        raise NotImplementedError()

    def getSymbolTickerPrice(self, symbol, futures=False):
        if futures:
            symbolInfo = self.futuresSession.latest_information_for_symbol(symbol=symbol)['result']
            return float(symbolInfo[0]['last_price'])
        else:
            symbolInfo = self.spotSession.latest_information_for_symbol(symbol=symbol)
            return float(symbolInfo['result']['lastPrice'])

    def getSymbolKlines(self, symbol, interval, startTime=None, endTime=None, limit=None, futures=False, blvtnav=False,
                        convertDateTime=False, doClean=False, toCleanDataframe=False):
        if interval not in self.timeIntervals:
            raise ValueError('Time interval is not valid.')

        if futures:
            data = self._getFuturesSymbolKlines(interval, limit, startTime, symbol)
        else:
            data = self._getSpotSymbolKlines(endTime, interval, limit, startTime, symbol)

        if convertDateTime or toCleanDataframe:
            BybitHelpers.klinesConvertDate(data, futures, self.timeIndexesInCandleData)

        if doClean or toCleanDataframe:
            finalDataArray = BybitHelpers.getKlinesDesiredOnlyCols(data, self.desiredCandleDataIndexes)

            if toCleanDataframe:
                return BybitHelpers.klinesConvertToPandas(finalDataArray)
            return finalDataArray
        else:
            return data

    def _getSpotSymbolKlines(self, endTime, interval, limit, startTime, symbol):
        if startTime is not None:
            startTimestamp = startTime.timestamp() * 1000
        else:
            startTimestamp = None
        if endTime is not None:
            endTimestamp = endTime.timestamp() * 1000
        else:
            endTimestamp = None

        if limit is not None:
            if limit > 1000:
                limit = 1000
            elif limit < 1:
                limit = 1
        data = self.spotSession.query_kline(symbol=symbol, interval=interval, startTime=startTimestamp,
                                            endTime=endTimestamp, limit=limit)['result']
        for datum in data:
            for idx in range(len(datum)):
                if idx in self.timeIndexesInCandleData:
                    continue
                datum[idx] = float(datum[idx])
        return data

    def _getFuturesSymbolKlines(self, interval, limit, startTime, symbol):
        futuresInterval = BybitHelpers.convertIntervalToFuturesKlines(interval)
        data = []
        if limit is not None:
            if limit > 200:
                limit = 200
            elif limit < 1:
                limit = 1
        else:
            limit = 200
        if startTime is None:
            startTimestamp = int(
                datetime.now().timestamp() - BybitHelpers.getIntervalInSeconds(interval, self.timeIntervals) * limit)
        else:
            if isinstance(startTime, int):
                startTimestamp = startTime
            else:
                startTimestamp = int(startTime.timestamp)
        candles = self.futuresSession.query_kline(symbol=symbol, interval=futuresInterval, from_time=startTimestamp,
                                                  limit=limit)
        for candle in candles['result']:
            dataArray = [float(candle['open_time']), float(candle['open']), float(candle['high']),
                         float(candle['low']), float(candle['close']), float(candle['volume']),
                         int(candle['open_time']) + BybitHelpers.getIntervalInSeconds(interval, self.timeIntervals),
                         None, None, None, None]
            data.append(dataArray)
        return data

    def getExchangeTime(self, futures=False):
        if futures:
            return self.futuresSession.server_time()['time_now']
        else:
            return int(self.spotSession.server_time()['result']['serverTime'])

    def getSymbol24hTicker(self, symbol):
        raise NotImplementedError()

    def testFuturesOrder(self, futuresOrderData):
        if futuresOrderData.timeInForce is None:
            futuresOrderData.timeInForce = 'GoodTillCancel'

        if futuresOrderData.closePosition is None:
            futuresOrderData.closePosition = False

        if futuresOrderData.reduceOnly is None:
            futuresOrderData.reduceOnly = False

        isFuturesOrderDataValid(futuresOrderData)

        return futuresOrderData

    def makeFuturesOrder(self, futuresOrderData: DataHelpers.futuresOrderData):
        orderParams = BybitHelpers.getFuturesOrderAsDict(futuresOrderData, self.futuresTimeInForces)

        if 'STOP' in futuresOrderData.orderType:
            result = self.futuresSession.place_conditional_order(**orderParams)
            return BybitHelpers.futuresOrderOut(result['result'], isConditional=True)
        else:
            result = self.futuresSession.place_active_order(**orderParams)
            return BybitHelpers.futuresOrderOut(result['result'])

    def createAndTestFuturesOrder(self, symbol, side, orderType, positionSide=None, timeInForce=None, quantity=None,
                                  reduceOnly=None, price=None, newClientOrderId=None,
                                  stopPrice=None, closePosition=None, activationPrice=None, callbackRate=None,
                                  workingType=None, priceProtect=None, newOrderRespType=None,
                                  recvWindow=None, extraParams=None):
        currOrder = DataHelpers.setFuturesOrderData(activationPrice, callbackRate, closePosition, extraParams,
                                                    newClientOrderId, newOrderRespType, orderType, positionSide, price,
                                                    priceProtect, quantity, recvWindow, reduceOnly, side, stopPrice,
                                                    symbol, timeInForce, workingType)

        self.testFuturesOrder(currOrder)

        return currOrder

    def makeBatchFuturesOrder(self, futuresOrderDatas):
        batchOrders = []
        batchConditionalOrders = []
        for order in futuresOrderDatas:
            orderAsDict = BybitHelpers.getFuturesOrderAsDict(order, self.futuresTimeInForces)

            if 'STOP' in order.orderType:
                batchConditionalOrders.append(order)
            else:
                batchOrders.append(orderAsDict)

        results = []
        if len(batchConditionalOrders) > 0:
            putResults = self.futuresSession.place_conditional_order_bulk(batchConditionalOrders)
            for result in putResults:
                results.append(BybitHelpers.futuresOrderOut(result['result'], isConditional=True))
        if len(batchOrders) > 0:
            putResults = self.futuresSession.place_active_order_bulk(batchOrders)
            for result in putResults:
                results.append(BybitHelpers.futuresOrderOut(result['result']))

        return results

    def changeInitialLeverage(self, symbol, leverage):
        return self.futuresSession.set_leverage(symbol=symbol, buy_leverage=leverage, sell_leverage=leverage)

    def changeMarginType(self, symbol, marginType, params):
        try:
            buyLeverage = params['buyLeverage']
            sellLeverage = params['sellLeverage']
            if marginType.upper() == 'ISOLATED':
                isIsolated = True
            elif marginType.upper() == 'CROSS':
                isIsolated = False
            else:
                raise ValueError('Margin type must either be \'ISOLATED\' or \'CROSS\'.')
        except Exception:
            raise ValueError('Must specify \'buyLeverage\' and \'sellLeverage\' in \'params')

        self.futuresSession.cross_isolated_margin_switch(symbol=symbol, is_isolated=isIsolated,
                                                         buy_leverage=buyLeverage, sell_leverage=sellLeverage)
        return True

    def changePositionMargin(self, symbol, amount, marginType=None):
        return self.futuresSession.change_margin(symbol=symbol, margin=amount)['result']

    def getPosition(self):
        return self.futuresSession.my_position()['result']

    def spotBestBidAsks(self, symbol=None):
        return self.spotSession.best_bid_ask_price(symbol=symbol)['result']

    def getSymbolOrderBook(self, symbol, limit=None, futures=False):
        if futures:
            return self.futuresSession.orderbook(symbol=symbol)['result']
        else:
            return self.spotSession.orderbook(symbol=symbol)['result']

    def getSymbolRecentTrades(self, symbol, limit=None, futures=False):
        if futures:
            if limit is not None and limit > 0:
                limit = 1000 if limit > 1000 else limit
            else:
                limit = 500

            recentTrades = self.futuresSession.public_trading_records(symbol=symbol, limit=limit)['result']
            return BybitHelpers.getRecentTradeHistoryOut(recentTrades, futures=True)
        else:
            if limit is not None and limit > 0:
                limit = 60 if limit > 60 else limit
            else:
                limit = 60

            recentTrades = self.spotSession.public_trading_records(symbol=symbol, limit=limit)['result']
            return BybitHelpers.getRecentTradeHistoryOut(recentTrades)

    def getPositionInfo(self, symbol=None):
        result = self.futuresSession.my_position(symbol=symbol)
        return result['result']

    def getSymbolMinTrade(self, symbol, futures=False):
        symbolTickerPrice = self.getSymbolTickerPrice(symbol=symbol, futures=futures)

        minQuantity = None
        minQuoteQuantity = None
        stepQuantity = None
        stepPrice = None

        if futures:
            symbolInfos = self.futuresSession.query_symbol()['result']

            for symbolInfo in symbolInfos:
                if symbolInfo['name'] == symbol:
                    minQuantity = float(symbolInfo['lot_size_filter']['min_trading_qty'])
                    minQuoteQuantity = symbolTickerPrice * minQuantity
                    stepQuantity = float(symbolInfo['lot_size_filter']['qty_step'])
                    stepPrice = symbolInfo['price_filter']['tick_size']

        else:
            symbolInfos = self.spotSession.query_symbol()['result']

            for symbolInfo in symbolInfos:
                if symbolInfo['name'] == symbol:
                    minQuantity = float(symbolInfo['minTradeQuantity'])
                    minQuoteQuantity = float(symbolInfo['minTradeAmount'])
                    stepQuantity = float(symbolInfo['basePrecision'])
                    stepPrice = symbolInfo['minPricePrecision']

        return {'minQuantity': minQuantity, 'minQuoteQuantity': minQuoteQuantity,
                'precisionStep': stepQuantity, 'stepPrice': stepPrice}

    def makeSlTpLimitFuturesOrder(self, symbol, orderSide, quantity=None, quoteQuantity=None, enterPrice=None,
                                  takeProfit=None, stopLoss=None, leverage=None, marginType=None):
        if enterPrice is None or takeProfit is None or stopLoss is None or leverage is None or marginType is None:
            raise ValueError('Specify all inputs.')

        symbolInfo = self.getSymbolMinTrade(symbol=symbol, futures=True)

        quantity = DataHelpers.getQuantity(enterPrice, quantity, quoteQuantity, symbolInfo['precisionStep'])

        self.setMarginLeverage(leverage, marginType, symbol)
        orderParams = {
            'takeProfit': takeProfit,
            'stopLoss': stopLoss,
            'tpTriggerBy': 'MarkPrice',
            'slTriggerBy': 'MarkPrice'
        }

        futuresOrder = self.createAndTestFuturesOrder(symbol=symbol, side=orderSide, orderType='LIMIT',
                                                      timeInForce='GTC', quantity=quantity, price=enterPrice,
                                                      closePosition=False, extraParams=orderParams)
        orderingResult = self.makeFuturesOrder(futuresOrder)
        return orderingResult['orderId']

    def setMarginLeverage(self, leverage, marginType, symbol):
        params = {'buyLeverage': leverage, 'sellLeverage': leverage}
        self.changeInitialLeverage(leverage, symbol)
        self.changeMarginType(symbol, marginType, params)
