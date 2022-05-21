import json
import logging
import time

import pytest

from TradeGates.TradeGate import TradeGate

loglevel = logging.INFO
logging.basicConfig(level=loglevel)
log = logging.getLogger(__name__)


@pytest.fixture
def getGates():
    gates = []
    with open('./config.json') as f:
        config = json.load(f)

    for key in config.keys():
        gates.append(TradeGate(config[key], sandbox=True))

    return gates


def testSymbolFuturesOrders(getGates):
    for gate in getGates:
        symbolFutureOrders = gate.getSymbolOrders('BTCUSDT', futures=True)
        # print('\nSymbol future orders from {} exchange: {}'.format(gate.exchangeName, symbolFutureOrders))
        assert symbolFutureOrders is not None, 'Problem in futures order list from {} exchange.'.format(
            gate.exchangeName)


def testFuturesBalance(getGates):
    for gate in getGates:
        balance = gate.getBalance(futures=True)
        # print('\nFutures balance from {} exchange: {}'.format(gate.exchangeName, balance))
        assert balance is not None, 'Problem in futures balance from {} exchange.'.format(gate.exchangeName)

        try:
            if not gate.exchangeName == 'Binance':
                if not sorted(list(balance[0].keys())) == sorted(['asset', 'free', 'locked', 'exchangeSpecific']):
                    assert False, 'Bad fetch balance interface for {} exchange,'.format(gate.exchangeName)
            else:
                if not sorted(list(balance[0].keys())) == sorted(['asset', 'free', 'locked']):
                    assert False, 'Bad fetch balance interface for {} exchange,'.format(gate.exchangeName)
        except:
            assert False, 'Bad fetch single coin balance interface for {} exchange,'.format(gate.exchangeName)


def testFuturesSingleCoinBalance(getGates):
    for gate in getGates:
        balance = gate.getBalance('USDT', futures=True)
        # print('\nUSDT Futures balance from {} exchange: {}'.format(gate.exchangeName, balance))
        assert balance is not None, 'Problem in fetching futures single coin balance from {} exchange.'.format(
            gate.exchangeName)

        try:
            if not gate.exchangeName == 'Binance':
                if not sorted(list(balance.keys())) == sorted(['asset', 'free', 'locked', 'exchangeSpecific']):
                    assert False, 'Bad fetch balance interface for {} exchange,'.format(gate.exchangeName)
            else:
                if not sorted(list(balance.keys())) == sorted(['asset', 'free', 'locked']):
                    assert False, 'Bad fetch balance interface for {} exchange,'.format(gate.exchangeName)
        except:
            assert False, 'Bad fetch single coin balance interface for {} exchange,'.format(gate.exchangeName)


def testCreatingFuturesOrder(getGates):
    for gate in getGates:
        futuresOrderData = gate.createAndTestFuturesOrder('BTCUSDT', 'BUY', 'MARKET', quantity=0.002)
        # print('\nTest creating futures order in {} exchange: {}'.format(gate.exchangeName, futuresOrderData))
        assert futuresOrderData is not None, 'Problem in creating futures order in {} exchange.'.format(
            gate.exchangeName)


def testFuturesOrder(getGates):
    for gate in getGates:
        futuresOrderData = gate.createAndTestFuturesOrder('BTCUSDT', 'BUY', 'MARKET', quantity=0.002)
        result = gate.makeFuturesOrder(futuresOrderData)
        # print('\nFuture ordering in {} exchange: {}'.format(gate.exchangeName, result))
        assert result is not None, 'Problem in submiting futures order in {} exchange.'.format(gate.exchangeName)


def testBatchFuturesOrders(getGates):
    for gate in getGates:
        try:
            verifiedOrders = [gate.createAndTestFuturesOrder('BTCUSDT', 'BUY', 'MARKET', quantity=0.1),
                              gate.createAndTestFuturesOrder('BTCUSDT', 'BUY', 'MARKET', quantity=0.2),
                              gate.createAndTestFuturesOrder('BTCUSDT', 'BUY', 'MARKET', quantity=0.3)]

            result = gate.makeBatchFuturesOrder(verifiedOrders)
            # print('\nResult of batch ordering from {} exchange: {}'.format(gate.exchangeName, result))
            assert result is not None, 'Problem in making new order in {} exchange'.format(gate.exchangeName)
        except Exception:
            assert False, 'Problem in making new order in {} exchange'.format(gate.exchangeName)


# @pytest.mark.skip(reason="For Special Purposes")
def testFuturesTpSlLimitOrder(getGates):
    for gate in getGates:
        if gate.exchangeName.lower() != 'binance':
            continue
        try:
            result = gate.makeSlTpLimitFuturesOrder(symbol='ADAUSDT', orderSide='BUY', quantity=None, quoteQuantity=40,
                                                    enterPrice=1.1649, takeProfit=1.1473, stopLoss=1.1974,
                                                    leverage=10,
                                                    marginType='ISOLATED')
            # print('\nResult of TP-SL-Limit ordering from {} exchange: {}'.format(gate.exchangeName, result))
            assert result is not None, 'Problem in making new order in {} exchange'.format(gate.exchangeName)
        except Exception:
            assert False, 'Problem in making new SL-TP-Limit order in {} exchange'.format(gate.exchangeName)


