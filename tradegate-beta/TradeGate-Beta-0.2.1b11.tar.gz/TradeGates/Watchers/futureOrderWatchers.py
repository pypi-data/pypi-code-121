import time


def watchFuturesLimitTrigger(gate, symbol, orderId, doPutTpSl, cancelIfNotOpened, params):
    if doPutTpSl:
        if 'tpSlOrderSide' not in params.keys() or 'stopLoss' not in params.keys() or 'takeProfit' not in params.keys():
            raise ValueError('Must specify \'tpSlOrderSide\' and \'stopLoss\' and \'takeProfit\'')

    if cancelIfNotOpened:
        if 'cancelDelaySec' not in params.keys():
            raise ValueError('Must specify \'cancelDelaySec\'')
        delayTimeSec = float(params['cancelDelaySec'])
        startDelayTime = time.time()

    print('Watching order')
    while True:
        time.sleep(0.1)
        order = gate.getOrder(symbol=symbol, orderId=orderId, futures=True)

        if cancelIfNotOpened:
            if time.time() - startDelayTime > delayTimeSec:
                gate.cancelOrder(symbol=symbol, orderId=orderId, futures=True)
                break

        if order['status'] == 'NEW':
            continue
        elif order['status'] == 'FILLED':
            if doPutTpSl:
                orderSide = params['tpSlOrderSide']
                stopLoss = params['stopLoss']
                takeProfit = params['takeProfit']

                stopLossOrder = gate.createAndTestFuturesOrder(symbol, orderSide, 'STOP_MARKET',
                                                               stopPrice=str(stopLoss), closePosition=True,
                                                               priceProtect=True, workingType='MARK_PRICE',
                                                               timeInForce='GTC')

                takeProfitOrder = gate.createAndTestFuturesOrder(symbol, orderSide, 'TAKE_PROFIT_MARKET',
                                                                 stopPrice=str(takeProfit), closePosition=True,
                                                                 priceProtect=True, workingType='MARK_PRICE',
                                                                 timeInForce='GTC')
                result = gate.makeBatchFuturesOrder([stopLossOrder, takeProfitOrder])
                # print(result)
                break
        elif order['status'] == 'CANCELED':
            break

    print('Watching position')
    while True:
        time.sleep(0.1)
        position = gate.getPositionInfo(symbol)[0]

        if float(position['entryPrice']) == 0.0:
            gate.cancelAllSymbolOpenOrders(symbol, futures=True)
            break

# if __name__ == '__main__':
#     print(sys.argv)
#     time.sleep(3)
#     with open('helloWorld.txt')
