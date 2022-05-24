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


def testNewTestOrder(getGates):
    for gate in getGates:
        try:
            res = gate.createAndTestSpotOrder('BTCUSDT', 'SELL', 'LIMIT', timeInForce='GTC', quantity=0.002,
                                              price=49500)
            assert res is not None, 'Problem in testing making order from {} exchange'.format(gate.exchangeName)
        except Exception as e:
            assert False, 'From {} exchange : {}'.format(gate.exchangeName, str(e))


def testNewTestOrderBadOrderType(getGates):
    for gate in getGates:
        try:
            res = gate.createAndTestSpotOrder('BTCUSDT', 'SELL', 'LINIT', timeInForce='GTC', quantity=0.002,
                                              price=49500)
            assert res is None, 'Bad order type and information provided. Must fail (Exchange: {})'.format(
                gate.exchangeName)
        except Exception:
            assert True, 'Bad order type and information provided. Must fail (Exchange: {})'.format(gate.exchangeName)


def testNewOrder(getGates):
    for gate in getGates:
        try:
            verifiedOrder = gate.createAndTestSpotOrder('BTCUSDT', 'BUY', 'LIMIT', quantity=0.002, price=35000,
                                                        timeInForce='GTC')
            result = gate.makeSpotOrder(verifiedOrder)
            assert result is not None, 'Problem in making new order in {} exchange'.format(gate.exchangeName)
        except Exception:
            assert False, 'Problem in making new order in {} exchange'.format(gate.exchangeName)


def testGetOrders(getGates):
    for gate in getGates:
        orders = gate.getSymbolOrders('BTCUSDT', futures=False)
        # print('\nGetting order history for BTCUSDT symbol from {}: {}'.format(gate.exchangeName, orders[0]))

        assert orders is not None, 'Problem in getting list of all orders from {} exchange.'.format(gate.exchangeName)


def testGetOpenOrders(getGates):
    for gate in getGates:
        symbolOpenOrders = gate.getOpenOrders('BTCUSDT')
        # print('\nGetting BTCUSDT open orders list from {} exchange: {}'.format(gate.exchangeName, symbolOpenOrders))
        assert symbolOpenOrders is not None, 'Problem in getting list of open orders with symbol from {} exchange.'.format(
            gate.exchangeName)


def testGetOrder(getGates):
    for gate in getGates:
        try:
            verifiedOrder = gate.createAndTestSpotOrder('BTCUSDT', 'BUY', 'LIMIT', quantity=0.02, price=34000,
                                                        timeInForce='GTC', newClientOrderId=str(int(time.time())))
            result = gate.makeSpotOrder(verifiedOrder)
        except Exception as e:
            assert False, 'Problem in making order from {} exchange: {}'.format(gate.exchangeName, str(e))

        # print('Submitted order on {} exchange: {}'.format(gate.exchangeName, result))

        order = gate.getOrder('BTCUSDT', orderId=result['orderId'])
        assert order['clientOrderId'] == result['clientOrderId'], \
            'Fetch client orderID is not equal to the actual client orderID from {} exchange.'.format(gate.exchangeName)
        # print('Correct \'clientOrderId\'.')

        order = gate.getOrder('BTCUSDT', localOrderId=result['clientOrderId'])
        assert order['orderId'] == result['orderId'], \
            'Fetch orderID is not equal to the actual orderID from {} exchange.'.format(gate.exchangeName)
        # print('Correct \'orderId\'.')

        gate.cancelOrder('BTCUSDT', orderId=result['orderId'])


def testCancelingAllOpenOrders(getGates):
    for gate in getGates:
        gate.cancelAllSymbolOpenOrders('BTCUSDT')

        openOrders = gate.getOpenOrders('BTCUSDT')
        assert len(openOrders) == 0, 'Problem in canceling all Open Orders in {} exchange.'.format(gate.exchangeName)


def testCancelingOrder(getGates):
    for gate in getGates:
        try:
            verifiedOrder = gate.createAndTestSpotOrder('BTCUSDT', 'BUY', 'LIMIT', quantity=0.002, price=35000,
                                                        timeInForce='GTC', newClientOrderId=str(int(time.time())))
            result = gate.makeSpotOrder(verifiedOrder)
        except Exception as e:
            assert False, 'Problem in making order in {} exchange: {}'.format(gate.exchangeName, str(e))

        result = gate.cancelOrder(symbol='BTCUSDT', orderId=result['orderId'])
        result = gate.getOrder(symbol='BTCUSDT', orderId=result['orderId'])

        assert result['status'] == 'CANCELED', 'Problem in canceling specified Open Orders in {} exchange.'.format(
            gate.exchangeName)

        try:
            verifiedOrder = gate.createAndTestSpotOrder('BTCUSDT', 'BUY', 'LIMIT', quantity=0.002, price=35000,
                                                        timeInForce='GTC', newClientOrderId=str(int(time.time())))
            result = gate.makeSpotOrder(verifiedOrder)
        except Exception as e:
            assert False, 'Problem in making order in {} exchange: {}'.format(gate.exchangeName, str(e))

        result = gate.cancelOrder(symbol='BTCUSDT', localOrderId=result['clientOrderId'])
        result = gate.getOrder(symbol='BTCUSDT', orderId=result['orderId'])

        assert result['status'] == 'CANCELED', 'Problem in canceling specified Open Orders in {} exchange.'.format(
            gate.exchangeName)