def testFuturesTpSlMarketOrder(getGates):
    for gate in getGates:
        if gate.exchangeName.lower() != 'binance':
            continue
        try:
            result = gate.makeSlTpMarketFuturesOrder(symbol='BTCUSDT', orderSide='BUY', quantity=None, quoteQuantity=40,
                                                     takeProfit=47000, stopLoss=45000, leverage=10,
                                                     marginType='ISOLATED')
            print('\nResult of TP-SL-Market ordering from {} exchange: {}'.format(gate.exchangeName, result))
            assert result is not None, 'Problem in making new order in {} exchange'.format(gate.exchangeName)
        except Exception:
            assert False, 'Problem in making new SL-TP-Limit order in {} exchange'.format(gate.exchangeName)


def testGetFuturesOpenOrders(getGates):
    for gate in getGates:
        symbolOpenOrders = gate.getOpenOrders('BTCUSDT', futures=True)

        # print('\n\'BTCUSDT\' open orders from {} exchange: {}'.format(gate.exchangeName, symbolOpenOrders))

        assert symbolOpenOrders is not None, \
            'Problem in getting list of open orders with symbol from {} exchange.'.format(gate.exchangeName)


def testGetPositionInformation(getGates):
    for gate in getGates:
        openPosition = gate.getPositionInfo('BTCUSDT')

        # print('\nOpen position information from {} exchange: {}'.format(gate.exchangeName, openPosition))

        assert openPosition is not None, 'Problem in getting position information without symbol from {} exchange.'.format(
            gate.exchangeName)


def testGetFutureOrder(getGates):
    for gate in getGates:
        futuresOrderData = gate.createAndTestFuturesOrder('BTCUSDT', 'BUY', 'LIMIT', quantity=0.002, price=40000,
                                                          timeInForce='GTC', newClientOrderId=str(int(time.time())))
        result = gate.makeFuturesOrder(futuresOrderData)
        order = gate.getOrder('BTCUSDT', orderId=result['orderId'], futures=True)

        # print('\nOrder data fetched from {} exchange: {}'.format(gate.exchangeName, order))

        assert order['clientOrderId'] == result[
            'clientOrderId'], 'Futures fetch client orderID is not equal to the actual client orderID from {} exchange.'.format(
            gate.exchangeName)

        order = gate.getOrder('BTCUSDT', localOrderId=result['clientOrderId'], futures=True)
        assert order['orderId'] == result[
            'orderId'], 'Futures fetch orderID is not equal to the actual orderID from {} exchange.'.format(
            gate.exchangeName)


def testCancelingAllFuturesOpenOrders(getGates):
    for gate in getGates:
        futuresOrderData = gate.createAndTestFuturesOrder('BTCUSDT', 'BUY', 'LIMIT', price=35000, quantity=0.002,
                                                          timeInForce='GTC')
        gate.makeFuturesOrder(futuresOrderData)

        gate.cancelAllSymbolOpenOrders('BTCUSDT', futures=True)

        openOrders = gate.getOpenOrders('BTCUSDT', futures=True)
        assert len(openOrders) == 0, 'Problem in canceling all Open Orders in {} exchange.'.format(gate.exchangeName)


def testCancelingOrder(getGates):
    for gate in getGates:
        futuresOrderData = gate.createAndTestFuturesOrder('BTCUSDT', 'BUY', 'LIMIT', price=35000, quantity=0.002,
                                                          timeInForce='GTC', newClientOrderId=str(int(time.time())))
        result = gate.makeFuturesOrder(futuresOrderData)

        gate.cancelOrder(symbol='BTCUSDT', localOrderId=result['clientOrderId'], futures=True)

        result = gate.getOrder(symbol='BTCUSDT', localOrderId=result['clientOrderId'], futures=True)
        assert result['status'] in ['CANCELED', 'Cancelled'], \
            'Problem in canceling specified Open Orders from {} exchange.'.format(gate.exchangeName)


def testFuturesTradeHistory(getGates):
    for gate in getGates:
        if gate.exchangeName.lower() == 'kucoin':
            tradeHistory = gate.symbolAccountTradeHistory('XBTUSDTM', futures=True)
        else:
            tradeHistory = gate.symbolAccountTradeHistory('BTCUSDT', futures=True)
        # print('\nTrade history from {} exchange: {}'.format(gate.exchangeName, tradeHistory))

        assert tradeHistory is not None, 'Problem in fetching trade history from {} exchange.'.format(gate.exchangeName)

        interface = ['symbol', 'id', 'orderId', 'orderListId', 'price', 'qty', 'quoteQty', 'commission',
                     'commissionAsset', 'time',
                     'isBuyer', 'isMaker', 'isBestMatch']

        errorMessage = 'Bad fetch trade history interface for {} exchange,'.format(gate.exchangeName)
        try:
            if not gate.exchangeName == 'Binance':
                interface.append('exchangeSpecific')
                if not sorted(list(tradeHistory[0].keys())) == sorted(interface):
                    assert False, errorMessage
            else:
                if not sorted(list(tradeHistory[0].keys())) == sorted(interface):
                    assert False, errorMessage
        except Exception:
            assert False, errorMessage


def testFuturesSymbolList(getGates):
    for gate in getGates:
        if gate.exchangeName.lower() != 'binance':
            continue
        symbolList = gate.getSymbolList(futures=True)
        print(symbolList)

        assert symbolList != None
